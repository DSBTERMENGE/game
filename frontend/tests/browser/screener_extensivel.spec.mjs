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
      "/screener.html": ["screener.html", "text/html; charset=utf-8"],
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

function padrao(codigo, estado, avaliacoes = 0, exclusoes = 0, saldo = null) {
  return {
    padrao_cod: codigo, padrao_nome: `Padrão ${codigo}`, num_ocorrencias: 1,
    total_sorteios: 100, percentual_ocorrencia: "1.000000",
    limite_percentual: "10.000000", operador: "<", estado,
    avaliacoes, correspondencias: exclusoes, exclusoes, saldo,
  };
}

const dados = {
  escopo: { tipo: "amostra", total_universo: 50063860, total_analisado: 5000, processamento_integral: false },
  resumo: { total_analisado: 5000, total_excluido: 1000, percentual_excluido: "20.000000", total_aprovado: 4000, percentual_aprovado: "80.000000", reconciliado: true },
  familias: [
    { codigo: "ESTATISTICA", nome: "Valores estatísticos", ordem: 1, entrada: 5000, exclusoes: 300, saldo: 4700, percentual_total_inicial: "6", percentual_saldo_recebido: "6", filtros: filtros("EST", 3, 5000, 300) },
    { codigo: "GEOMETRIA", nome: "Análise geométrica", ordem: 2, entrada: 4700, exclusoes: 500, saldo: 4200, percentual_total_inicial: "10", percentual_saldo_recebido: "10.638298", filtros: filtros("GEO", 5, 4700, 500) },
    { codigo: "PADROES", nome: "Padrões históricos", ordem: 3, entrada: 4200, exclusoes: 200, saldo: 4000, percentual_total_inicial: "4", percentual_saldo_recebido: "4.761905", filtros: [
      { ...filtros("PAD_PD_002", 1, 4200, 200)[0], codigo: "PAD_PD_002" },
      { ...filtros("PAD_PD_003", 1, 4000, 0)[0], codigo: "PAD_PD_003" },
      { ...filtros("PAD_PD_005", 1, 4000, 0)[0], codigo: "PAD_PD_005" },
      { ...filtros("PAD_PD_006", 1, 4000, 0)[0], codigo: "PAD_PD_006" },
      { ...filtros("PAD_PD_009", 1, 4000, 0)[0], codigo: "PAD_PD_009" },
    ] },
  ],
  fechamento: { equacao: "total_analisado = total_excluido + total_aprovado", lado_esquerdo: 5000, lado_direito: 5000, valido: true },
  detalhes_padroes: {
    limite_percentual: "10.000000", operador: "<",
    grupos: [
      { grupo_cod: "PG_001", grupo_nome: "Sequenciais", entrada: 4200, exclusoes: 200, saldo: 4000, reconciliado: true,
        padroes: [padrao("PD_002", "APLICADO_RARO", 4200, 200, 4000), padrao("PD_003", "APLICADO_RARO", 4000, 0, 4000)] },
      { grupo_cod: "PG_002", grupo_nome: "Colunas", entrada: 4000, exclusoes: 0, saldo: 4000, reconciliado: true,
        padroes: [padrao("PD_005", "APLICADO_RARO", 4000, 0, 4000), padrao("PD_006", "APLICADO_RARO", 4000, 0, 4000)] },
      { grupo_cod: "PG_003", grupo_nome: "Linhas", entrada: 4000, exclusoes: 0, saldo: 4000, reconciliado: true,
        padroes: [padrao("PD_009", "APLICADO_RARO", 4000, 0, 4000)] },
    ],
    fechamento: { entrada: 4200, exclusoes: 200, saldo: 4000, valido: true },
  },
  configuracao_raridade: {
    limite_percentual: "10.000000", operador: "<",
    padroes_selecionados: ["PD_002", "PD_003", "PD_005", "PD_006", "PD_009"],
  },
};

