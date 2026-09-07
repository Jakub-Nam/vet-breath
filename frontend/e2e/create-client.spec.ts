import { test, expect, type Route } from '@playwright/test';

/**
 * Vet panel "Add client" flow: the vet creates a client account directly with a
 * password (no invitation email). The backend is mocked — these tests prove the
 * frontend wiring: the form reveals, password-match is enforced client-side, and a
 * valid submit POSTs {email, full_name, password} to /vets/clients.
 */

/** A JWT the frontend can decode (payload only — the signature is never verified client-side). */
function fakeVetToken(): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(
    JSON.stringify({ sub: '1', role: 'vet', exp: Math.floor(Date.now() / 1000) + 3600 }),
  );
  return `${header}.${payload}.signature`;
}

const EMPTY_PANEL = { clients: [], dogs: [] };

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
    await route.fulfill({ json: EMPTY_PANEL });
  });
});

test('mismatched passwords are rejected client-side without any request', async ({ page }) => {
  let created = false;
  await page.route('**/vets/clients', async (route: Route) => {
    created = true;
    await route.fulfill({ status: 201, json: {} });
  });

  await page.goto('/vet/panel');
  await page.getByRole('button', { name: '+ Add client' }).click();

  await page.getByPlaceholder('Client email').fill('newclient@example.com');
  await page.getByPlaceholder('Password', { exact: true }).fill('secret123');
  await page.getByPlaceholder('Repeat password').fill('different');
  await page.getByRole('button', { name: 'Create client account' }).click();

  await expect(page.locator('.error')).toHaveText(/passwords do not match/i);
  expect(created).toBe(false);
});

test('matching passwords POST the new client account and show success', async ({ page }) => {
  let requestBody: Record<string, unknown> | null = null;
  await page.route('**/vets/clients', async (route: Route) => {
    expect(route.request().method()).toBe('POST');
    requestBody = route.request().postDataJSON();
    await route.fulfill({
      status: 201,
      json: {
        id: 1,
        email: 'newclient@example.com',
        full_name: 'New Client',
        status: 'active',
      },
    });
  });

  await page.goto('/vet/panel');
  await page.getByRole('button', { name: '+ Add client' }).click();

  await page.getByPlaceholder('Client email').fill('newclient@example.com');
  await page.getByPlaceholder('Client name (optional)').fill('New Client');
  await page.getByPlaceholder('Password', { exact: true }).fill('secret123');
  await page.getByPlaceholder('Repeat password').fill('secret123');
  await page.getByRole('button', { name: 'Create client account' }).click();

  await expect(page.locator('.success')).toHaveText(/account created for newclient@example.com/i);
  expect(requestBody).toEqual({
    email: 'newclient@example.com',
    full_name: 'New Client',
    password: 'secret123',
  });
});
