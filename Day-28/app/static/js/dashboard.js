/**
 * FinDoc-AuditEngine Dynamic Enterprise Workbench Controller.
 * Supports arbitrary custom multi-line invoices, live PO/GRN editing,
 * unstructured text PII scrubbing, random realistic scenario synthesis,
 * and perturbation-based ML explainability.
 */

const FX_RATE = 86.50;
let benchmarkPresets = [];
let activeLedger = [];
let currentFilter = 'ALL';
let manualTotalOverride = false;

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize with 1 editable default row
  setEditableLineItems([
    {
      item_id: 'ITEM-1',
      description: 'Ergonomic Mechanical Keyboards',
      unit_price_usd: 40.00,
      po_unit_price_usd: 40.00,
      quantity: 10,
      grn_received: 10,
      grn_rejected: 0,
    }
  ]);
  await loadPresets();
  await refreshMetrics();
  await refreshLedger();
  setupFilterChips();
  setupSearch();
});

// -------------------------------------------------------------
// 1. Dynamic Editable Line-Item Management
// -------------------------------------------------------------

function setEditableLineItems(rows) {
  const tbody = document.getElementById('itemsTableBody');
  tbody.innerHTML = '';
  rows.forEach((r) => appendLineItemRowDOM(r));
  manualTotalOverride = false;
  recalculateDynamicTotals();
}

function appendLineItemRowDOM(row) {
  const tbody = document.getElementById('itemsTableBody');
  const tr = document.createElement('tr');
  tr.className = 'editable-item-row';
  tr.innerHTML = `
    <td><input type="text" class="table-input mono item-id" value="${row.item_id || 'SKU-01'}" required></td>
    <td><input type="text" class="table-input item-desc" value="${row.description || 'Enterprise Hardware / Service'}" required></td>
    <td><input type="number" step="0.01" min="0" class="table-input mono item-inv-price" value="${Number(row.unit_price_usd ?? 100).toFixed(2)}" oninput="onLineItemEdited()"></td>
    <td><input type="number" step="0.01" min="0" class="table-input mono item-po-price" value="${Number(row.po_unit_price_usd ?? row.unit_price_usd ?? 100).toFixed(2)}" oninput="onLineItemEdited()"></td>
    <td><input type="number" step="1" min="1" class="table-input mono item-qty" value="${Number(row.quantity ?? 1)}" oninput="onLineItemEdited()"></td>
    <td><input type="number" step="1" min="0" class="table-input mono item-grn-rec" value="${Number(row.grn_received ?? row.quantity ?? 1)}" oninput="onLineItemEdited()"></td>
    <td><input type="number" step="1" min="0" class="table-input mono item-grn-rej" value="${Number(row.grn_rejected ?? 0)}" oninput="onLineItemEdited()"></td>
    <td style="text-align:center;">
      <button type="button" class="btn-remove-row" title="Remove Line Item" onclick="removeLineItemRow(this)">&times;</button>
    </td>
  `;
  tbody.appendChild(tr);
}

function addLineItemRow() {
  const idx = document.querySelectorAll('#itemsTableBody tr').length + 1;
  appendLineItemRowDOM({
    item_id: `ITEM-${idx}`,
    description: `Operational Line Item #${idx}`,
    unit_price_usd: 250.00,
    po_unit_price_usd: 250.00,
    quantity: 2,
    grn_received: 2,
    grn_rejected: 0,
  });
  manualTotalOverride = false;
  recalculateDynamicTotals();
}

function removeLineItemRow(btn) {
  const tbody = document.getElementById('itemsTableBody');
  if (tbody.querySelectorAll('tr').length <= 1) {
    return; // Keep at least 1 row
  }
  btn.closest('tr').remove();
  manualTotalOverride = false;
  recalculateDynamicTotals();
}

function onLineItemEdited() {
  manualTotalOverride = false;
  recalculateDynamicTotals();
}

function onManualTotalChange() {
  manualTotalOverride = true;
  recalculateDynamicTotals(true);
}

