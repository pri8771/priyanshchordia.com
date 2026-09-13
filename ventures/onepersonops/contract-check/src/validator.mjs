/**
 * One Person Ops — Contract Check validator (ValidationReceiptV1).
 * Pure, deterministic, side-effect free. No network/model/fs/telemetry.
 */

export const VALIDATOR_VERSION = '1.0.0';
export const CONTRACT_VERSION = 'ValidationReceiptV1';
export const MAX_REQUEST_BYTES = 64 * 1024;
export const MAX_NESTING = 16;
export const MAX_ERRORS = 100;

const SUPPORTED_KEYWORDS = new Set([
  'type',
  'required',
  'properties',
  'additionalProperties',
  'items',
  'enum',
  'minLength',
  'maxLength',
  'minimum',
  'maximum',
  'minItems',
  'maxItems',
]);

const TYPE_SET = new Set([
  'object',
  'array',
  'string',
  'number',
  'integer',
  'boolean',
  'null',
]);

/** Sorted-key canonical JSON (UTF-8) for hashing / replay. */
export function canonicalize(value) {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(value) {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map(sortKeys);
  const out = Object.create(null);
  for (const key of Object.keys(value).sort()) {
    out[key] = sortKeys(value[key]);
  }
  return out;
}

export async function sha256Hex(text) {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function utf8Bytes(text) {
  return new TextEncoder().encode(text).byteLength;
}

function jsonType(value) {
  if (value === null) return 'null';
  if (Array.isArray(value)) return 'array';
  return typeof value;
}

function isInteger(value) {
  return typeof value === 'number' && Number.isInteger(value);
}

function ownKeys(obj) {
  return Object.keys(obj);
}

function hasOwn(obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key);
}

function pushError(errors, entry) {
  if (errors.length >= MAX_ERRORS) return false;
  errors.push(entry);
  return errors.length < MAX_ERRORS;
}

function unsupportedKeyword(schema, path, errors) {
  if (!schema || typeof schema !== 'object' || Array.isArray(schema)) return false;
  for (const key of ownKeys(schema)) {
    if (!SUPPORTED_KEYWORDS.has(key)) {
      pushError(errors, {
        path: path || '$',
        code: 'SCHEMA_UNSUPPORTED',
        expected: `supported keyword; got "${key}"`,
        actual_type: 'schema',
        hint: `Remove unsupported keyword "${key}". Supported: ${[...SUPPORTED_KEYWORDS].join(', ')}.`,
      });
      return true;
    }
  }
  return false;
}

function checkType(value, typeSpec, path, errors) {
  const types = Array.isArray(typeSpec) ? typeSpec : [typeSpec];
  for (const t of types) {
    if (!TYPE_SET.has(t)) {
      pushError(errors, {
        path,
        code: 'SCHEMA_UNSUPPORTED',
        expected: 'type in object|array|string|number|integer|boolean|null',
        actual_type: String(t),
        hint: 'Use only the Contract Check type subset.',
      });
      return false;
    }
  }
  const actual = jsonType(value);
  const ok = types.some((t) => {
    if (t === 'integer') return isInteger(value);
    if (t === 'number') return typeof value === 'number' && !Number.isNaN(value);
    return actual === t;
  });
  if (!ok) {
    pushError(errors, {
      path,
      code: 'TYPE_MISMATCH',
      expected: types.join('|'),
      actual_type: actual,
      hint: `Value at ${path} must be ${types.join(' or ')}.`,
    });
  }
  return ok;
}

function checkSchema(schema, path, errors) {
  if (errors.length >= MAX_ERRORS) return;
  if (!schema || typeof schema !== 'object' || Array.isArray(schema)) {
    pushError(errors, { path, code: 'INVALID_SCHEMA', expected: 'object schema',
      actual_type: jsonType(schema), hint: 'Schema nodes must be JSON objects.' });
    return;
  }
  if (unsupportedKeyword(schema, path, errors)) return;
  const invalid = (key, expected) => pushError(errors, {
    path, code: 'INVALID_SCHEMA', expected, actual_type: jsonType(schema[key]),
    hint: `Use a supported value for ${key}.`,
  });
  if (hasOwn(schema, 'type')) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!types.length || types.some((t) => !TYPE_SET.has(t))) {
      pushError(errors, { path, code: 'SCHEMA_UNSUPPORTED', expected: 'supported non-empty type selection',
        actual_type: 'schema', hint: 'Use the documented type subset.' });
    }
  }
  if (hasOwn(schema, 'required') && (!Array.isArray(schema.required) ||
      schema.required.some((key) => typeof key !== 'string'))) invalid('required', 'array of property names');
  if (hasOwn(schema, 'enum') && !Array.isArray(schema.enum)) invalid('enum', 'enum array');
  if (hasOwn(schema, 'additionalProperties') && typeof schema.additionalProperties !== 'boolean') {
    pushError(errors, { path, code: 'SCHEMA_UNSUPPORTED', expected: 'additionalProperties boolean',
      actual_type: jsonType(schema.additionalProperties), hint: 'Only boolean additionalProperties is supported.' });
  }
  for (const key of ['minLength', 'maxLength', 'minItems', 'maxItems']) {
    if (hasOwn(schema, key) && (!Number.isInteger(schema[key]) || schema[key] < 0)) invalid(key, 'non-negative integer');
  }
  for (const key of ['minimum', 'maximum']) {
    if (hasOwn(schema, key) && (typeof schema[key] !== 'number' || !Number.isFinite(schema[key]))) invalid(key, 'finite number');
  }
  if (hasOwn(schema, 'properties')) {
    if (!schema.properties || typeof schema.properties !== 'object' || Array.isArray(schema.properties)) {
      invalid('properties', 'object mapping property names to schemas');
    } else {
      for (const key of ownKeys(schema.properties)) checkSchema(schema.properties[key], `${path}.${key}`, errors);
    }
  }
  if (hasOwn(schema, 'items')) checkSchema(schema.items, `${path}[]`, errors);
}

