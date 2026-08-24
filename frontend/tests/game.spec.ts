import { expect, test } from '@playwright/test';

test('two players can create and join a game', async ({ browser }) => {
  const contextA = await browser.newContext();
  const contextB = await browser.newContext();
  const pageA = await contextA.newPage();
  const pageB = await contextB.newPage();

  await pageA.goto('/');
  await pageA.getByLabel('Player name').fill('Alice');
  await pageA.getByRole('button', { name: 'Create game' }).click();

  await expect(pageA.getByText(/Lobby:/)).toBeVisible();
  const titleText = await pageA.locator('h2').textContent();
  const codeMatch = titleText?.match(/Lobby:\s*([A-Z0-9]+)/);
  const code = codeMatch?.[1];
  expect(code).toBeTruthy();

  await pageB.goto('/');
  await pageB.getByLabel('Player name').fill('Bob');
  await pageB.getByLabel('Join code').fill(code ?? '');
  await pageB.getByRole('button', { name: 'Join game' }).click();

  await expect(pageA.getByText('Lobby:')).toBeVisible();
  await expect(pageB.getByText('Game:')).toBeVisible();
});
