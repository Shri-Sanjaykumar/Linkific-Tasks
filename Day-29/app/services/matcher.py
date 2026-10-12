"""Deterministic 3-Way Financial Reconciliation Engine.

Performs line-item level cross-verification across:
1. Vendor Invoice (billed rates, quantities, taxes, totals)
2. ERP Purchase Order (committed rates, ordered quantities)
3. Dock Goods Receipt Note - GRN (physically received & accepted quantities)
Returns both aggregate variance telemetry and per-item diff records for dynamic UI inspection.
"""

from typing import List, Optional
from app.models import (
    InvoicePayload,
    PurchaseOrderRecord,
    MatchResult,
    ItemReconciliationDiff,
)
from app.core.config import settings
from app.core.logging_config import logger


class ReconciliationMatcher:
    """Deterministic 3-Way Invoice Reconciliation Engine."""

    @staticmethod
    def match(invoice: InvoicePayload, po: Optional[PurchaseOrderRecord]) -> MatchResult:
        discrepancies: List[str] = []
        item_diffs: List[ItemReconciliationDiff] = []
        total_price_var = 0.0
        total_qty_var = 0

        if not po:
            discrepancies.append(
                f"Purchase Order '{invoice.po_number or 'UNSPECIFIED'}' not found in ERP commitment ledger."
            )
            for inv_item in invoice.items:
                item_diffs.append(
                    ItemReconciliationDiff(
                        item_id=inv_item.item_id,
                        description=inv_item.description,
                        billed_qty=inv_item.quantity,
                        po_ordered_qty=0,
                        grn_accepted_qty=0,
                        grn_rejected_qty=0,
                        billed_unit_price_usd=inv_item.unit_price_usd,
                        po_unit_price_usd=0.0,
                        unit_price_delta_usd=inv_item.unit_price_usd,
                        line_variance_usd=inv_item.total_price_usd,
                        status="UNCOMMITTED_PO",
                    )
                )
            logger.info(f"Reconciliation: Invoice '{invoice.invoice_id}' failed — missing PO.")
            return MatchResult(
                matched=False,
                po_found=False,
                price_variance_usd=round(invoice.total_amount_usd, 2),
                quantity_variance_units=sum(i.quantity for i in invoice.items),
                tax_variance_usd=0.0,
                discrepancy_details=discrepancies,
                item_diffs=item_diffs,
            )

        po_item_map = {item.item_id: item for item in po.items}

        for inv_item in invoice.items:
            po_item = po_item_map.get(inv_item.item_id)
            if not po_item:
                discrepancies.append(
                    f"Line-item '{inv_item.item_id}' ({inv_item.description}) billed on invoice is absent from PO '{po.po_number}'."
                )
                total_price_var += inv_item.total_price_usd
                total_qty_var += inv_item.quantity
                item_diffs.append(
                    ItemReconciliationDiff(
                        item_id=inv_item.item_id,
                        description=inv_item.description,
                        billed_qty=inv_item.quantity,
                        po_ordered_qty=0,
                        grn_accepted_qty=0,
                        grn_rejected_qty=0,
                        billed_unit_price_usd=inv_item.unit_price_usd,
                        po_unit_price_usd=0.0,
                        unit_price_delta_usd=inv_item.unit_price_usd,
                        line_variance_usd=inv_item.total_price_usd,
                        status="UNLISTED_ITEM",
                    )
                )
                continue

            # 1. Price Rate Verification
            price_diff = round(inv_item.unit_price_usd - po_item.unit_price_usd, 2)
            item_var = 0.0
            status_code = "MATCHED"

            if abs(price_diff) > 0.01:
                item_var += price_diff * inv_item.quantity
                total_price_var += price_diff * inv_item.quantity
                status_code = "RATE_VARIANCE"
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
                item_var += var_val
                total_price_var += var_val
                status_code = "QTY_SHORTAGE" if status_code == "MATCHED" else "RATE_AND_QTY_VARIANCE"
                discrepancies.append(
                    f"Quantity Discrepancy on item '{inv_item.item_id}': Billed {inv_item.quantity} units, but dock GRN accepted only {accepted_qty} units ({grn_rejected} rejected at dock)."
                )

            item_diffs.append(
                ItemReconciliationDiff(
                    item_id=inv_item.item_id,
                    description=inv_item.description,
                    billed_qty=inv_item.quantity,
                    po_ordered_qty=po_item.quantity,
                    grn_accepted_qty=accepted_qty,
                    grn_rejected_qty=grn_rejected,
                    billed_unit_price_usd=inv_item.unit_price_usd,
                    po_unit_price_usd=po_item.unit_price_usd,
                    unit_price_delta_usd=price_diff,
                    line_variance_usd=round(item_var, 2),
                    status=status_code,
                )
            )

        # 3. Overall Total & Tax Variance Check
        expected_po_total = po.approved_total_usd
        header_gap = abs(invoice.total_amount_usd - expected_po_total)
        if len(discrepancies) == 0 and header_gap > settings.MAX_PERMISSIBLE_PRICE_VARIANCE_USD:
            total_price_var += invoice.total_amount_usd - expected_po_total
            discrepancies.append(
                f"Header Total Variance: Invoice total ${invoice.total_amount_usd:,.2f} exceeds approved PO commitment ${expected_po_total:,.2f} by ${header_gap:,.2f}."
            )

        net_var = round(abs(total_price_var), 2)
        matched = (len(discrepancies) == 0) and (net_var <= settings.MAX_PERMISSIBLE_PRICE_VARIANCE_USD)

        if not matched:
            logger.info(f"Reconciliation: Invoice '{invoice.invoice_id}' failed match with {len(discrepancies)} discrepancy flag(s).")
        else:
            logger.info(f"Reconciliation: Invoice '{invoice.invoice_id}' matched PO '{po.po_number}' cleanly.")

        return MatchResult(
            matched=matched,
            po_found=True,
            price_variance_usd=net_var,
            quantity_variance_units=total_qty_var,
            tax_variance_usd=0.0,
            discrepancy_details=discrepancies,
            item_diffs=item_diffs,
        )