function checkJson(value, path, depth, errors) {
  if (errors.length >= MAX_ERRORS) return;
  if (depth > MAX_NESTING) {
    pushError(errors, { path: '$', code: 'DEPTH_EXCEEDED', expected: `nesting <= ${MAX_NESTING}`,
      actual_type: 'request', hint: 'Flatten the payload or schema.' });
    return;
  }
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number' && Number.isFinite(value)) return;
  if (typeof value !== 'object') {
    pushError(errors, { path, code: 'INVALID_REQUEST', expected: 'finite JSON value',
      actual_type: jsonType(value), hint: 'Use only JSON objects, arrays, strings, finite numbers, booleans or null.' });
    return;
  }
  for (const key of ownKeys(value)) {
    if (['__proto__', 'constructor', 'prototype'].includes(key)) {
      pushError(errors, { path, code: 'PROTOTYPE_KEY', expected: 'no prototype-polluting keys',
        actual_type: 'object', hint: 'Remove __proto__, constructor or prototype keys.' });
    }
    checkJson(value[key], Array.isArray(value) ? `${path}[${key}]` : `${path}.${key}`, depth + 1, errors);
  }
}

function validateNode(schema, data, path, depth, errors) {
  if (errors.length >= MAX_ERRORS) return;
  if (depth > MAX_NESTING) {
    pushError(errors, {
      path,
      code: 'DEPTH_EXCEEDED',
      expected: `nesting <= ${MAX_NESTING}`,
      actual_type: jsonType(data),
      hint: 'Flatten the payload or raise nesting only via a new contract version.',
    });
    return;
  }
  if (unsupportedKeyword(schema, path, errors)) return;
  if (!schema || typeof schema !== 'object') {
    pushError(errors, {
      path,
      code: 'INVALID_SCHEMA',
      expected: 'object schema',
      actual_type: jsonType(schema),
      hint: 'Schema must be a JSON object.',
    });
    return;
  }

  if (hasOwn(schema, 'additionalProperties') && typeof schema.additionalProperties !== 'boolean') {
    pushError(errors, {
      path: path || '$',
      code: 'SCHEMA_UNSUPPORTED',
      expected: 'additionalProperties boolean',
      actual_type: jsonType(schema.additionalProperties),
      hint: 'Only boolean additionalProperties is supported in Contract Check.',
    });
    return;
  }

  if (hasOwn(schema, 'type')) {
    if (!checkType(data, schema.type, path, errors)) return;
  }

  if (hasOwn(schema, 'enum')) {
    const allowed = schema.enum;
    if (!Array.isArray(allowed)) {
      pushError(errors, {
        path,
        code: 'INVALID_SCHEMA',
        expected: 'enum array',
        actual_type: jsonType(allowed),
        hint: 'enum must be an array of literals.',
      });
      return;
    }
    const hit = allowed.some((v) => canonicalize(v) === canonicalize(data));
    if (!hit) {
      pushError(errors, {
        path,
        code: 'ENUM_MISMATCH',
        expected: `one of ${canonicalize(allowed)}`,
        actual_type: jsonType(data),
        hint: `Value at ${path} must match the enum.`,
      });
    }
  }

  if (typeof data === 'string') {
    const characterCount = [...data].length;
    if (hasOwn(schema, 'minLength') && characterCount < schema.minLength) {
      pushError(errors, {
        path,
        code: 'MIN_LENGTH',
        expected: `length >= ${schema.minLength}`,
        actual_type: 'string',
        hint: `Provide at least ${schema.minLength} characters.`,
      });
    }
    if (hasOwn(schema, 'maxLength') && characterCount > schema.maxLength) {
      pushError(errors, {
        path,
        code: 'MAX_LENGTH',
        expected: `length <= ${schema.maxLength}`,
        actual_type: 'string',
        hint: `Shorten to at most ${schema.maxLength} characters.`,
      });
    }
  }

  if (typeof data === 'number') {
    if (hasOwn(schema, 'minimum') && data < schema.minimum) {
      pushError(errors, {
        path,
        code: 'MINIMUM',
        expected: `>= ${schema.minimum}`,
        actual_type: 'number',
        hint: `Increase value to at least ${schema.minimum}.`,
      });
    }
    if (hasOwn(schema, 'maximum') && data > schema.maximum) {
      pushError(errors, {
        path,
        code: 'MAXIMUM',
        expected: `<= ${schema.maximum}`,
        actual_type: 'number',
        hint: `Decrease value to at most ${schema.maximum}.`,
      });
    }
  }

  if (Array.isArray(data)) {
    if (hasOwn(schema, 'minItems') && data.length < schema.minItems) {
      pushError(errors, {
        path,
        code: 'MIN_ITEMS',
        expected: `items >= ${schema.minItems}`,
        actual_type: 'array',
        hint: `Add items until length is at least ${schema.minItems}.`,
      });
    }
    if (hasOwn(schema, 'maxItems') && data.length > schema.maxItems) {
      pushError(errors, {
        path,
        code: 'MAX_ITEMS',
        expected: `items <= ${schema.maxItems}`,
        actual_type: 'array',
        hint: `Remove items until length is at most ${schema.maxItems}.`,
      });
    }
    if (hasOwn(schema, 'items')) {
      for (let i = 0; i < data.length; i++) {
        validateNode(schema.items, data[i], `${path}[${i}]`, depth + 1, errors);
        if (errors.length >= MAX_ERRORS) return;
      }
    }
  }

  if (data !== null && typeof data === 'object' && !Array.isArray(data)) {
    // Prototype-key denial: only own enumerable string keys; never follow __proto__.
    const keys = ownKeys(data);
    if (keys.includes('__proto__') || keys.includes('constructor') || keys.includes('prototype')) {
      pushError(errors, {
        path,
        code: 'PROTOTYPE_KEY',
        expected: 'no prototype-polluting keys',
        actual_type: 'object',
        hint: 'Remove __proto__, constructor, or prototype keys from the payload.',
      });
    }

    if (hasOwn(schema, 'required')) {
      for (const req of schema.required) {
        if (!hasOwn(data, req)) {
          pushError(errors, {
            path: `${path}.${req}`,
            code: 'REQUIRED',
            expected: 'present',
            actual_type: 'undefined',
            hint: `Add required property "${req}".`,
          });
        }
      }
    }

    const props = hasOwn(schema, 'properties') ? schema.properties : null;
    for (const key of keys) {
      const childPath = path === '$' ? `$.${key}` : `${path}.${key}`;
      if (props && hasOwn(props, key)) {
        validateNode(props[key], data[key], childPath, depth + 1, errors);
      } else if (hasOwn(schema, 'additionalProperties') && schema.additionalProperties === false) {
        pushError(errors, {
          path: childPath,
          code: 'ADDITIONAL_PROPERTY',
          expected: 'no additional properties',
          actual_type: jsonType(data[key]),
          hint: `Remove unexpected property "${key}".`,
        });
      } else {
        // Still walk children for nesting limits even when extras are allowed / untyped.
        const child = data[key];
        if (child !== null && typeof child === 'object') {
          validateNode({ type: jsonType(child) }, child, childPath, depth + 1, errors);
        }
      }
      if (errors.length >= MAX_ERRORS) return;
    }
  }
}

