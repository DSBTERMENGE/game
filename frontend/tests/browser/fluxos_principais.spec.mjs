import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";


const resultados = [
  {
    id_resultado: 1,
    numero_ap: 1,
    data_resultado: "1996-03-11",
    dezenas: [4, 5, 30, 33, 41, 52],
  },
  {
    id_resultado: 2,
    numero_ap: 2,
    data_resultado: "1996-03-18",
    dezenas: [9, 37, 39, 41, 43, 49],
  },
];
const raizFrontend = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
let servidor;


test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const caminhos = {
      "/": ["index.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/js/main.js": ["js/main.js", "text/javascript; charset=utf-8"],
    };
    const recurso = caminhos[requisicao.url];
    if (!recurso) {
      resposta.writeHead(404).end();
      return;
    }
    resposta.writeHead(200, { "Content-Type": recurso[1] });
    resposta.end(await readFile(path.join(raizFrontend, recurso[0])));
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(4173, "127.0.0.1", resolver);
  });
});


test.afterAll(async () => {
  await new Promise((resolver, rejeitar) => {
    servidor.close((erro) => (erro ? rejeitar(erro) : resolver()));
  });
});


async function simularApi(page) {
  let importacoes = 0;
  await page.route("**/api/resultados", async (rota) => {
    await rota.fulfill({ json: { resultados, total: resultados.length } });
  });
  await page.route("**/api/resultados/importar", async (rota) => {
    importacoes += 1;
    await rota.fulfill({
      json: {
        mensagem: "Importação concluída: 0 resultado(s) inserido(s).",
        relatorio: { inseridas: 0, iguais: 2, alteradas: 0, invalidas: 0 },
      },
    });
  });
  return () => importacoes;
}


test("carrega, desenha, seleciona e navega circularmente", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");

  await expect(page.locator("#mensagem-sistema")).toHaveText("2 resultados carregados.");
  await expect(page.locator("#seletor-resultado option")).toHaveCount(2);
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await expect(page.locator("circle.marca-resultado")).toHaveCount(6);
  await expect(page.locator("circle.marca-media")).toHaveCount(1);

  await page.locator("#botao-anterior").click();
  await expect(page.locator("#jogo-numero")).toHaveText("2");
  await page.locator("#botao-proximo").click();
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await page.locator("#seletor-resultado").selectOption("1");
  await expect(page.locator("#jogo-numero")).toHaveText("2");
});


test("inicia, avança e pausa o voo", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");
  await page.locator("#tempo-voo").fill("0.1");
  await page.locator("#botao-voo").click();

  await expect(page.locator("#botao-voo")).toHaveText("Pausar voo dos pássaros");
  await expect(page.locator("#jogo-numero")).toHaveText("2", { timeout: 1_000 });
  await page.locator("#botao-voo").click();
  await expect(page.locator("#botao-voo")).toHaveText("Iniciar voo dos pássaros");
  await expect(page.locator("#mensagem-sistema")).toHaveText("Voo interrompido.");
});


test("seleciona Excel, importa, desenha mancha e limpa", async ({ page }) => {
  const totalImportacoes = await simularApi(page);
  await page.goto("/");
  const planilha = path.resolve("MSen/tests/fixtures/resultados_validos.xlsx");

  await page.locator("#arquivo-excel").setInputFiles(planilha);
  await expect(page.locator("#nome-arquivo")).toHaveText("resultados_validos.xlsx");
  await expect(page.locator("#botao-importar-excel")).toBeEnabled();
  await page.locator("#botao-importar-excel").click();
  await expect.poll(totalImportacoes).toBe(1);
  await expect(page.locator("#mensagem-sistema")).toHaveText(
    "Importação concluída: 0 inseridos, 2 iguais, 0 alterados e 0 inválidos.",
  );

  await page.locator("#botao-mancha").click();
  await expect(page.locator("circle.marca-mancha-resultado")).toHaveCount(12);
  await expect(page.locator("circle.marca-mancha-media")).toHaveCount(2);
  await expect(page.locator("#jogo-numero")).toHaveText("Todos");

  await page.locator("#botao-limpar").click();
  await expect(page.locator("#camada-marcas circle")).toHaveCount(0);
  await expect(page.locator("#mensagem-sistema")).toHaveText("Gráfico limpo.");
});
