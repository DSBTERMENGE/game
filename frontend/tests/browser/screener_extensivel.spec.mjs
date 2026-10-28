import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";


const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
let servidor;

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const arquivos = {
      "/screener-extensivel.html": ["screener-extensivel.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/screener.css": ["css/screener.css", "text/css; charset=utf-8"],
      "/js/screener-extensivel.js": ["js/screener-extensivel.js", "text/javascript; charset=utf-8"],
      "/js/screener-extensivel-contrato.js": ["js/screener-extensivel-contrato.js", "text/javascript; charset=utf-8"],
      "/js/navegacao.js": ["js/navegacao.js", "text/javascript; charset=utf-8"],
    };
    const item = arquivos[new URL(requisicao.url, "http://127.0.0.1").pathname];
    if (!item) return resposta.writeHead(404).end();
    resposta.writeHead(200, { "Content-Type": item[1] });
    resposta.end(await readFile(path.join(raiz, item[0])));
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(4175, "127.0.0.1", resolver);
  });
});

test.afterAll(async () => {
  if (servidor) await new Promise((resolver) => servidor.close(resolver));
});

function filtros(prefixo, quantidade, entrada, totalExclusoes) {
  const exclusao = totalExclusoes / quantidade;
  return Array.from({ length: quantidade }, (_, indice) => ({
    codigo: `${prefixo}_${indice + 1}`, nome: `Filtro ${indice + 1}`, ordem: indice + 1,
    entrada: entrada - exclusao * indice, avaliacoes: entrada - exclusao * indice,
    exclusoes: exclusao, saldo: entrada - exclusao * (indice + 1),
    percentual_total_inicial: "2.000000", percentual_saldo_recebido: "2.000000",
  }));
}

const dados = {
  escopo: { tipo: "amostra", total_universo: 50063860, total_analisado: 5000, processamento_integral: false },
  resumo: { total_analisado: 5000, total_excluido: 1000, percentual_excluido: "20.000000", total_aprovado: 4000, percentual_aprovado: "80.000000", reconciliado: true },
  familias: [
    { codigo: "ESTATISTICA", nome: "Valores estatísticos", ordem: 1, entrada: 5000, exclusoes: 300, saldo: 4700, percentual_total_inicial: "6", percentual_saldo_recebido: "6", filtros: filtros("EST", 3, 5000, 300) },
    { codigo: "GEOMETRIA", nome: "Análise geométrica", ordem: 2, entrada: 4700, exclusoes: 500, saldo: 4200, percentual_total_inicial: "10", percentual_saldo_recebido: "10.638298", filtros: filtros("GEO", 5, 4700, 500) },
    { codigo: "PADROES", nome: "Padrões históricos", ordem: 3, entrada: 4200, exclusoes: 200, saldo: 4000, percentual_total_inicial: "4", percentual_saldo_recebido: "4.761905", filtros: filtros("PAD", 1, 4200, 200) },
  ],
  fechamento: { equacao: "total_analisado = total_excluido + total_aprovado", lado_esquerdo: 5000, lado_direito: 5000, valido: true },
};

test("renderiza contrato real em blocos expansíveis e compactos", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 820 });
  await page.route("**/api/screener/quadro-extensivel", (rota) => rota.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify({
      ...dados,
      comparacao: {
        anterior: { total_aprovado: 4409 }, novo: { total_aprovado: 4000 },
        diferenca_aprovadas: -409,
      },
    }),
  }));
  await page.goto("http://127.0.0.1:4175/screener-extensivel.html");
  await page.locator("#botao-executar-extensivel").click();

  await expect(page.locator(".prototipo-nivel")).toHaveCount(3);
  await expect(page.locator("#extensivel-total-universo")).toHaveText("50.063.860");
  await expect(page.locator("#extensivel-total-analisado")).toHaveText("5.000");
  await expect(page.locator("#extensivel-reconciliacao")).toContainText("Fechamento correto");
  await expect(page.locator("#extensivel-comparacao")).toContainText("anterior: 4.409");
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(0);
  await page.locator("#botao-abrir-todos").click();
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(3);
  await expect(page.locator(".prototipo-detalhes tbody tr")).toHaveCount(9);
  await expect(page.locator(".integracao-validada")).toHaveCount(9);
  const medidas = await page.locator("#extensivel-niveis").evaluate((elemento) => ({
    direita: elemento.getBoundingClientRect().right,
    inferior: elemento.getBoundingClientRect().bottom,
    largura: document.documentElement.clientWidth,
    altura: document.documentElement.clientHeight,
  }));
  expect(medidas.direita).toBeLessThanOrEqual(medidas.largura + 1);
  expect(medidas.inferior).toBeLessThanOrEqual(medidas.altura + 1);
});
