import { test, expect, type Route } from '@playwright/test';

/**
 * Runtime enforcement of Trusted Types.
 *
 * Cloudflare serves the policy report-only in prod (see `public/_headers`); here
 * we inject the *enforcing* form on the document response so the browser blocks
 * — not just reports — unsafe DOM sinks. Passing proves two things: the app boots
 * cleanly under enforced Trusted Types (safe to flip report-only → enforce), and
 * the `angular` policy actually rejects raw-string injection.
 */
const ENFORCING_CSP = "require-trusted-types-for 'script'; trusted-types angular";

async function enforceTrustedTypes(route: Route): Promise<void> {
  if (route.request().resourceType() !== 'document') {
    await route.continue();
    return;
  }
  const response = await route.fetch();
  await route.fulfill({
    response,
    headers: { ...response.headers(), 'content-security-policy': ENFORCING_CSP },
  });
}

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    (window as unknown as { __ttViolations: string[] }).__ttViolations = [];
    document.addEventListener('securitypolicyviolation', (event) => {
      (window as unknown as { __ttViolations: string[] }).__ttViolations.push(
        `${event.violatedDirective} @ ${event.blockedURI || event.sourceFile}`,
      );
    });
  });
  await page.route('**/*', enforceTrustedTypes);
});

test('app boots under enforced Trusted Types with no violations', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('app-root')).toBeAttached();
  await expect(page.locator('input[type="email"]')).toBeVisible();

  const violations = await page.evaluate(
    () => (window as unknown as { __ttViolations: string[] }).__ttViolations,
  );
  expect(violations, `Trusted Types violations during load:\n${violations.join('\n')}`).toEqual([]);
});

test('Trusted Types blocks a raw-string DOM sink', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('app-root')).toBeAttached();

  const outcome = await page.evaluate(() => {
    try {
      const element = document.createElement('div');
      // Under enforced Trusted Types this assignment must throw, not sanitize.
      (element as unknown as { innerHTML: string }).innerHTML =
        '<img src=x onerror="window.__pwned = true">';
      return element.innerHTML.includes('img') ? 'not-enforced' : 'sanitized';
    } catch (error) {
      return (error as Error).name;
    }
  });

  expect(outcome).toBe('TypeError');
});