test("renderiza contrato real em blocos expansíveis e compactos", async ({ page }) => {
  let limiteRecebido;
  await page.setViewportSize({ width: 1280, height: 820 });
  await page.route("**/api/screener/quadro", async (rota) => {
    limiteRecebido = rota.request().postDataJSON().limite_raridade;
    await new Promise((resolver) => setTimeout(resolver, 150));
    const respostaDados = structuredClone(dados);
    const limiteFormatado = Number(limiteRecebido).toFixed(6);
    respostaDados.configuracao_raridade.limite_percentual = limiteFormatado;
    respostaDados.detalhes_padroes.limite_percentual = limiteFormatado;
    respostaDados.detalhes_padroes.grupos.forEach((grupo) => grupo.padroes.forEach((padrao) => {
      padrao.limite_percentual = limiteFormatado;
    }));
    return rota.fulfill({
      status: 200, contentType: "application/json", body: JSON.stringify({
        ...respostaDados,
        comparacao: {
          anterior: { total_aprovado: 4409 }, novo: { total_aprovado: 4000 },
          diferenca_aprovadas: -409,
        },
      }),
    });
  });
  await page.goto("http://127.0.0.1:4175/screener.html");
  await expect(page.locator("#botao-abrir-todos")).toBeDisabled();
  await expect(page.locator("#botao-fechar-todos")).toBeDisabled();
  await page.locator("#limite-raridade-extensivel").fill("7.5");
  await page.locator("#botao-executar-extensivel").click();
  await expect(page.locator("#mensagem-extensivel")).toContainText("Executando 5.000");
  await expect(page.locator("#botao-executar-extensivel")).toBeDisabled();
  await expect(page.locator("#botao-abrir-todos")).toBeDisabled();
  expect(limiteRecebido).toBe("7.5");

  await expect(page.locator(".prototipo-nivel")).toHaveCount(3);
  await expect(page.locator("#extensivel-total-universo")).toHaveText("50.063.860");
  await expect(page.locator("#extensivel-total-analisado")).toHaveText("5.000");
  await expect(page.locator("#extensivel-reconciliacao")).toContainText("Fechamento correto");
  await expect(page.locator("#extensivel-comparacao")).toContainText("anterior: 4.409");
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(0);
  await expect(page.locator("#botao-abrir-todos")).toBeEnabled();
  await expect(page.locator("#botao-fechar-todos")).toBeEnabled();
  await page.locator("#botao-abrir-todos").click();
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(3);
  await expect(page.locator(".prototipo-detalhes > table > tbody > tr")).toHaveCount(13);
  await expect(page.locator(".integracao-validada")).toHaveCount(13);
  await expect(page.locator(".prototipo-nivel--padroes > .prototipo-detalhes > table tbody tr").first().locator("td").first()).toContainText("PD_002 · Padrão PD_002 | PG_001 · Sequenciais");
  await expect(page.locator(".padrao-grupo")).toHaveCount(3);
  await page.locator(".padrao-grupo").first().locator("summary").click();
  await expect(page.locator(".padrao-grupo").first().locator("tbody tr")).toHaveCount(2);
  await expect(page.locator(".padrao-aplicado")).toHaveCount(5);
  await expect(page.locator(".padrao-nao-aplicado")).toHaveCount(0);
  await expect(page.locator("#extensivel-raridade-usada")).toContainText("PD_002, PD_003, PD_005, PD_006, PD_009");
  await expect(page.locator("#extensivel-raridade-usada")).toContainText("7,500000%");
  expect(await page.evaluate(() => localStorage.getItem("msen.screener.limiteRaridade"))).toBe("7.500000");
  await page.unroute("**/api/screener/quadro");
  await page.route("**/api/screener/quadro", (rota) => rota.fulfill({
    status: 503,
    contentType: "application/json",
    body: JSON.stringify({ erro: { mensagem: "Falha posterior controlada." } }),
  }));
  await page.locator("#botao-executar-extensivel").click();
  await expect(page.locator("#mensagem-extensivel")).toContainText("Falha posterior controlada");
  await expect(page.locator("#botao-abrir-todos")).toBeEnabled();
  await expect(page.locator("#botao-fechar-todos")).toBeEnabled();
  const medidas = await page.locator("#extensivel-niveis").evaluate((elemento) => ({
    direita: elemento.getBoundingClientRect().right,
    inferior: elemento.getBoundingClientRect().bottom,
    largura: document.documentElement.clientWidth,
    altura: document.documentElement.clientHeight,
  }));
  expect(medidas.direita).toBeLessThanOrEqual(medidas.largura + 1);
  expect(medidas.inferior).toBeLessThanOrEqual(medidas.altura + 1);
});

test("falha mantém detalhes indisponíveis quando não existe execução carregada", async ({ page }) => {
  await page.route("**/api/screener/quadro", (rota) => rota.fulfill({
    status: 503,
    contentType: "application/json",
    body: JSON.stringify({ erro: { mensagem: "Serviço temporariamente indisponível." } }),
  }));
  await page.goto("http://127.0.0.1:4175/screener.html");
  await page.locator("#botao-executar-extensivel").click();
  await expect(page.locator("#mensagem-extensivel")).toContainText(
    "Não foi possível concluir a execução: Serviço temporariamente indisponível.",
  );
  await expect(page.locator("#botao-executar-extensivel")).toBeEnabled();
  await expect(page.locator("#limite-raridade-extensivel")).toBeEnabled();
  await expect(page.locator("#botao-abrir-todos")).toBeDisabled();
  await expect(page.locator("#botao-fechar-todos")).toBeDisabled();
});
