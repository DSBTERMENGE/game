import { test, expect } from "@playwright/test";


test("Backtest completo usa dados reais e apresenta o relatório gráfico", async ({ page }) => {
  await page.goto("/selecao-dezenas.html");

  const configuracao = page.locator("#backtest-configuracao");
  await expect(configuracao.locator("option")).toHaveCount(3);
  await configuracao.selectOption("3");
  await expect(configuracao.locator("option:checked")).toContainText("k=0.5, j=0");
  await expect(page.locator("#backtest-inicial")).toHaveValue("500");

  await page.locator("#botao-gerar-backtest").click();
  const previa = page.locator("#dialogo-previa-backtest");
  await expect(previa).toBeVisible();
  await expect(page.locator("#previa-backtest-periodo")).toHaveText("500 a 3069");
  await expect(page.locator("#previa-backtest-quantidade")).toHaveText("2.570");

  await page.locator("#botao-confirmar-backtest").click();
  const relatorio = page.locator("#relatorio-backtest");
  await expect(relatorio).toBeVisible({ timeout: 30_000 });
  await expect(page.locator("#periodo-backtest")).toContainText("Configuração_k=0.5, j=0");
  await expect(page.locator("#periodo-backtest")).toContainText("concursos 500 a 3069");
  await expect(page.locator("#resumo-backtest")).toContainText("Testes efetuados");
  await expect(page.locator("#classes-backtest .selecao-classe")).toHaveCount(7);
  await expect(page.locator("#grafico-backtest-quantidade path")).not.toHaveCount(0);
  await expect(page.locator("#grafico-backtest-acertos path")).not.toHaveCount(0);
  await expect(page.locator("#estado-backtest")).toContainText("Relatório concluído e exibido abaixo");
});

test("aceita início posterior a 500 e mantém o último concurso automático", async ({ page }) => {
  await page.goto("/selecao-dezenas.html");
  await page.locator("#backtest-configuracao").selectOption("2");
  await page.locator("#backtest-inicial").fill("2500");
  await page.locator("#botao-gerar-backtest").click();

  await expect(page.locator("#previa-backtest-configuracao")).toHaveText("Configuração_k=1, j=0");
  await expect(page.locator("#previa-backtest-periodo")).toHaveText("2500 a 3069");
  await expect(page.locator("#previa-backtest-quantidade")).toHaveText("570");

  await page.locator("#botao-confirmar-backtest").click();
  await expect(page.locator("#relatorio-backtest")).toBeVisible({ timeout: 30_000 });
  await expect(page.locator("#periodo-backtest")).toContainText("concursos 2500 a 3069");
  await expect(page.locator("#resumo-backtest")).toContainText("570");
});
