import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
let servidor;

const configuracao = {
  nome: "Estudo acumulado inicial", concurso_inicial: 1, tamanho_inicial: 500,
  regra_janela: "INICIO_FIXO_FINAL_EXPANSIVO", tipo_evento: "TODOS",
  metodo_faixa: "MEDIA_MAIS_MENOS_DESVIO_PADRAO", parametro_faixa: "1.000000",
  unidade_parametro: "MULTIPLICADOR_DESVIO_PADRAO",
  regra_arredondamento: "LIMITES_EXTERNOS", versao_calculo: 1,
  assinatura_sha256: "a".repeat(64),
};
const estado = {
  configuracao_ativa: configuracao,
  resultados: { quantidade: 3069, concurso_inicial: 1, concurso_final: 3069 },
  geracao_ativa: { estado: "ATIVA", concurso_inicial: 1, concurso_final: 3069 },
  linhas_historicas: 462600,
};
const dezenas = Array.from({ length: 60 }, (_, indice) => ({
  dezena: indice + 1, quantidade_ocorrencias: 30 + indice,
  quantidade_intervalos: 29 + indice, intervalo_minimo: 1,
  intervalo_maximo: 20 + indice, media_intervalos: String(5 + indice / 10),
  mediana_intervalos: String(5 + indice / 10),
  desvio_padrao_intervalos: String(1 + indice / 100),
}));

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const arquivos = {
      "/frequencias.html": ["frequencias.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/modal-andamento.css": ["css/modal-andamento.css", "text/css; charset=utf-8"],
      "/css/frequencias.css": ["css/frequencias.css", "text/css; charset=utf-8"],
      "/js/frequencias.js": ["js/frequencias.js", "text/javascript; charset=utf-8"],
      "/js/frequencia-graficos.js": ["js/frequencia-graficos.js", "text/javascript; charset=utf-8"],
      "/js/frequencia-historico.js": ["js/frequencia-historico.js", "text/javascript; charset=utf-8"],
      "/js/frequencia-controles.js": ["js/frequencia-controles.js", "text/javascript; charset=utf-8"],
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
  await page.route("**/api/frequencias/estado", (rota) => rota.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify(estado),
  }));
  await page.route("**/api/frequencias/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({ modo: "SEM_ALTERACAO", concursos_novos: [], divergencias_configuracao: [] }),
  }));
  await page.route("**/api/frequencias/fotografia-atual?*", (rota) => {
    const tipo = new URL(rota.request().url()).searchParams.get("tipo_evento");
    return rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({
        tipo_evento: tipo, unidade_intervalos: "CONCURSOS",
        concurso_inicial: 1, concurso_final: 3069, quantidade_resultados: 3069,
        atualizado_em: "2026-10-30T12:00:00+00:00", dezenas,
      }),
    });
  });
  await page.route("**/api/frequencias/serie?*", (rota) => {
    const consulta = new URL(rota.request().url()).searchParams;
    const inicio = Number(consulta.get("concurso_inicial"));
    const fim = Number(consulta.get("concurso_final"));
    const pontos = Array.from({ length: fim - inicio + 1 }, (_, indice) => ({
      numero_do_concurso: inicio + indice, quantidade_ocorrencias: 20 + indice,
      quantidade_intervalos: 19 + indice, intervalo_minimo: 2,
      intervalo_maximo: 30, media_intervalos: "12.000000",
      mediana_intervalos: "11.000000", desvio_padrao_intervalos: "3.000000",
      previsao_central: String(inicio + indice + 12),
      limite_inferior_exato: String(inicio + indice + 9),
      limite_superior_exato: String(inicio + indice + 15),
      concurso_limite_inferior: inicio + indice + 9,
      concurso_limite_superior: inicio + indice + 15,
    }));
    const avaliacoes = pontos.map((ponto, indice) => ({
      numero_do_concurso: ponto.numero_do_concurso,
      estado: indice === 3 ? "ERRO_ACIMA" : (indice === pontos.length - 1 ? "CENSURADO" : "ACERTO"),
      concurso_anterior: ponto.numero_do_concurso - 5,
      concurso_real: ponto.numero_do_concurso + (indice === 3 ? 20 : 12),
      limite_inferior: ponto.concurso_limite_inferior,
      limite_superior: ponto.concurso_limite_superior,
      previsao_central: ponto.previsao_central,
      erro_absoluto: indice === pontos.length - 1 ? null : (indice === 3 ? "8" : "0"),
      erro_percentual: indice === pontos.length - 1 ? null : (indice === 3 ? "32" : "0"),
    }));
    return rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({
        dezena: Number(consulta.get("dezena")), tipo_evento: consulta.get("tipo_evento"),
        total: pontos.length, periodo: { concurso_inicial: inicio, concurso_final: fim },
        ocorrencias_reais: [inicio + 1, inicio + 4], pontos,
        assertividade: {
          regra_denominador: "INTERVALO_REAL_ENTRE_EVENTOS", limites_inclusivos: true,
          total: pontos.length, avaliaveis: pontos.length - 1, acertos: pontos.length - 2,
          erros: 1, censurados: 1, percentual_acerto: "90",
          erro_absoluto_medio: "0.8", erro_percentual_medio: "3.2", avaliacoes,
        },
      }),
    });
  });
  await page.goto("/frequencias.html");
  await expect(page.locator("#mensagem-frequencias")).toHaveText("Estado da frequência carregado.");
}

