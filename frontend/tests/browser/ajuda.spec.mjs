import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const porta = Number(process.env.PLAYWRIGHT_TEST_PORT || 4173);
let servidor;

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    try {
      const url = new URL(requisicao.url, "http://127.0.0.1");
      const relativo = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
      if (relativo.includes("..")) return resposta.writeHead(400).end();
      const tipo = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css" }[path.extname(relativo)];
      const conteudo = await readFile(path.join(raiz, relativo));
      resposta.writeHead(200, { "Content-Type": `${tipo || "application/octet-stream"}; charset=utf-8` });
      resposta.end(conteudo);
    } catch {
      resposta.writeHead(404).end();
    }
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(porta, "127.0.0.1", resolver);
  });
});
test.afterAll(async () => {
  if (servidor) await new Promise((resolver) => servidor.close(resolver));
});


test("Ajuda navega, pesquisa e aceita link direto", async ({ page }) => {
  await page.goto("/ajuda.html#conceito-corte-historico");
  await expect(page.getByRole("heading", { name: "Corte histórico", exact: true })).toBeVisible();
  await expect(page.locator('a[href="#conceito-corte-historico"]')).toHaveAttribute("aria-current", "page");

  const busca = page.getByLabel("Localizar assunto");
  await busca.fill("executar 5000");
  await expect(page.locator("#ajuda-estado-busca")).toContainText(/assuntos? encontrados?/);
  await page.locator('#ajuda-resultados-busca a[href="#pagina-preparacao-screener"]').click();
  await expect(page.getByRole("heading", { name: "Preparação do Screener", exact: true })).toBeFocused();
  await expect(page).toHaveURL(/#pagina-preparacao-screener$/);

  await busca.fill("fator k fator j");
  await page.locator('#ajuda-resultados-busca a[href="#conceito-faixa-k-j"]').click();
  await expect(page.getByText(/centro_deslocado = U \+ μ \+ j × σ/)).toBeVisible();
  await expect(page.getByText(/aprovada quando LI ajustado ≤ CA ≤ LS ajustado/)).toBeVisible();

  await busca.fill("salvar estudo navegador");
  await page.locator('#ajuda-resultados-busca a[href="#pagina-distribuicoes"]').click();
  await expect(page.getByRole("heading", { name: "Distribuições", exact: true })).toBeFocused();
  await expect(page.getByText(/guarda essa configuração apenas neste navegador/)).toBeVisible();
});

test("Ajuda permanece utilizável em tela estreita e trata tópico ausente", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/ajuda.html#topico-inexistente");
  await expect(page.getByText("O tópico solicitado não foi encontrado.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "O que é o Game", exact: true })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Índice da Ajuda" })).toBeVisible();
  await expect(page.getByLabel("Localizar assunto")).toBeVisible();
});

test("Ajuda contextual preserva retorno seguro à página de origem", async ({ page }) => {
  await page.goto("/ajuda.html?origem=%2Ffrequencias.html%3Fdezena%3D17%23evolucao-historica-dezena#pagina-frequencia-dezenas");
  await expect(page.getByRole("heading", { name: "Frequência das dezenas", exact: true })).toBeVisible();
  const retorno = page.getByRole("link", { name: "Voltar para Frequência das dezenas" });
  await expect(retorno).toHaveAttribute("href", "/frequencias.html?dezena=17#evolucao-historica-dezena");

  await page.goto("/ajuda.html?origem=https%3A%2F%2Fexemplo.com%2Ffrequencias.html#pagina-frequencia-dezenas");
  await expect(page.locator("#ajuda-voltar-origem")).toBeHidden();
});

test("tópicos contextuais de páginas e gráficos possuem destinos válidos", async ({ page }) => {
  for (const [id, titulo] of [
    ["pagina-frequencia-dezenas", "Frequência das dezenas"],
    ["pagina-graficos-frequencia", "Gráficos de frequência"],
    ["pagina-graficos-frequencia-evolucao", "Evolução dos intervalos"],
    ["pagina-graficos-frequencia-distribuicao", "Curva de distribuição dos intervalos"],
    ["pagina-graficos-frequencia-ordenado", "Ocorrências em ordem crescente"],
    ["pagina-selecao-dezenas", "Seleção de dezenas"],
    ["pagina-gestao-desenvolvimento", "Gestão do desenvolvimento"],
  ]) {
    await page.goto(`/ajuda.html#${id}`);
    await expect(page.getByRole("heading", { name: titulo, exact: true })).toBeVisible();
  }
});

