import { test, expect, type Route } from '@playwright/test';

/**
 * Vet panel "Re-send invitation" flow.
 *
 * The prod build served here points its `apiUrl` at the live backend, so every
 * spec mocks the API with `page.route` — these tests prove the *frontend* wiring
 * (button visibility gated on `pending`, its position left of the status, the
 * POST it fires, the success banner), not that any email is actually delivered.
 * Whether mail leaves the server is a backend/Resend concern, unreachable from
 * a browser test.
 */

/** A JWT the frontend can decode (payload only — the signature is never verified client-side). */
function fakeVetToken(): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(
    JSON.stringify({ sub: '1', role: 'vet', exp: Math.floor(Date.now() / 1000) + 3600 }),
  );
  return `${header}.${payload}.signature`;
}

const PANEL_WITH_PENDING = {
  clients: [
    { id: 7, email: 'pending@example.com', full_name: 'Pending Owner', status: 'pending' },
    { id: 8, email: 'active@example.com', full_name: 'Active Owner', status: 'active' },
  ],
  dogs: [],
};

test.beforeEach(async ({ page, baseURL }) => {
  const token = fakeVetToken();
  await page.addInitScript((value) => {
    localStorage.setItem('token', value);
  }, token);

  // `http-server` has no SPA fallback, so a deep link like /vet/panel 404s.
  // Serve the app's index.html for it; Angular's router then reads the path.
  await page.route('**/vet/panel', async (route: Route) => {
    if (route.request().resourceType() !== 'document') {
      await route.continue();
      return;
    }
    const index = await route.fetch({ url: `${baseURL}/` });
    await route.fulfill({ response: index });
  });

  await page.route('**/vets/panel', async (route: Route) => {
    await route.fulfill({ json: PANEL_WITH_PENDING });
  });
});

test('re-send button shows only for pending clients, to the left of the status', async ({
  page,
}) => {
  await page.goto('/vet/panel');

  const pendingRow = page.locator('.client-row', { hasText: 'Pending Owner' });
  const activeRow = page.locator('.client-row', { hasText: 'Active Owner' });

  // Pending client: the button exists and precedes the status badge in the DOM.
  const resendButton = pendingRow.locator('button.btn-resend');
  await expect(resendButton).toBeVisible();
  await expect(pendingRow.locator('.client-actions > *').first()).toHaveClass(/btn-resend/);

  // Active client: no re-send button (nothing to re-send once accepted).
  await expect(activeRow.locator('button.btn-resend')).toHaveCount(0);
});

test('clicking re-send POSTs to the resend endpoint and shows a success banner', async ({
  page,
}) => {
  let resendUrl: string | null = null;
  await page.route('**/vets/clients/*/resend', async (route: Route) => {
    resendUrl = route.request().url();
    expect(route.request().method()).toBe('POST');
    await route.fulfill({
      json: { id: 7, email: 'pending@example.com', full_name: 'Pending Owner', status: 'pending' },
    });
  });

  await page.goto('/vet/panel');

  const pendingRow = page.locator('.client-row', { hasText: 'Pending Owner' });
  await pendingRow.locator('button.btn-resend').click();

  await expect(page.locator('.success')).toHaveText(/re-sent to pending@example.com/i);
  expect(resendUrl).toMatch(/\/vets\/clients\/7\/resend$/);
});