test("carrega estado, configurações e executa simulação com progresso", async ({ page }) => {
  await preparar(page);
  await expect(page.locator("#resumo-resultados")).toHaveText("3.069");
  await expect(page.locator("#resumo-ultimo-processado")).toHaveText("3.069");
  await expect(page.locator("#resumo-linhas")).toHaveText("462.600");
  await expect(page.locator("#frequencia-salvar-dados")).toBeChecked();
  await expect(page.locator(".frequencias-grafico-cartao")).toHaveCount(6);
  await expect(page.locator(".grafico-frequencia-barra")).toHaveCount(360);
  await page.locator("#frequencia-tipo-grafico").selectOption("2VS");
  await expect(page.locator("#mensagem-graficos-frequencia")).toContainText("Fotografia 2VS");
  await page.locator("#historico-concurso-inicial").fill("500");
  await page.locator("#historico-concurso-final").fill("510");
  await page.locator("#botao-consultar-historico").click();
  await expect(page.locator(".historico-cartao")).toHaveCount(2);
  await expect(page.locator(".historico-ocorrencia")).toHaveCount(2);
  await expect(page.locator("#mensagem-historico-frequencia")).toContainText("11 pontos");
  await expect(page.locator("#assertividade-avaliaveis")).toHaveText("10");
  await expect(page.locator("#assertividade-erros")).toHaveText("1");
  await expect(page.locator("#corpo-erros-assertividade tr")).toHaveCount(1);

  await page.locator("#frequencia-salvar-dados").uncheck();
  await page.route("**/api/frequencias/execucoes", (rota) => rota.fulfill({
    status: 202, contentType: "application/json",
    body: JSON.stringify({ id: "teste", estado: "AGUARDANDO", etapa: "Aguardando", concluido: 0, total: 1, percentual: 0 }),
  }));
  await page.route("**/api/frequencias/execucoes/teste", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({ id: "teste", estado: "CONCLUIDA", etapa: "Concluída", concluido: 1, total: 1, percentual: 100, resultado: { tipo: "SIMULACAO", linhas_calculadas: 462600 } }),
  }));
  await page.locator("#botao-executar-frequencia").click();
  await expect(page.locator(".modal-andamento__resultado")).toContainText("Simulação concluída sem gravação");
});

for (const largura of [1280, 520]) {
  test(`página permanece utilizável no Chrome com ${largura}px`, async ({ page }) => {
    await page.setViewportSize({ width: largura, height: 800 });
    await preparar(page);
    const medidas = await page.locator("main").evaluate((elemento) => ({
      direita: elemento.getBoundingClientRect().right,
      largura: document.documentElement.clientWidth,
      rolagemPagina: elemento.scrollHeight >= elemento.clientHeight,
    }));
    expect(medidas.direita).toBeLessThanOrEqual(medidas.largura + 1);
    expect(medidas.rolagemPagina).toBeTruthy();
    await expect(page.locator("#botao-executar-frequencia")).toBeVisible();
  });
}
