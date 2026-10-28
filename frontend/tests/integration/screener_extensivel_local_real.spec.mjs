import { expect, test } from "@playwright/test";


test.skip(
  process.env.MSEN_REAL_SERVER !== "1",
  "Executado somente contra um servidor local real autorizado.",
);

test("Chrome executa e reconcilia a amostra real do novo funil", async ({ page }) => {
  await page.goto("/screener-extensivel.html");
  await page.locator("#botao-executar-extensivel").click();

  await expect(page.locator(".prototipo-nivel")).toHaveCount(3, { timeout: 30_000 });
  await expect(page.locator("#extensivel-total-analisado")).toHaveText("5.000");
  await expect(page.locator("#extensivel-total-excluido")).toHaveText("4.580");
  await expect(page.locator("#extensivel-total-aprovado")).toHaveText("420");
  await expect(page.locator("#extensivel-reconciliacao")).toContainText("Fechamento correto");
  await expect(page.locator("#extensivel-comparacao")).toContainText("anterior: 4.409");
  await expect(page.locator("#mensagem-extensivel")).toContainText("Amostra protegida reconciliada");
  await expect(page.locator("#botao-executar-extensivel")).toBeEnabled();

  const saldos = await page.locator(".prototipo-nivel summary span:last-child b").allTextContents();
  expect(saldos).toEqual(["2.001", "423", "420"]);
});
