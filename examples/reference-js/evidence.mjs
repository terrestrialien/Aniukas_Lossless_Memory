// Bounded ALM reference example: verify captured source bytes and read one evidence window.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

const decoder = new TextDecoder('utf-8', { fatal: true });
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

function within(root, name) {
  if (typeof name !== 'string' || !name || name.includes('\\') || isAbsolute(name)) {
    throw new Error(`unsafe fixture path: ${name}`);
  }
  const file = resolve(root, name);
  const rel = relative(root, file);
  if (!rel || rel === '..' || rel.startsWith(`..\\`) || rel.startsWith('../')) {
    throw new Error(`unsafe fixture path: ${name}`);
  }
  return file;
}

function bytesAt(root, name) {
  return readFileSync(within(root, name));
}

function jsonAt(root, name) {
  return JSON.parse(decoder.decode(bytesAt(root, name)));
}

function verifyDigest(bytes, length, digest, label) {
  if (bytes.length !== length || sha256(bytes) !== digest) {
    throw new Error(`${label}: byte length or SHA-256 mismatch`);
  }
}

export function readEvidence(root, windowId = 'WIN-00005') {
  root = resolve(root);
  if (!/^[A-Za-z0-9-]+$/.test(windowId)) throw new Error('unsafe window ID');
  const manifest = jsonAt(root, 'log-manifest/LOG-EXAMPLE.json');
  const window = jsonAt(root, `evidence-window/${windowId}.json`);
  if (manifest.format_version !== '1' || window.format_version !== '1' ||
      window.id !== windowId || window.log_id !== manifest.id ||
      window.instance_id !== manifest.instance_id ||
      window.source_digest !== manifest.original_sha256) {
    throw new Error('window does not identify the sealed source');
  }

  const original = bytesAt(root, manifest.original_file);
  verifyDigest(original, manifest.original_byte_length, manifest.original_sha256, 'original');
  if (manifest.original_encoding.toUpperCase() !== 'UTF-8') {
    throw new Error('this example supports UTF-8 sources only');
  }

  const messages = new Map();
  let nextOrdinal = 1;
  let nextChunk = 1;
  let previousEnd = 0;
  for (const chunk of manifest.chunks) {
    if (chunk.number !== nextChunk++ || chunk.message_start !== nextOrdinal) {
      throw new Error('chunk numbering or message coverage is not contiguous');
    }
    const raw = bytesAt(root, chunk.file);
    verifyDigest(raw, chunk.byte_length, chunk.sha256, `chunk ${chunk.number}`);
    const chunkText = decoder.decode(raw);
    if (!chunkText.endsWith('\n') || chunkText.includes('\r')) {
      throw new Error(`chunk ${chunk.number}: expected LF-terminated JSONL`);
    }
    const lines = chunkText.slice(0, -1).split('\n');
    for (const line of lines) {
      const message = JSON.parse(line);
      if (message.log_id !== manifest.id || message.instance_id !== manifest.instance_id ||
          message.ordinal !== nextOrdinal || message.original_byte_start < previousEnd ||
          message.original_byte_end < message.original_byte_start ||
          message.original_byte_end > original.length) {
        throw new Error(`invalid message order or source selector at ordinal ${nextOrdinal}`);
      }
      const sourceText = decoder.decode(original.subarray(message.original_byte_start, message.original_byte_end));
      if (sourceText !== message.text) throw new Error(`source text mismatch at ordinal ${nextOrdinal}`);
      messages.set(nextOrdinal, message);
      previousEnd = message.original_byte_end;
      nextOrdinal++;
    }
    if (chunk.message_end !== nextOrdinal - 1) throw new Error('chunk message end disagrees with rows');
  }
  if (manifest.completeness === 'complete' && manifest.missing_ranges.length !== 0) {
    throw new Error('complete log declares missing ranges');
  }
  if (!Number.isInteger(window.message_start) || !Number.isInteger(window.message_end) ||
      window.message_start < 1 || window.message_start > window.message_end) {
    throw new Error('invalid evidence window bounds');
  }
  const cited = [];
  for (let ordinal = window.message_start; ordinal <= window.message_end; ordinal++) {
    const message = messages.get(ordinal);
    if (!message) throw new Error(`missing cited message ${ordinal}`);
    cited.push({ ordinal, timestamp: message.timestamp, text: message.text });
  }
  return { windowId, logId: manifest.id, cited };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = process.argv[2] ?? resolve('examples/memory');
  try {
    const result = readEvidence(root, process.argv[3]);
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
