import { expect, test } from '@playwright/test';

test('el chat responde con streaming, fuentes y feedback', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Abrir el asistente' }).click();
  const chat = page.getByRole('dialog');
  await chat.getByRole('button', { name: '¿Qué proyectos de IA ha desarrollado Rafael?' }).click();

  await expect(chat.getByText('AePTIC').first()).toBeVisible();
  await expect(chat.getByLabel('Fuentes consultadas')).toBeVisible();

  await chat.getByRole('button', { name: 'Respuesta útil' }).click();
});

test('rechaza preguntas fuera de dominio y ofrece contacto', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Abrir el asistente' }).click();
  const chat = page.getByRole('dialog');

  const input = chat.getByRole('textbox', { name: 'Escribe tu pregunta…' });
  await input.fill('¿Cuál es la capital de Francia?');
  await input.press('Enter');

  await expect(
    chat.getByRole('group', { name: 'Conversación' }).getByText(/No dispongo de esa información/),
  ).toBeVisible();
  await expect(chat.getByRole('link', { name: 'Usa el formulario de contacto' })).toBeVisible();
});

test('el tema oscuro persiste en el documento', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Activar tema oscuro' }).click();

  await expect(page.locator('html')).toHaveClass(/dark/);
  await expect(page.getByRole('button', { name: 'Activar tema claro' })).toBeVisible();
});

test('el formulario valida antes de enviar', async ({ page }) => {
  await page.goto('/#contact');
  await page.getByRole('button', { name: 'Enviar mensaje' }).click();

  const nameIsInvalid = await page
    .locator('#name')
    .evaluate((element) => !(element as HTMLInputElement).checkValidity());
  expect(nameIsInvalid).toBe(true);
});
