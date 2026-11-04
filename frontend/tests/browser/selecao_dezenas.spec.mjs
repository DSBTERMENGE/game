import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
let servidor;

const configuracao = {
  nome: "Seleção inicial", fator_k: "1.000000", fator_j: "0.000000",
  modo_quantidade: "MAX", quantidade_dezenas: null,
  horizonte_concursos: 1, versao_calculo: 1, assinatura_sha256: "a".repeat(64),
};
const detalhe = {
  id_alvo_selecao: 9, numero_concurso_alvo: 3070, numero_concurso_corte: 3069,
  situacao: "PENDENTE", dezenas_retornadas: [1, 7, 12, 23, 34, 55],
  quantidade_aprovada: 6, quantidade_retornada: 6, quantidade_acertos: null,
  quantidade_combinacoes_brutas: 1,
};

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const arquivos = {
      "/selecao-dezenas.html": ["selecao-dezenas.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/modal-andamento.css": ["css/modal-andamento.css", "text/css; charset=utf-8"],
      "/css/selecao-dezenas.css": ["css/selecao-dezenas.css", "text/css; charset=utf-8"],
      "/js/selecao-dezenas.js": ["js/selecao-dezenas.js", "text/javascript; charset=utf-8"],
      "/js/selecao-dezenas-controles.js": ["js/selecao-dezenas-controles.js", "text/javascript; charset=utf-8"],
      "/js/modal-andamento.js": ["js/modal-andamento.js", "text/javascript; charset=utf-8"],
      "/js/navegacao.js": ["js/navegacao.js", "text/javascript; charset=utf-8"],
    };
    const item = arquivos[new URL(requisicao.url, "http://127.0.0.1").pathname];
    if (!item) return resposta.writeHead(404).end();
    resposta.writeHead(200, { "Content-Type": item[1] });
    resposta.end(await readFile(path.join(raiz, item[0])));
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(4173, "127.0.0.1", resolver);
  });
});

test.afterAll(async () => {
  if (servidor) await new Promise((resolver) => servidor.close(resolver));
});

async function preparar(page) {
  await page.route("**/api/selecao-dezenas/configuracoes", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({ configuracoes: [{ id_configuracao_selecao: 1, configuracao }] }),
  }));
  await page.route("**/api/selecao-dezenas/previsoes", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      nova_previsao: { id_execucao_selecao: 8, concurso_corte: 3069, concurso_alvo_inicial: 3070, concurso_alvo_final: 3070 },
      conferencia: { previsoes_conferidas: 0 },
    }),
  }));
  await page.route("**/api/selecao-dezenas/previsoes/8/detalhes", (rota) => rota.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify({ detalhes: [detalhe] }),
  }));
  await page.goto("/selecao-dezenas.html");
  await expect(page.locator("#mensagem-selecao")).toContainText("1 configuração");
}

test("exibe previsão futura, parâmetros e resultado ainda pendente", async ({ page }) => {
  await preparar(page);
  await page.locator("#botao-atualizar-previsao").click();
  const celulas = page.locator("#corpo-previsoes tr").first().locator("td");
  await expect(celulas).toHaveCount(7);
  await expect(celulas.nth(2)).toHaveText("Aguardando resultado");
  await expect(celulas.nth(3)).toHaveText("01 · 07 · 12 · 23 · 34 · 55");
  await expect(celulas.nth(5)).toContainText("k 1; j 0; máximo aprovado");
});

test("consolida período, tamanho dos conjuntos e classes exclusivas do backtest", async ({ page }) => {
  await preparar(page);
  await page.route("**/api/selecao-dezenas/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      resultados: { primeiro: 1, ultimo: 3069, quantidade: 3069 },
      backtest: { concurso_inicial: 500, concurso_final: 3069, quantidade_alvos: 2570 },
      previsao_futura: { concurso_inicial: 3070, concurso_final: 3070 },
    }),
  }));
  await page.route("**/api/selecao-dezenas/backtests", (rota) => rota.fulfill({
    status: 202, contentType: "application/json",
    body: JSON.stringify({
      id: "tarefa", estado: "AGUARDANDO", etapa: "Aguardando início",
      concluido: 0, total: 1, percentual: 0, duracao_segundos: 0,
    }),
  }));
  await page.route("**/api/selecao-dezenas/execucoes/tarefa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      estado: "CONCLUIDA", etapa: "Concluída", concluido: 1, total: 1,
      percentual: 100, duracao_segundos: 1.2,
      resultado: { id_execucao_selecao: 12 },
    }),
  }));
  await page.route("**/api/selecao-dezenas/backtests/12/resumo", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      id_execucao_selecao: 12, primeiro_avaliado: 500, ultimo_avaliado: 3069,
      avaliados: 2570, nao_avaliaveis: 0, minimo_dezenas: 6, maximo_dezenas: 14,
      media_dezenas: "9.25", media_acertos_concurso: "2.10",
      classes: Array.from({ length: 7 }, (_, classe) => ({ classe, quantidade: classe + 1, percentual: 10 + classe })),
    }),
  }));
  await page.route("**/api/selecao-dezenas/backtests/12/detalhes", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({ detalhes: [{ ...detalhe, situacao: "AVALIADO", quantidade_acertos: 2 }] }),
  }));
  await page.locator("#form-backtest-selecao button[type=submit]").click();
  await expect(page.locator("#dialogo-previa-backtest")).toBeVisible();
  await expect(page.locator("#previa-backtest-quantidade")).toHaveText("2.570");
  await page.locator("#botao-confirmar-backtest").click();
  await expect(page.locator(".modal-andamento")).toBeVisible();
  await expect(page.locator(".modal-andamento__quantidade")).toHaveText("1 / 1 — 100%");
  await expect(page.locator(".modal-andamento__duracao")).toContainText("s");
  await expect(page.locator("#resumo-backtest")).toContainText("concursos 500 a 3069");
  await expect(page.locator("#resumo-backtest")).toContainText("conjuntos de 6 a 14 dezenas");
  await expect(page.locator("#classes-backtest .selecao-classe")).toHaveCount(7);
  await expect(page.locator("#corpo-detalhes-backtest tr")).toHaveCount(1);
});
