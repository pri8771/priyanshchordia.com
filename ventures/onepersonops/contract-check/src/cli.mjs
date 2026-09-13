#!/usr/bin/env node
/**
 * Contract Check CLI — one JSON request on stdin → one receipt on stdout.
 * exit 0 = valid, 1 = invalid_data, 2 = invalid_request
 */
import { validateContract, VALIDATOR_VERSION, CONTRACT_VERSION, MAX_REQUEST_BYTES } from './validator.mjs';

async function readStdin() {
  const chunks = [];
  let bytes = 0;
  for await (const chunk of process.stdin) {
    bytes += chunk.length;
    if (bytes > MAX_REQUEST_BYTES) {
      const error = new Error(`Request exceeds ${MAX_REQUEST_BYTES} UTF-8 bytes.`);
      error.code = 'SIZE_EXCEEDED';
      throw error;
    }
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8');
}

function isInvalidRequest(receipt) {
  return (
    receipt.request_id === null ||
    (receipt.errors || []).some(
      (e) => e.code === 'INVALID_REQUEST' || e.code === 'SIZE_EXCEEDED',
    )
  );
}

async function main() {
  let raw;
  try {
    raw = await readStdin();
  } catch (err) {
    const receipt = {
      contract_version: CONTRACT_VERSION,
      request_id: null,
      schema_sha256: null,
      input_sha256: null,
      validator_version: VALIDATOR_VERSION,
      valid: false,
      errors: [
        {
          path: '$',
          code: err.code === 'SIZE_EXCEEDED' ? 'SIZE_EXCEEDED' : 'INVALID_REQUEST',
          expected: 'readable stdin JSON within the request byte limit',
          actual_type: 'io_error',
          hint: String(err?.message || err),
        },
      ],
      processed_at: new Date().toISOString(),
    };
    process.stdout.write(JSON.stringify(receipt) + '\n');
    process.exit(2);
  }

  let request;
  try {
    if (!raw.trim()) throw new Error('empty stdin');
    request = JSON.parse(raw);
  } catch (err) {
    const receipt = {
      contract_version: CONTRACT_VERSION,
      request_id: null,
      schema_sha256: null,
      input_sha256: null,
      validator_version: VALIDATOR_VERSION,
      valid: false,
      errors: [
        {
          path: '$',
          code: 'INVALID_REQUEST',
          expected: 'exactly one JSON object',
          actual_type: 'parse_error',
          hint: String(err?.message || err),
        },
      ],
      processed_at: new Date().toISOString(),
    };
    process.stdout.write(JSON.stringify(receipt) + '\n');
    process.exit(2);
  }

  const receipt = await validateContract(request);
  process.stdout.write(JSON.stringify(receipt) + '\n');
  if (isInvalidRequest(receipt)) process.exit(2);
  process.exit(receipt.valid ? 0 : 1);
}

main();
