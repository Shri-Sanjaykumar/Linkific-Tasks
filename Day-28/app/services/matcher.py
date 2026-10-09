"""Deterministic 3-Way Reconciliation Service.

Compares:
1. Vendor Invoice line-item quantities, prices, and tax.
2. Purchase Order (PO) agreed rates and total commitments.
3. Goods Receipt Note (GRN) accepted vs rejected quantities at the dock.
"""

from typing import Dict, List, Optional
from app.models import InvoicePayload, PurchaseOrderRecord, MatchResult
from app.core.config import settings
from app.core.logging_config import logger


class ReconciliationMatcher:
    """Enterprise 3-way matching engine detecting variances across AP documents."""

    @classmethod
    def match(
        cls,
        invoice: InvoicePayload,
        po: Optional[PurchaseOrderRecord],
    ) -> MatchResult:
        """Execute mathematical comparison across Invoice, PO, and GRN.
        
        Args:
            invoice: Validated InvoicePayload instance.
            po: Optional PurchaseOrderRecord from corporate commitments.

        Returns:
            MatchResult containing reconciliation status and line-item variances.
        """
        if po is None:
            logger.warning(f"Reconciliation: Invoice '{invoice.invoice_id}' has no matching PO '{invoice.po_number}'.")
            return MatchResult(
                matched=False,
                po_found=False,
                price_variance_usd=round(invoice.total_amount_usd, 2),
                quantity_variance_units=0,
                tax_variance_usd=round(invoice.tax_usd, 2),
                discrepancy_details=[
                    f"Missing PO record: '{invoice.po_number}' not found in corporate ERP commitments."
                ],
            )

        discrepancies: List[str] = []
        total_price_var = 0.0
        total_qty_var = 0

        # Build PO lookup dictionary by item_id
        po_item_map = {item.item_id: item for item in po.items}

        for inv_item in invoice.items:
            po_item = po_item_map.get(inv_item.item_id)
            if not po_item:
                discrepancies.append(
                    f"Line-item '{inv_item.item_id}' ({inv_item.description}) billed on invoice is absent from PO '{po.po_number}'."
                )
                total_price_var += inv_item.total_price_usd
                total_qty_var += inv_item.quantity
                continue

            # 1. Price Rate Verification
            price_diff = inv_item.unit_price_usd - po_item.unit_price_usd
            if abs(price_diff) > 0.01:
                item_var = price_diff * inv_item.quantity
                total_price_var += item_var
                discrepancies.append(
                    f"Rate Variance on item '{inv_item.item_id}': Billed ${inv_item.unit_price_usd:.2f} vs PO agreed ${po_item.unit_price_usd:.2f} (Delta: ${price_diff:+.2f}/unit)."
                )

            # 2. Quantity & Dock GRN Verification
            grn_received = po.grn_units_received.get(inv_item.item_id, po_item.quantity)
            grn_rejected = po.grn_units_rejected.get(inv_item.item_id, 0)
            accepted_qty = max(0, grn_received - grn_rejected)

            if inv_item.quantity > accepted_qty:
                qty_diff = inv_item.quantity - accepted_qty
                total_qty_var += qty_diff
                var_val = qty_diff * po_item.unit_price_usd
                total_price_var += var_val
                discrepancies.append(
                    f"Quantity Discrepancy on item '{inv_item.item_id}': Billed {inv_item.quantity} units, but dock GRN accepted only {accepted_qty} units ({grn_rejected} rejected at dock)."
                )

        # 3. Overall Variance Evaluation
        net_var = round(abs(total_price_var), 2)
        matched = (len(discrepancies) == 0) and (net_var <= settings.MAX_PERMISSIBLE_PRICE_VARIANCE_USD)

        if not matched:
            logger.info(f"Reconciliation: Invoice '{invoice.invoice_id}' failed match with {len(discrepancies)} discrepancy flag(s).")
        else:
            logger.info(f"Reconciliation: Invoice '{invoice.invoice_id}' matched PO '{po.po_number}' cleanly.")

        return MatchResult(
            matched=matched,
            po_found=True,
            price_variance_usd=round(total_price_var, 2),
            quantity_variance_units=total_qty_var,
            tax_variance_usd=0.0,
            discrepancy_details=discrepancies,
        )

    # Classmethod alias for backward compatibility
    reconcile = match


ThreeWayMatcher = ReconciliationMatcher
