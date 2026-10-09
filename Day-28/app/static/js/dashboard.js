/**
 * FinDoc-AuditEngine Live Enterprise Dashboard Controller.
 * Pure Vanilla JavaScript: Fast, resilient, zero-framework dependency.
 */

let benchmarkPresets = [];
let activeLedger = [];
let currentFilter = 'ALL';

document.addEventListener('DOMContentLoaded', async () => {
  await loadPresets();
  await refreshMetrics();
  await refreshLedger();
  setupFilterChips();
  setupSearch();
});

// -------------------------------------------------------------
// 1. Data Fetching: Presets, Metrics, Ledger
// -------------------------------------------------------------

async function loadPresets() {
  try {
    const res = await fetch('/api/v1/audit/presets');
    if (res.ok) {
      benchmarkPresets = await res.json();
      const select = document.getElementById('presetSelect');
      if (select && benchmarkPresets.length > 0) {
        select.innerHTML = '<option value="">-- Choose a Live Enterprise Scenario --</option>';
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
      document.getElementById('metricDisbursedUSD').innerText = `$${Number(data.total_disbursed_usd).toLocaleString()}`;
      document.getElementById('metricDisbursedINR').innerText = `₹${Number(data.total_disbursed_inr).toLocaleString()}`;
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
// 2. Preset Selection & Form Auto-fill
// -------------------------------------------------------------

function onPresetSelected() {
  const select = document.getElementById('presetSelect');
  const idx = select.value;
  if (idx === '' || !benchmarkPresets[idx]) return;

  const { invoice, po } = benchmarkPresets[idx];

  document.getElementById('inputInvoiceId').value = invoice.invoice_id;
  document.getElementById('inputVendorName').value = invoice.vendor_name;
  document.getElementById('inputPoNumber').value = invoice.po_number || '';
  document.getElementById('inputAmount').value = invoice.total_amount_usd;
  document.getElementById('inputCountry').value = invoice.vendor_country || 'IN';
  document.getElementById('inputEmail').value = invoice.vendor_contact_email || '';
  document.getElementById('inputPan').value = invoice.vendor_pan || '';
  document.getElementById('inputIsNew').checked = invoice.is_new_vendor || false;

  // Render Line items table
  const tbody = document.getElementById('itemsTableBody');
  tbody.innerHTML = '';
  (invoice.items || []).forEach(item => {
    const poItem = (po.items || []).find(p => p.item_id === item.item_id) || item;
    const grnRec = (po.grn_units_received || {})[item.item_id] ?? poItem.quantity;
    const grnRej = (po.grn_units_rejected || {})[item.item_id] ?? 0;

    tbody.innerHTML += `
      <tr>
        <td><strong>${item.item_id}</strong><br><small style="color:#64748b">${item.description}</small></td>
        <td>$${item.unit_price_usd.toFixed(2)}</td>
        <td>$${poItem.unit_price_usd.toFixed(2)}</td>
        <td>${item.quantity}</td>
        <td>${grnRec - grnRej} accepted (${grnRej} rejected)</td>
      </tr>
    `;
  });

  // Store active PO object for submission
  window.currentSelectedPO = po;
}

// -------------------------------------------------------------
// 3. Live Audit Execution (POST /api/v1/audit/process)
// -------------------------------------------------------------

async function executeAudit(event) {
  if (event) event.preventDefault();

  const btn = document.getElementById('btnSubmitAudit');
  btn.disabled = true;
  btn.innerHTML = '<span>Processing Anomaly & Governance Gates...</span>';

  const invoiceId = document.getElementById('inputInvoiceId').value.trim();
  const vendorName = document.getElementById('inputVendorName').value.trim();
  const poNumber = document.getElementById('inputPoNumber').value.trim();
  const totalAmount = parseFloat(document.getElementById('inputAmount').value);
  const country = document.getElementById('inputCountry').value.trim().toUpperCase();
  const email = document.getElementById('inputEmail').value.trim();
  const pan = document.getElementById('inputPan').value.trim();
  const isNew = document.getElementById('inputIsNew').checked;

  // Fallback line item if none in table
  const lineItems = (window.currentSelectedPO && window.currentSelectedPO.items)
    ? window.currentSelectedPO.items
    : [{ item_id: 'ITEM-1', description: 'Enterprise Services', quantity: 1, unit_price_usd: totalAmount, total_price_usd: totalAmount }];

  const payload = {
    invoice: {
      invoice_id: invoiceId || 'INV-MANUAL-01',
      vendor_id: 'VEND-LIVE',
      vendor_name: vendorName || 'Direct Vendor Inc',
      po_number: poNumber || 'PO-LIVE',
      invoice_date: new Date().toISOString().split('T')[0],
      due_date: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
      subtotal_usd: totalAmount,
      tax_usd: 0.0,
      total_amount_usd: totalAmount,
      currency: 'USD',
      items: lineItems,
      vendor_country: country,
      is_new_vendor: isNew,
      vendor_contact_email: email,
      vendor_pan: pan,
    },
    purchase_order: window.currentSelectedPO || {
      po_number: poNumber || 'PO-LIVE',
      vendor_id: 'VEND-LIVE',
      approved_total_usd: totalAmount,
      items: lineItems,
      grn_units_received: { [lineItems[0].item_id]: lineItems[0].quantity },
      grn_units_rejected: { [lineItems[0].item_id]: 0 },
    }
  };

  try {
    const res = await fetch('/api/v1/audit/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      alert(`Audit failed: ${err.detail || err.message || 'Unknown error'}`);
      return;
    }

    const decision = await res.json();
    renderInspectionResult(decision);
    await refreshMetrics();
    await refreshLedger();
  } catch (err) {
    console.error('Audit execution error:', err);
    alert('Communication error with FinDoc-AuditEngine backend.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>⚡ Run Financial Audit & ML Risk Analysis</span>';
  }
}

// -------------------------------------------------------------
// 4. Render Inspection Result Hero & Metrics
// -------------------------------------------------------------

function renderInspectionResult(d) {
  const resultCard = document.getElementById('inspectionResultCard');
  resultCard.style.display = 'block';

  let tierClass = 'tier-BLOCKED';
  let tagClass = 'tag-BLOCKED';
  let tierLabel = d.approval_tier;

  if (d.approval_tier === 'TIER_1_STP_AUTO_APPROVED') {
    tierClass = 'tier-STP';
    tagClass = 'tag-STP';
    tierLabel = 'Tier 1: Straight-Through (STP)';
  } else if (d.approval_tier === 'TIER_2_MANAGER_REVIEW') {
    tierClass = 'tier-MANAGER';
    tagClass = 'tag-MANAGER';
    tierLabel = 'Tier 2: Manager Review Required';
  } else if (d.approval_tier === 'TIER_3_DIRECTOR_SIGNOFF') {
    tierClass = 'tier-DIRECTOR';
    tagClass = 'tag-DIRECTOR';
    tierLabel = 'Tier 3: Executive Director Signoff';
  } else if (d.approval_tier === 'FROZEN_FRAUD_RISK') {
    tierLabel = 'CRITICAL: Frozen Fraud Risk';
  } else if (d.approval_tier === 'REJECTED_DISCREPANCY') {
    tierLabel = 'BLOCKED: Reconciliation Variance';
  }

  const hero = document.getElementById('decisionHero');
  hero.className = `decision-hero ${tierClass}`;
  hero.innerHTML = `
    <div class="hero-status-row">
      <span class="tier-tag ${tagClass}">${tierLabel}</span>
      <span style="font-size:0.75rem; font-family:var(--font-mono); color:var(--text-muted)">${d.audit_id}</span>
    </div>
    <div class="hero-title">${d.authorized ? '✅ APPROVED DISBURSEMENT' : '⛔ TRANSACTION BLOCKED'}</div>
    <div class="hero-summary">${d.reconciliation_summary}</div>
  `;

  // Dual Currency Card
  document.getElementById('resValUSD').innerText = `$${d.total_amount_usd.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  document.getElementById('resValINR').innerText = `₹${d.total_amount_inr.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  document.getElementById('resVarianceUSD').innerText = `$${d.variance_amount_usd.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
  document.getElementById('resVarianceINR').innerText = `₹${d.variance_amount_inr.toLocaleString(undefined, {minimumFractionDigits: 2})}`;

  // Risk Score Meter
  const scoreVal = document.getElementById('resRiskScore');
  scoreVal.innerText = d.risk_score;
  const scoreFill = document.getElementById('resRiskFill');
  scoreFill.style.width = `${Math.min(100, d.risk_score)}%`;
  
  if (d.risk_score >= 85) scoreFill.style.backgroundColor = '#ef4444';
  else if (d.risk_score >= 65) scoreFill.style.backgroundColor = '#f97316';
  else if (d.risk_score >= 35) scoreFill.style.backgroundColor = '#f59e0b';
  else scoreFill.style.backgroundColor = '#10b981';

  // Feature Contributions List
  const contribBox = document.getElementById('resFeatureContributions');
  contribBox.innerHTML = '';
  (d.feature_contributions || []).forEach(c => {
    const fillPercent = Math.min(100, (c.risk_contribution / 45.0) * 100);
    const color = c.risk_contribution > 25 ? '#ef4444' : (c.risk_contribution > 10 ? '#f59e0b' : '#3b82f6');
    contribBox.innerHTML += `
      <div class="contrib-item">
        <div class="contrib-header">
          <span>${c.feature_name} (${c.feature_value})</span>
          <span style="color:${color}">+${c.risk_contribution.toFixed(1)} pts</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${fillPercent}%; background-color: ${color}"></div>
        </div>
      </div>
    `;
  });

  // Privacy Redactions Badge
  document.getElementById('resPiiRedactions').innerText = `${d.pii_redactions_made} sensitive tokens masked`;

  // Audit Flags
  const flagsList = document.getElementById('resAuditFlags');
  if (d.audit_flags && d.audit_flags.length > 0) {
    flagsList.innerHTML = d.audit_flags.map(f => `<li style="margin-bottom:0.35rem; color:#f87171">⚠️ ${f}</li>`).join('');
  } else {
    flagsList.innerHTML = `<li style="color:#10b981">✨ Clean transaction: Zero compliance flags detected.</li>`;
  }
}

// -------------------------------------------------------------
// 5. Render Audit Ledger & Filters
// -------------------------------------------------------------

function renderLedgerTable(items) {
  const tbody = document.getElementById('ledgerTableBody');
  if (!items || items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#64748b; padding:2rem">No audit records found matching active filter.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map((row, idx) => {
    const isApproved = row.authorized;
    return `
      <tr>
        <td style="font-family:var(--font-mono); color:#94a3b8">${new Date(row.timestamp).toLocaleTimeString()}</td>
        <td><strong>${row.invoice_id}</strong></td>
        <td>$${row.total_amount_usd.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
        <td style="color:#06b6d4; font-weight:600">₹${row.total_amount_inr.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
        <td><span style="font-weight:700; color:${row.risk_score >= 65 ? '#ef4444' : '#10b981'}">${row.risk_score}</span></td>
        <td><span class="badge-status ${isApproved ? 'badge-approved' : 'badge-blocked'}">${isApproved ? 'APPROVED' : 'BLOCKED'}</span></td>
        <td>
          <button class="btn-secondary" style="padding:0.25rem 0.65rem; font-size:0.75rem" onclick="openDetailsModal(${idx})">Inspect</button>
        </td>
      </tr>
    `;
  }).join('');
}

function setupFilterChips() {
  const chips = document.querySelectorAll('.chip');
  chips.forEach(c => {
    c.addEventListener('click', () => {
      chips.forEach(x => x.classList.remove('active'));
      c.classList.add('active');
      currentFilter = c.getAttribute('data-tier');
      refreshLedger();
    });
  });
}

function setupSearch() {
  const input = document.getElementById('ledgerSearch');
  if (input) {
    input.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = activeLedger.filter(r => r.invoice_id.toLowerCase().includes(q));
      renderLedgerTable(filtered);
    });
  }
}

function openDetailsModal(index) {
  const record = activeLedger[index];
  if (!record) return;

  document.getElementById('modalTitle').innerText = `Audit Details: ${record.invoice_id} (${record.audit_id})`;
  document.getElementById('modalJsonPayload').innerText = JSON.stringify(record, null, 2);
  document.getElementById('detailsModal').style.display = 'flex';
}

function closeModal() {
  document.getElementById('detailsModal').style.display = 'none';
}
