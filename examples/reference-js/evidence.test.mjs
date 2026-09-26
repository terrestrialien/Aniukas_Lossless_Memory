import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, join } from 'node:path';
import test from 'node:test';
import { readEvidence } from './evidence.mjs';

const fixture = resolve('examples/memory');

test('returns the exact cited line from the sealed source', () => {
  const result = readEvidence(fixture);
  assert.equal(result.windowId, 'WIN-00005');
  assert.equal(result.cited[0].ordinal, 5);
  assert.match(result.cited[0].text, /^Defer the repair workshop/);
});

function withCopy(change, message) {
  const temp = mkdtempSync(join(tmpdir(), 'alm-evidence-'));
  const copy = join(temp, 'memory');
  try {
    cpSync(fixture, copy, { recursive: true });
    change(copy);
    assert.throws(() => readEvidence(copy), message);
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
}

test('rejects altered original bytes', () => withCopy(root => {
  const file = join(root, 'logs/original.txt');
  const bytes = readFileSync(file);
  bytes[50] ^= 1;
  writeFileSync(file, bytes);
}, /original: byte length or SHA-256 mismatch/));

test('rejects altered normalized messages even after a matching chunk rehash', () => withCopy(root => {
  const file = join(root, 'logs/c001.jsonl');
  const changed = readFileSync(file, 'utf8').replace('Defer the repair workshop', 'Cancel the repair workshop');
  writeFileSync(file, changed);
  const manifestFile = join(root, 'log-manifest/LOG-EXAMPLE.json');
  const manifest = JSON.parse(readFileSync(manifestFile, 'utf8'));
  const bytes = readFileSync(file);
  manifest.chunks[0].byte_length = bytes.length;
  manifest.chunks[0].sha256 = createHash('sha256').update(bytes).digest('hex');
  writeFileSync(manifestFile, JSON.stringify(manifest));
}, /source text mismatch at ordinal 5/));

test('rejects a window bound to a different source digest', () => withCopy(root => {
  const file = join(root, 'evidence-window/WIN-00005.json');
  const window = JSON.parse(readFileSync(file, 'utf8'));
  window.source_digest = '0'.repeat(64);
  writeFileSync(file, JSON.stringify(window));
}, /window does not identify the sealed source/));
