import { validateContract, VALIDATOR_VERSION, CONTRACT_VERSION, MAX_REQUEST_BYTES } from '../src/validator.mjs';

const defaultSchema = {
  type: 'object',
  required: ['tool', 'ok'],
  properties: {
    tool: { type: 'string', minLength: 1 },
    ok: { type: 'boolean' },
    detail: { type: 'string', maxLength: 200 },
  },
  additionalProperties: false,
};

const defaultData = {
  tool: 'search',
  ok: true,
  detail: 'hello',
};

function requireEl(id) {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing #${id} in DOM`);
  return el;
}

const els = {
  requestId: requireEl('request-id'),
  schema: requireEl('schema'),
  data: requireEl('data'),
  run: requireEl('run'),
  clear: requireEl('clear'),
  download: requireEl('download'),
  receipt: requireEl('receipt'),
  status: requireEl('status'),
  empty: requireEl('empty-state'),
  errorBanner: requireEl('error-banner'),
  meta: requireEl('meta-version'),
};

let lastReceipt = null;
let generation = 0;
function invalidateReceipt() {
  generation += 1;
  lastReceipt = null;
  els.receipt.textContent = '';
  els.empty.hidden = false;
  els.download.disabled = true;
  return generation;
}

function setStatus(text, kind) {
  els.status.textContent = text;
  els.status.dataset.kind = kind || 'idle';
}

function showError(msg) {
  els.errorBanner.hidden = !msg;
  els.errorBanner.textContent = msg || '';
}

function loadDefaults() {
  els.requestId.value = `web-${Date.now()}`;
  els.schema.value = JSON.stringify(defaultSchema, null, 2);
  els.data.value = JSON.stringify(defaultData, null, 2);
  invalidateReceipt();
  showError('');
  setStatus('Ready — paste schema and data, then Validate.', 'idle');
}

async function runValidate() {
  const ticket = invalidateReceipt();
  showError('');
  els.empty.hidden = true;
  setStatus('Validating…', 'loading');
  if (new TextEncoder().encode(els.schema.value + els.data.value + els.requestId.value).byteLength > MAX_REQUEST_BYTES) {
    showError(`Input exceeds ${MAX_REQUEST_BYTES} UTF-8 bytes.`);
    setStatus('Input too large', 'error');
    return;
  }
  let schema;
  let data;
  try {
    schema = JSON.parse(els.schema.value);
  } catch (err) {
    showError(`Schema JSON parse error: ${err.message}`);
    setStatus('Schema parse failed', 'error');
    return;
  }
  try {
    data = JSON.parse(els.data.value);
  } catch (err) {
    showError(`Data JSON parse error: ${err.message}`);
    setStatus('Data parse failed', 'error');
    return;
  }

  const request_id = (els.requestId.value || '').trim() || `web-${Date.now()}`;
  const receipt = await validateContract({ request_id, schema, data });
  if (ticket !== generation) return;
  lastReceipt = receipt;
  // Always render as plain text — never interpret HTML/scripts in payload.
  els.receipt.textContent = JSON.stringify(receipt, null, 2);
  els.download.disabled = false;
  setStatus(
    receipt.valid ? 'Valid receipt' : `Invalid — ${receipt.errors.length} error(s)`,
    receipt.valid ? 'ok' : 'fail',
  );
}

function onValidateClick() {
  const expectedGeneration = generation + 1;
  return runValidate().catch((err) => {
    if (generation !== expectedGeneration) return;
    invalidateReceipt();
    showError(String(err?.message || err));
    setStatus('Unexpected error', 'error');
  });
}

function onDownloadClick() {
  if (!lastReceipt) return;
  const blob = new Blob([JSON.stringify(lastReceipt, null, 2)], {
    type: 'application/json',
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `validation-receipt-${lastReceipt.request_id || 'receipt'}.json`;
  a.rel = 'noopener';
  a.click();
  URL.revokeObjectURL(url);
}

els.run.addEventListener('click', onValidateClick);
els.clear.addEventListener('click', loadDefaults);
els.download.addEventListener('click', onDownloadClick);

for (const input of [els.requestId, els.schema, els.data]) {
  input.addEventListener('input', () => {
    invalidateReceipt();
    showError('');
    setStatus('Input changed — validate again.', 'idle');
  });
}

// Expose for smoke tests / progressive enhancement
window.__contractCheck = {
  runValidate: onValidateClick,
  loadDefaults,
  downloadReceipt: onDownloadClick,
  version: { contract: CONTRACT_VERSION, validator: VALIDATOR_VERSION },
};

els.meta.textContent = `${CONTRACT_VERSION} · validator ${VALIDATOR_VERSION}`;
loadDefaults();