function collectLineItemsFromDOM() {
  const rows = document.querySelectorAll('#itemsTableBody tr.editable-item-row');
  const invItems = [];
  const poItems = [];
  const grnReceived = {};
  const grnRejected = {};

  rows.forEach((tr, i) => {
    const itemId = (tr.querySelector('.item-id')?.value || `ITEM-${i + 1}`).trim();
    const desc = (tr.querySelector('.item-desc')?.value || 'Line Item').trim();
    const invPrice = parseFloat(tr.querySelector('.item-inv-price')?.value) || 0.0;
    const poPrice = parseFloat(tr.querySelector('.item-po-price')?.value) || 0.0;
    const qty = Math.max(1, parseInt(tr.querySelector('.item-qty')?.value, 10) || 1);
    const grnRec = Math.max(0, parseInt(tr.querySelector('.item-grn-rec')?.value, 10) || 0);
    const grnRej = Math.max(0, parseInt(tr.querySelector('.item-grn-rej')?.value, 10) || 0);

    invItems.push({
      item_id: itemId,
      description: desc,
      quantity: qty,
      unit_price_usd: Number(invPrice.toFixed(2)),
      total_price_usd: Number((invPrice * qty).toFixed(2)),
    });

    poItems.push({
      item_id: itemId,
      description: desc,
      quantity: qty,
      unit_price_usd: Number(poPrice.toFixed(2)),
      total_price_usd: Number((poPrice * qty).toFixed(2)),
    });

    grnReceived[itemId] = grnRec;
    grnRejected[itemId] = grnRej;
  });

  return { invItems, poItems, grnReceived, grnRejected };
}

