import { expect, test } from '@playwright/test';

test('creates and inspects successful and failed executions', async ({ page }) => {
  const agentName = `e2e-agent-${Date.now()}`;

  await page.goto('/');
  await page.locator('#agent-name').fill(agentName);
  await page.getByRole('button', { name: 'Cadastrar agente' }).click();
  await expect(page.getByRole('heading', { name: agentName })).toBeVisible();

  await page.getByRole('button', { name: 'Rodar demo' }).click();
  await expect(page.getByRole('status')).toContainText('Demo concluída', { timeout: 15_000 });
  const completedTrace = page.locator('tr[data-link]').filter({ hasText: 'Concluído' }).first();
  await expect(completedTrace).toBeVisible();
  await completedTrace.click();
  await expect(page.getByRole('heading', { name: 'Timeline' })).toBeVisible();
  await expect(page.getByText('success', { exact: true })).toBeVisible();

  const agents = await page.request.get('/api/agents');
  const agent = (await agents.json()).items.find((item: { name: string }) => item.name === agentName);
  expect(agent).toBeTruthy();
  const failedDemo = await page.request.post(`/api/agents/${agent.agent_id}/demo?scenario=error`);
  expect(failedDemo.ok()).toBeTruthy();

  await page.goto('/');
  await expect(page.getByRole('table').getByText('Com erro', { exact: true })).toBeVisible();
  await page.getByLabel('Filtrar traces por status').selectOption('error');
  await expect(page.locator('tr[data-link]')).toHaveCount(1);
});