/**
 * @param {{ request_id: string, schema: object, data: unknown }} request
 * @returns {Promise<object>} ValidationReceiptV1
 */
export async function validateContract(request) {
  const processed_at = new Date().toISOString();
  const errors = [];

  if (!request || typeof request !== 'object' || Array.isArray(request)) {
    return {
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
          expected: 'object with request_id, schema, data',
          actual_type: jsonType(request),
          hint: 'Send a single JSON object request.',
        },
      ],
      processed_at,
    };
  }

  const request_id = request.request_id;
  if (typeof request_id !== 'string' || request_id.length === 0) {
    errors.push({
      path: '$.request_id',
      code: 'INVALID_REQUEST',
      expected: 'non-empty string request_id',
      actual_type: jsonType(request_id),
      hint: 'Provide request_id as a non-empty string.',
    });
  }

  for (const key of ['schema', 'data']) {
    if (!hasOwn(request, key)) errors.push({ path: `$.${key}`, code: 'INVALID_REQUEST',
      expected: `own ${key} property`, actual_type: 'missing', hint: `Provide ${key}.` });
  }
  // Inspect JSON structure independently of schema application, stopping at the depth/error limits.
  if (hasOwn(request, 'schema')) checkJson(request.schema, '$.schema', 0, errors);
  if (hasOwn(request, 'data')) checkJson(request.data, '$', 0, errors);

  // Size limit applies to the UTF-8 encoding of the request object (excluding processed_at).
  let requestBytes = 0;
  try {
    if (!errors.some((e) => e.code === 'DEPTH_EXCEEDED')) requestBytes = utf8Bytes(canonicalize(request));
  } catch {
    errors.push({
      path: '$',
      code: 'INVALID_REQUEST',
      expected: 'JSON-serializable request',
      actual_type: 'unserializable',
      hint: 'Request must be JSON-serializable.',
    });
  }
  if (requestBytes > MAX_REQUEST_BYTES) {
    errors.push({
      path: '$',
      code: 'SIZE_EXCEEDED',
      expected: `<= ${MAX_REQUEST_BYTES} bytes`,
      actual_type: 'request',
      hint: `Shrink the request below ${MAX_REQUEST_BYTES} UTF-8 bytes.`,
    });
  }

  let schema_sha256 = null;
  let input_sha256 = null;
  try {
    if (!errors.some((e) => e.code === 'DEPTH_EXCEEDED')) {
      schema_sha256 = await sha256Hex(canonicalize(request.schema ?? null));
      input_sha256 = await sha256Hex(canonicalize(request.data ?? null));
    }
  } catch {
    if (!errors.some((e) => e.code === 'INVALID_REQUEST')) errors.push({
      path: '$', code: 'INVALID_REQUEST', expected: 'JSON values and available SHA-256',
      actual_type: 'hash_failure', hint: 'Use JSON values and a runtime with Web Crypto SHA-256.' });
  }

  if (errors.length) {
    return {
      contract_version: CONTRACT_VERSION,
      request_id: typeof request_id === 'string' ? request_id : null,
      schema_sha256,
      input_sha256,
      validator_version: VALIDATOR_VERSION,
      valid: false,
      errors: errors.slice(0, MAX_ERRORS),
      processed_at,
    };
  }

  checkSchema(request.schema, '$', errors);
  if (!errors.length) validateNode(request.schema, request.data, '$', 0, errors);

  return {
    contract_version: CONTRACT_VERSION,
    request_id,
    schema_sha256,
    input_sha256,
    validator_version: VALIDATOR_VERSION,
    valid: errors.length === 0,
    errors: errors.slice(0, MAX_ERRORS),
    processed_at,
  };
}
