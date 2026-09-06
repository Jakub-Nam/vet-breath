/**
 * Verifies the Trusted Types configuration that ships to Cloudflare Pages.
 *
 * Scope: this asserts the CSP header lands in the deployable artifact (the file
 * Cloudflare actually serves). It does NOT prove runtime enforcement — Trusted
 * Types is enforced by Chromium against the served header, which only a real
 * browser (e.g. a Playwright E2E) can verify.
 *
 * Run: `node --test scripts/trusted-types.test.mjs` (from frontend/).
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..');

// Prefer the build output (what Cloudflare serves); fall back to the source file.
const candidates = [
  join(frontendRoot, 'dist', 'frontend', 'browser', '_headers'),
  join(frontendRoot, 'public', '_headers'),
];
const headersPath = candidates.find(existsSync);
const contents = headersPath ? readFileSync(headersPath, 'utf8') : '';

const cspLine = contents
  .split('\n')
  .map((line) => line.trim())
  .find((line) => /^content-security-policy(-report-only)?:/i.test(line));

test('_headers ships to the deployable artifact', () => {
  assert.ok(headersPath, `_headers not found in any of:\n  ${candidates.join('\n  ')}`);
});

test('a Content-Security-Policy header is declared', () => {
  assert.ok(cspLine, 'No Content-Security-Policy(-Report-Only) line found in _headers');
});

test("CSP requires Trusted Types for the 'script' sink", () => {
  assert.match(cspLine ?? '', /require-trusted-types-for\s+'script'/);
});

test("CSP allows Angular's Trusted Types policy and nothing unexpected", () => {
  const directive = (cspLine ?? '').match(/trusted-types\s+([^;]+)/i);
  assert.ok(directive, 'No trusted-types directive found in the CSP');
  const policies = directive[1].trim().split(/\s+/);
  assert.ok(
    policies.includes('angular'),
    `trusted-types must list "angular"; got: ${policies.join(' ')}`,
  );
  // The app uses no bypassSecurityTrust*, so the unsafe-bypass policy must not creep in.
  assert.ok(
    !policies.includes('angular#unsafe-bypass'),
    'trusted-types allows angular#unsafe-bypass — the app has no bypassSecurityTrust* usage that needs it',
  );
});
