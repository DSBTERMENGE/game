import { expect, test } from "@playwright/test";


test.skip(
  process.env.MSEN_REAL_SERVER !== "1",
  "Executado somente contra um servidor local real autorizado.",
);

test("Chrome exibe as distribuições reais e calcula a prévia", async ({ page }) => {
  await page.goto("/distribuicoes.html");
  await expect(page.locator("#mensagem-distribuicoes")).toHaveText(
    "Perfis históricos carregados.",
    { timeout: 30_000 },
  );
  await expect(page.locator(".cartao-distribuicao")).toHaveCount(10);
  await expect(page.locator("#resumo-amostra")).toHaveText("3.069");
  await expect(page.locator(".screener-inativo")).toContainText("screener inativo");

  await page.locator("#botao-configurar-faixas").click();
  await page.locator("#config-metodo-faixa").selectOption("percentual_media");
  await page.locator("#config-margem-inferior").fill("10");
  await page.locator("#config-margem-superior").fill("20");
  await page.locator("#botao-calcular-previa").click();
  await expect(page.locator("#corpo-previa-faixas tr")).toHaveCount(10, {
    timeout: 30_000,
  });
  await expect(page.locator("#mensagem-previa")).toContainText("Prévia calculada");
  await expect(page.locator("#botao-salvar-configuracao")).toBeEnabled();

  const ativacao = await page.request.get("/api/perfis/distribuicoes");
  const corpo = await ativacao.json();
  expect(corpo.distribuicoes.ativa_no_screener).toBeFalsy();
  expect(corpo.distribuicoes.janela.quantidade_resultados).toBe(3069);
});