function recalculateDynamicTotals(preserveTotalInput = false) {
  const { invItems, poItems, grnReceived, grnRejected } = collectLineItemsFromDOM();
  const taxUsd = parseFloat(document.getElementById('inputTaxUsd')?.value) || 0.0;
  const hasPo = document.getElementById('inputHasPo')?.checked ?? true;

  const invSubtotal = invItems.reduce((acc, it) => acc + it.total_price_usd, 0.0);
  const poSubtotal = poItems.reduce((acc, it) => acc + it.total_price_usd, 0.0);

  let computedTotal = invSubtotal + taxUsd;
  const amountInput = document.getElementById('inputAmount');
  if (!preserveTotalInput && !manualTotalOverride && amountInput) {
    amountInput.value = computedTotal.toFixed(2);
  } else if (amountInput) {
    computedTotal = parseFloat(amountInput.value) || computedTotal;
  }

  // Projected variances
  let rateVar = 0.0;
  let qtyShortage = 0;

  if (!hasPo) {
    rateVar = computedTotal;
    qtyShortage = invItems.reduce((acc, it) => acc + it.quantity, 0);
  } else {
    invItems.forEach((invIt, idx) => {
      const poIt = poItems[idx];
      const diff = invIt.unit_price_usd - poIt.unit_price_usd;
      if (Math.abs(diff) > 0.01) {
        rateVar += diff * invIt.quantity;
      }
      const accepted = Math.max(0, (grnReceived[invIt.item_id] ?? invIt.quantity) - (grnRejected[invIt.item_id] ?? 0));
      if (invIt.quantity > accepted) {
        const missing = invIt.quantity - accepted;
        qtyShortage += missing;
        rateVar += missing * poIt.unit_price_usd;
      }
    });
  }

  document.getElementById('previewSubtotal').innerText = `$${invSubtotal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.getElementById('previewInrTotal').innerText = `INR ${(computedTotal * FX_RATE).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const rateEl = document.getElementById('previewRateVar');
  rateEl.innerText = `$${Math.abs(rateVar).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  rateEl.style.color = Math.abs(rateVar) > 1.0 ? 'var(--status-blocked-fg)' : 'var(--status-approved-fg)';

  const qtyEl = document.getElementById('previewQtyVar');
  qtyEl.innerText = `${qtyShortage} units`;
  qtyEl.style.color = qtyShortage > 0 ? 'var(--status-blocked-fg)' : 'var(--status-approved-fg)';

  return { invSubtotal, poSubtotal, computedTotal, taxUsd };
}

// -------------------------------------------------------------
// 2. Data Fetching: Presets, Metrics, Ledger
// -------------------------------------------------------------

async function loadPresets() {
  try {
    const res = await fetch('/api/v1/audit/presets');
    if (res.ok) {
      benchmarkPresets = await res.json();
      const select = document.getElementById('presetSelect');
      if (select && benchmarkPresets.length > 0) {
        select.innerHTML = '<option value="">-- Custom Dynamic Entry (Or Select Reference Case) --</option>';
        benchmarkPresets.forEach((item, idx) => {
          const inv = item.invoice;
          select.innerHTML += `<option value="${idx}">[${inv.invoice_id}] ${inv.vendor_name} — $${inv.total_amount_usd.toLocaleString()} (${item.expected_tier})</option>`;
        });
      }
    }
  } catch (err) {
    console.error('Failed to load presets:', err);
  }
}

async function refreshMetrics() {
  try {
    const res = await fetch('/api/v1/audit/summary');
    if (res.ok) {
      const data = await res.json();
      document.getElementById('metricTotalAudits').innerText = data.total_invoices_audited;
      document.getElementById('metricDisbursedUSD').innerText = `$${Number(data.total_disbursed_usd).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      document.getElementById('metricDisbursedINR').innerText = `INR ${Number(data.total_disbursed_inr).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      document.getElementById('metricStpRate').innerText = `${data.stp_rate_percentage}%`;
      document.getElementById('metricBlockedCount').innerText = data.blocked_invoices_count;
    }
  } catch (err) {
    console.error('Failed to fetch summary metrics:', err);
  }
}

async function refreshLedger() {
  try {
    let url = '/api/v1/audit/ledger';
    if (currentFilter !== 'ALL') {
      url += `?tier=${encodeURIComponent(currentFilter)}`;
    }
    const res = await fetch(url);
    if (res.ok) {
      activeLedger = await res.json();
      renderLedgerTable(activeLedger);
    }
  } catch (err) {
    console.error('Failed to fetch ledger:', err);
  }
}

// -------------------------------------------------------------
// 3. Preset Selection, Blank Reset & Random Scenario Generator
// -------------------------------------------------------------

function onPresetSelected() {
  const select = document.getElementById('presetSelect');
  const idx = select.value;
  if (idx === '' || !benchmarkPresets[idx]) return;

  const { invoice, po } = benchmarkPresets[idx];
  document.getElementById('inputInvoiceId').value = invoice.invoice_id;
  document.getElementById('inputVendorName').value = invoice.vendor_name;
  document.getElementById('inputPoNumber').value = invoice.po_number || '';
  document.getElementById('inputInvoiceDate').value = invoice.invoice_date || '2026-10-01';
  document.getElementById('inputDueDate').value = invoice.due_date || '2026-10-31';
  document.getElementById('inputTaxUsd').value = Number(invoice.tax_usd || 0).toFixed(2);
  document.getElementById('inputAmount').value = Number(invoice.total_amount_usd).toFixed(2);
  document.getElementById('inputCountry').value = invoice.vendor_country || 'IN';
  document.getElementById('inputEmail').value = invoice.vendor_contact_email || '';
  document.getElementById('inputPan').value = invoice.vendor_pan || '';
  document.getElementById('inputBankAccount').value = invoice.vendor_bank_account || '';
  document.getElementById('inputIsNew').checked = Boolean(invoice.is_new_vendor);
  document.getElementById('inputHasPo').checked = Boolean(po);

  const editableRows = (invoice.items || []).map((item) => {
    const poItem = (po && po.items ? po.items.find((p) => p.item_id === item.item_id) : null) || item;
    const grnRec = (po && po.grn_units_received && po.grn_units_received[item.item_id] !== undefined)
      ? po.grn_units_received[item.item_id]
      : poItem.quantity;
    const grnRej = (po && po.grn_units_rejected && po.grn_units_rejected[item.item_id] !== undefined)
      ? po.grn_units_rejected[item.item_id]
      : 0;

    return {
      item_id: item.item_id,
      description: item.description,
      unit_price_usd: item.unit_price_usd,
      po_unit_price_usd: poItem.unit_price_usd,
      quantity: item.quantity,
      grn_received: grnRec,
      grn_rejected: grnRej,
    };
  });

  setEditableLineItems(editableRows);
}

function resetBlankInvoice() {
  document.getElementById('presetSelect').value = '';
  const randNum = Math.floor(2000 + Math.random() * 7999);
  document.getElementById('inputInvoiceId').value = `INV-${randNum}`;
  document.getElementById('inputVendorName').value = 'Custom Enterprise Supplier Ltd';
  document.getElementById('inputPoNumber').value = `PO-${randNum}`;
  document.getElementById('inputInvoiceDate').value = '2026-10-09';
  document.getElementById('inputDueDate').value = '2026-11-08';
  document.getElementById('inputTaxUsd').value = '0.00';
  document.getElementById('inputCountry').value = 'IN';
  document.getElementById('inputEmail').value = 'billing@supplier.in';
  document.getElementById('inputPan').value = 'ABCDE1234F';
  document.getElementById('inputBankAccount').value = '';
  document.getElementById('inputHasPo').checked = true;
  document.getElementById('inputIsNew').checked = false;

  setEditableLineItems([
    {
      item_id: 'SKU-100',
      description: 'Custom Enterprise Software / Hardware Unit',
      unit_price_usd: 350.00,
      po_unit_price_usd: 350.00,
      quantity: 2,
      grn_received: 2,
      grn_rejected: 0,
    }
  ]);
}

function generateRandomScenario() {
  document.getElementById('presetSelect').value = '';
  const profiles = [
    {
      vendor: 'Tata Communications Enterprise',
      country: 'IN',
      isNew: false,
      hasPo: true,
      tax: 45.0,
      items: [
        { item_id: 'NET-FIB', description: 'Dedicated MPLS Leased Line', unit_price_usd: 280.0, po_unit_price_usd: 280.0, quantity: 2, grn_received: 2, grn_rejected: 0 }
      ]
    },
    {
      vendor: 'Snowflake Cloud Analytics Inc',
      country: 'US',
      isNew: false,
      hasPo: true,
      tax: 240.0,
      items: [
        { item_id: 'DB-CRED', description: 'Enterprise Warehouse Compute Credits', unit_price_usd: 1200.0, po_unit_price_usd: 1200.0, quantity: 4, grn_received: 4, grn_rejected: 0 }
      ]
    },
    {
      vendor: 'Precision Server Logistics GmbH',
      country: 'DE',
      isNew: false,
      hasPo: true,
      tax: 150.0,
      items: [
        { item_id: 'SRV-SSD', description: 'NVMe Datacenter Drives (Dock Shortage)', unit_price_usd: 300.0, po_unit_price_usd: 300.0, quantity: 10, grn_received: 10, grn_rejected: 3 }
      ]
    },
    {
      vendor: 'panama-shell-advisors',
      country: 'PA',
      isNew: true,
      hasPo: true,
      tax: 0.0,
      items: [
        { item_id: 'ADV-FEE', description: 'Unscheduled Offshore Retainer', unit_price_usd: 38000.0, po_unit_price_usd: 38000.0, quantity: 1, grn_received: 1, grn_rejected: 0 }
      ]
    },
    {
      vendor: 'Apex Rack Integration Corp',
      country: 'GB',
      isNew: false,
      hasPo: true,
      tax: 800.0,
      items: [
        { item_id: 'RACK-42U', description: '42U Colocation Enclosure Cabinets', unit_price_usd: 4500.0, po_unit_price_usd: 4500.0, quantity: 4, grn_received: 4, grn_rejected: 0 }
      ]
    }
  ];

  const pick = profiles[Math.floor(Math.random() * profiles.length)];
  const randId = Math.floor(3000 + Math.random() * 6000);

  document.getElementById('inputInvoiceId').value = `INV-${randId}`;
  document.getElementById('inputVendorName').value = pick.vendor;
  document.getElementById('inputPoNumber').value = `PO-${randId}`;
  document.getElementById('inputCountry').value = pick.country;
  document.getElementById('inputIsNew').checked = pick.isNew;
  document.getElementById('inputHasPo').checked = pick.hasPo;
  document.getElementById('inputTaxUsd').value = pick.tax.toFixed(2);
  document.getElementById('inputEmail').value = `ap@${pick.vendor.toLowerCase().replace(/[^a-z0-9]/g, '')}.com`;
  document.getElementById('inputPan').value = 'ABCDE9876K';

  setEditableLineItems(pick.items);
}

// -------------------------------------------------------------
// 4. Unstructured Raw Text Parser & PII Scrubber
// -------------------------------------------------------------

function toggleRawParser() {
  const drawer = document.getElementById('rawParserDrawer');
  drawer.classList.toggle('open');
}

async function parseRawInvoiceText() {
  const rawText = document.getElementById('rawDocumentInput').value.trim();
  if (!rawText) return;

  try {
    const res = await fetch('/api/v1/audit/parse-raw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw_text: rawText }),
    });
    if (res.ok) {
      const data = await res.json();
      const f = data.extracted_fields;
      document.getElementById('inputInvoiceId').value = f.invoice_id;
      document.getElementById('inputPoNumber').value = f.po_number;
      document.getElementById('inputVendorName').value = f.vendor_name;
      document.getElementById('inputCountry').value = f.vendor_country;
      document.getElementById('inputEmail').value = f.vendor_contact_email || '';
      document.getElementById('inputPan').value = f.vendor_pan || '';
      document.getElementById('inputTaxUsd').value = '0.00';

      setEditableLineItems([
        {
          item_id: 'ITEM-EXTRACTED',
          description: 'Extracted Document Line Item',
          unit_price_usd: f.total_amount_usd,
          po_unit_price_usd: f.total_amount_usd,
          quantity: 1,
          grn_received: 1,
          grn_rejected: 0,
        }
      ]);

      document.getElementById('rawScrubPreview').innerText =
        `Scrubbed ${data.pii_redactions_count} PII token(s): ${data.sanitized_text.substring(0, 95)}...`;
    }
  } catch (err) {
    console.error('Failed to parse raw text:', err);
  }
}

// -------------------------------------------------------------
// 5. Live Dynamic Audit Execution (POST /api/v1/audit/process)
// -------------------------------------------------------------

async function executeAudit(event) {
  if (event) event.preventDefault();

  const btn = document.getElementById('btnSubmitAudit');
  btn.disabled = true;
  btn.innerText = 'Executing 3-Way Match & Isolation Forest Scoring...';

  const { invItems, poItems, grnReceived, grnRejected } = collectLineItemsFromDOM();
  const { invSubtotal, poSubtotal, computedTotal, taxUsd } = recalculateDynamicTotals(true);

  const invoiceId = document.getElementById('inputInvoiceId').value.trim() || 'INV-CUSTOM-01';
  const vendorName = document.getElementById('inputVendorName').value.trim() || 'Enterprise Vendor';
  const poNumber = document.getElementById('inputPoNumber').value.trim() || 'PO-CUSTOM-01';
  const invoiceDate = document.getElementById('inputInvoiceDate').value || '2026-10-01';
  const dueDate = document.getElementById('inputDueDate').value || '2026-10-31';
  const country = document.getElementById('inputCountry').value.trim().toUpperCase() || 'IN';
  const email = document.getElementById('inputEmail').value.trim();
  const pan = document.getElementById('inputPan').value.trim();
  const bankAcc = document.getElementById('inputBankAccount').value.trim();
  const isNew = document.getElementById('inputIsNew').checked;
  const hasPo = document.getElementById('inputHasPo').checked;

  const payload = {
    invoice: {
      invoice_id: invoiceId,
      vendor_id: 'VEND-DYNAMIC',
      vendor_name: vendorName,
      po_number: poNumber,
      invoice_date: invoiceDate,
      due_date: dueDate,
      subtotal_usd: Number(invSubtotal.toFixed(2)),
      tax_usd: Number(taxUsd.toFixed(2)),
      total_amount_usd: Number(computedTotal.toFixed(2)),
      currency: 'USD',
      items: invItems,
      vendor_country: country,
      is_new_vendor: isNew,
      vendor_contact_email: email || null,
      vendor_pan: pan || null,
      vendor_bank_account: bankAcc || null,
    },
    purchase_order: hasPo
      ? {
          po_number: poNumber,
          vendor_id: 'VEND-DYNAMIC',
          vendor_name: vendorName,
          approved_total_usd: Number((poSubtotal + taxUsd).toFixed(2)),
          items: poItems,
          grn_units_received: grnReceived,
          grn_units_rejected: grnRejected,
        }
      : null,
  };

  try {
    const res = await fetch('/api/v1/audit/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`Audit error: ${err.detail || err.message || 'Invalid request payload'}`);
      return;
    }

    const decision = await res.json();
    renderInspectionResult(decision);
    await refreshMetrics();
    await refreshLedger();
  } catch (err) {
    console.error('Audit execution error:', err);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Execute 3-Way Reconciliation & Isolation Forest Audit';
  }
}

async function runFullDemoBatch() {
  const btn = document.getElementById('btnBatchDemo');
  btn.disabled = true;
  btn.innerText = 'Running Batch...';
  try {
    const res = await fetch('/api/v1/audit/demo-batch', { method: 'POST' });
    if (res.ok) {
      const decisions = await res.json();
      if (decisions.length > 0) {
        renderInspectionResult(decisions[decisions.length - 1]);
      }
      await refreshMetrics();
      await refreshLedger();
    }
  } catch (err) {
    console.error('Batch execution failed:', err);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Run 5-Scenario Batch';
  }
}

async function clearLedgerHistory() {
  await fetch('/api/v1/audit/ledger/clear', { method: 'DELETE' });
  await refreshMetrics();
  await refreshLedger();
}

// -------------------------------------------------------------
// 6. Render Determination Certificate, Item Diffs & XAI Bars
// -------------------------------------------------------------

function renderInspectionResult(d) {
  document.getElementById('emptyStatePanel').style.display = 'none';
  const resultCard = document.getElementById('inspectionResultCard');
  resultCard.style.display = 'block';

  document.getElementById('badgeAuditId').innerText = d.audit_id;

  let tierClass = 'tier-BLOCKED';
  let tagClass = 'tag-BLOCKED';
  let tierLabel = d.approval_tier;

  if (d.approval_tier === 'TIER_1_STP_AUTO_APPROVED') {
    tierClass = 'tier-STP';
    tagClass = 'tag-STP';
    tierLabel = 'Tier 1: Straight-Through Processing (STP)';
  } else if (d.approval_tier === 'TIER_2_MANAGER_REVIEW') {
    tierClass = 'tier-MANAGER';
    tagClass = 'tag-MANAGER';
    tierLabel = 'Tier 2: Finance Manager Review';
  } else if (d.approval_tier === 'TIER_3_DIRECTOR_SIGNOFF') {
    tierClass = 'tier-DIRECTOR';
    tagClass = 'tag-DIRECTOR';
    tierLabel = 'Tier 3: Executive Director Signoff';
  } else if (d.approval_tier === 'REJECTED_DISCREPANCY') {
    tierLabel = 'Rejected: 3-Way Reconciliation Variance';
  } else if (d.approval_tier === 'FROZEN_FRAUD_RISK') {
    tierLabel = 'Hold: Critical Fraud / Compliance Risk';
  }

  const banner = document.getElementById('certificateBanner');
  banner.className = `certificate-banner ${tierClass}`;

  document.getElementById('resAuthStatus').innerText = d.authorized
    ? 'AUTHORIZED FOR DISBURSEMENT WORKFLOW'
    : 'DISBURSEMENT BLOCKED BY GOVERNANCE GATE';
  document.getElementById('resTierTitle').innerText = tierLabel;
  document.getElementById('resSummaryText').innerText = d.reconciliation_summary;

  const riskBadge = document.getElementById('resRiskBadge');
  riskBadge.className = `status-badge ${tagClass}`;
  riskBadge.innerText = `Risk: ${d.risk_score.toFixed(1)} / 100 (${d.risk_level})`;

  document.getElementById('resAmountUSD').innerText = `$${Number(d.total_amount_usd).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.getElementById('resAmountINR').innerText = `INR ${Number(d.total_amount_inr).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.getElementById('resVarianceUSD').innerText = `$${Number(d.variance_amount_usd).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  document.getElementById('resPiiBadge').innerText = `${d.pii_redactions_made} PII Token(s) Scrubbed`;

  // Render Per-Item Reconciliation Diff Table
  const diffBody = document.getElementById('resItemDiffsBody');
  diffBody.innerHTML = '';
  (d.item_diffs || []).forEach((diff) => {
    const isOk = diff.status === 'MATCHED';
    const badgeCls = isOk ? 'tag-STP' : 'tag-BLOCKED';
    diffBody.innerHTML += `
      <tr>
        <td class="mono"><strong>${diff.item_id}</strong><br><span style="font-family:var(--font-sans); font-size:11px; color:var(--text-muted);">${diff.description}</span></td>
        <td class="mono" style="text-align:right;">$${diff.billed_unit_price_usd.toFixed(2)} vs $${diff.po_unit_price_usd.toFixed(2)}</td>
        <td class="mono" style="text-align:right;">${diff.billed_qty} billed / ${diff.grn_accepted_qty} ok (${diff.grn_rejected_qty} rej)</td>
        <td class="mono" style="text-align:right;">$${diff.line_variance_usd.toFixed(2)}</td>
        <td><span class="status-badge ${badgeCls}">${diff.status}</span></td>
      </tr>
    `;
  });

  // Render Perturbation Feature Contributions
  const barsContainer = document.getElementById('featureBarsContainer');
  barsContainer.innerHTML = '';
  (d.feature_contributions || []).forEach((fc) => {
    const pct = Math.min(100, Math.max(4, fc.risk_contribution * 2.2));
    const fillColor = fc.risk_contribution >= 20 ? 'var(--status-blocked-fg)' : (fc.risk_contribution >= 10 ? 'var(--status-review-fg)' : 'var(--accent-primary)');
    barsContainer.innerHTML += `
      <div class="xai-item">
        <div class="xai-item-top">
          <span class="xai-name">${fc.feature_name}</span>
          <span class="xai-val">${fc.feature_value} (+${fc.risk_contribution.toFixed(1)} pts)</span>
        </div>
        <div class="xai-track">
          <div class="xai-fill" style="width:${pct}%; background-color:${fillColor};"></div>
        </div>
        <div class="xai-desc">${fc.description}</div>
      </div>
    `;
  });

  // Render Governance Flags
  const flagsList = document.getElementById('resFlagsList');
  flagsList.innerHTML = '';
  if (!d.audit_flags || d.audit_flags.length === 0) {
    flagsList.innerHTML = '<li class="flag-ok">3-Way PO, Invoice, and Dock GRN quantities and rates verified with zero discrepancy.</li>';
  } else {
    d.audit_flags.forEach((f) => {
      flagsList.innerHTML += `<li class="flag-alert">${f}</li>`;
    });
  }

  // Render Stage Timing Telemetry
  if (d.telemetry) {
    document.getElementById('resTelemetryStrip').innerHTML = `
      <span>PII Scrub: ${d.telemetry.pii_scrub_ms.toFixed(2)}ms</span>
      <span>3-Way Match: ${d.telemetry.reconciliation_ms.toFixed(2)}ms</span>
      <span>ML Attribution: ${d.telemetry.ml_inference_ms.toFixed(2)}ms</span>
      <span>Total Pipeline: ${d.telemetry.total_pipeline_ms.toFixed(2)}ms</span>
    `;
  }
}

// -------------------------------------------------------------
// 7. Render Audit Ledger Table & Filtering
// -------------------------------------------------------------

function renderLedgerTable(items) {
  const tbody = document.getElementById('ledgerTableBody');
  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10" style="text-align:center; padding:28px; color:var(--text-muted);">
          No matching audit records in ledger.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = '';
  items.forEach((d, idx) => {
    let badgeClass = 'tag-BLOCKED';
    if (d.approval_tier === 'TIER_1_STP_AUTO_APPROVED') badgeClass = 'tag-STP';
    else if (d.approval_tier === 'TIER_2_MANAGER_REVIEW') badgeClass = 'tag-MANAGER';
    else if (d.approval_tier === 'TIER_3_DIRECTOR_SIGNOFF') badgeClass = 'tag-DIRECTOR';

    const shortTime = d.timestamp ? d.timestamp.replace('T', ' ').substring(0, 19) : '';

    tbody.innerHTML += `
      <tr>
        <td class="mono" style="padding-left:20px; font-weight:600;">${d.audit_id}</td>
        <td class="mono" style="color:var(--text-muted); font-size:11.5px;">${shortTime}</td>
        <td class="mono" style="font-weight:600;">${d.invoice_id}</td>
        <td>${d.vendor_name || 'Enterprise Vendor'} <span class="mono" style="color:var(--text-muted); font-size:11px;">(${d.vendor_country || 'IN'})</span></td>
        <td><span class="status-badge ${badgeClass}">${d.approval_tier}</span></td>
        <td class="mono" style="text-align:right; font-weight:600;">$${Number(d.total_amount_usd).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
        <td class="mono" style="text-align:right;">INR ${Number(d.total_amount_inr).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
        <td class="mono" style="text-align:right; color:${d.variance_amount_usd > 0 ? 'var(--status-blocked-fg)' : 'var(--text-muted)'};">$${Number(d.variance_amount_usd).toFixed(2)}</td>
        <td class="mono" style="text-align:right; font-weight:600;">${d.risk_score.toFixed(1)} (${d.risk_level})</td>
        <td style="text-align:right; padding-right:20px;">
          <button type="button" class="btn btn-outline btn-sm" onclick="openDetailModal(${idx})">Inspect</button>
        </td>
      </tr>
    `;
  });
}

function setupFilterChips() {
  const chips = document.querySelectorAll('#filterChipsContainer .filter-chip');
  chips.forEach((chip) => {
    chip.addEventListener('click', async () => {
      chips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      currentFilter = chip.getAttribute('data-tier') || 'ALL';
      await refreshLedger();
    });
  });
}

function setupSearch() {
  const input = document.getElementById('ledgerSearchInput');
  if (!input) return;
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q) {
      renderLedgerTable(activeLedger);
      return;
    }
    const filtered = activeLedger.filter(
      (d) =>
        d.invoice_id.toLowerCase().includes(q) ||
        (d.vendor_name || '').toLowerCase().includes(q) ||
        d.audit_id.toLowerCase().includes(q)
    );
    renderLedgerTable(filtered);
  });
}

function openDetailModal(idx) {
  const d = activeLedger[idx];
  if (!d) return;
  document.getElementById('modalTitle').innerText = `Audit Certificate — ${d.invoice_id}`;
  document.getElementById('modalSubtitle').innerText = `${d.audit_id} | ${d.timestamp}`;
  document.getElementById('modalSummaryText').innerText = d.reconciliation_summary;
  document.getElementById('modalJsonPayload').innerText = JSON.stringify(d, null, 2);
  document.getElementById('detailModalBackdrop').classList.add('open');
}

function closeDetailModal(event) {
  if (event && event.target && event.target.id !== 'detailModalBackdrop') return;
  document.getElementById('detailModalBackdrop').classList.remove('open');
}
