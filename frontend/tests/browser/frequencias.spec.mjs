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
  geracao_ativa: {
    estado: "ATIVA", concurso_inicial: 1, concurso_final: 3069,
    concluida_em: "2026-10-30T12:00:00+00:00",
  },
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
      "/graficos-frequencias.html": ["graficos-frequencias.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/modal-andamento.css": ["css/modal-andamento.css", "text/css; charset=utf-8"],
      "/css/frequencias.css": ["css/frequencias.css", "text/css; charset=utf-8"],
      "/css/graficos-frequencias.css": ["css/graficos-frequencias.css", "text/css; charset=utf-8"],
      "/js/frequencias.js": ["js/frequencias.js", "text/javascript; charset=utf-8"],
      "/js/graficos-frequencias.js": ["js/graficos-frequencias.js", "text/javascript; charset=utf-8"],
      "/js/navegacao-graficos-frequencias.js": ["js/navegacao-graficos-frequencias.js", "text/javascript; charset=utf-8"],
      "/js/ajuda-frequencias.js": ["js/ajuda-frequencias.js", "text/javascript; charset=utf-8"],
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
    body: JSON.stringify({
      modo: "SEM_ALTERACAO", motivo: "A geração já está atualizada.",
      salvar_dados: true, concurso_inicial: 500, concurso_final: 3069,
      quantidade_concursos: 0, linhas_estimadas: 0,
      concursos_novos: [], divergencias_configuracao: [],
    }),
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

test("carrega estado, abre prévia e executa simulação com progresso", async ({ page }) => {
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
  await page.route("**/api/frequencias/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      modo: "PRIMEIRA_CARGA", motivo: "Ainda não existe geração histórica ativa.",
      salvar_dados: false, concurso_inicial: 500, concurso_final: 3069,
      quantidade_concursos: 2570, linhas_estimadas: 462600,
      concursos_novos: [], divergencias_configuracao: [],
    }),
  }));
  await page.route("**/api/frequencias/execucoes", (rota) => rota.fulfill({
    status: 202, contentType: "application/json",
    body: JSON.stringify({ id: "teste", estado: "AGUARDANDO", etapa: "Aguardando", concluido: 0, total: 1, percentual: 0 }),
  }));
  await page.route("**/api/frequencias/execucoes/teste", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({ id: "teste", estado: "CONCLUIDA", etapa: "Concluída", concluido: 1, total: 1, percentual: 100, resultado: { tipo: "SIMULACAO", linhas_calculadas: 462600 } }),
  }));
  await page.locator("#botao-calcular-previa-frequencia").click();
  await expect(page.locator("#dialogo-previa-frequencia")).toBeVisible();
  await expect(page.locator("#previa-operacao")).toHaveText("Simulação — Primeira carga");
  await expect(page.locator("#previa-linhas-estimadas")).toHaveText("462.600");
  await expect(page.locator("#previa-gravacao")).toHaveText("Simulação: nenhum dado será gravado.");
  await page.locator("#botao-prosseguir-previa-frequencia").click();
  await expect(page.locator(".modal-andamento__resultado")).toContainText("Simulação concluída sem gravação");
});

test("abre a página auxiliar e retorna ao bloco histórico preservando filtros", async ({ page }) => {
  await preparar(page);
  await page.locator("#historico-dezena").selectOption("17");
  await page.locator("#historico-tipo-evento").selectOption("3VS");
  await page.locator("#historico-concurso-inicial").fill("500");
  await page.locator("#historico-concurso-final").fill("700");
  await page.locator("#botao-abrir-graficos-historico").click();

  await expect(page).toHaveURL(/graficos-frequencias\.html\?dezena=17&tipo_evento=3VS&concurso_inicial=500&concurso_final=700/);
  await expect(page.locator("#graficos-dezena")).toHaveValue("17");
  await expect(page.locator("#graficos-tipo-evento")).toHaveValue("3VS");
  await expect(page.locator("#graficos-concurso-inicial")).toHaveValue("500");
  await expect(page.locator("#graficos-concurso-final")).toHaveValue("700");
  await expect(page.locator(".historico-cartao-ampliado")).toHaveCount(2);
  await expect(page.locator(".grafico-historico-ampliado")).toHaveCount(2);
  await expect(page.locator("#estado-area-graficos")).toContainText("201 pontos");
  await expect(page.locator(".historico-ocorrencia")).toHaveCount(2);
  const alturas = await page.locator(".grafico-historico-ampliado").evaluateAll((graficos) => graficos.map((grafico) => grafico.getBoundingClientRect().height));
  expect(alturas.every((altura) => altura >= 450)).toBeTruthy();
  const coordenadasInvalidas = await page.locator(".grafico-historico-ampliado path, .grafico-historico-ampliado circle").evaluateAll((elementos) => elementos.some((elemento) => elemento.outerHTML.includes("NaN")));
  expect(coordenadasInvalidas).toBeFalsy();
  await expect(page.locator("#aviso-recorte-graficos")).toBeHidden();
  await page.locator("#escala-vertical-graficos").selectOption("AMPLIADA_10X");
  await expect(page.locator("#aviso-recorte-graficos")).toBeVisible();
  await expect(page.locator("#aviso-recorte-graficos")).toContainText("valores ficaram fora da área visível");
  await expect(page.locator(".grafico-historico-ampliado clipPath")).toHaveCount(2);
  await page.locator("#escala-vertical-graficos").selectOption("AUTOMATICA");
  await expect(page.locator("#aviso-recorte-graficos")).toBeHidden();
  await page.locator("#botao-ajuda-graficos").click();
  await expect(page.locator("#dialogo-ajuda-graficos")).toBeVisible();
  await expect(page.locator("#dialogo-ajuda-graficos")).toContainText("Ampliação 10×");
  await page.keyboard.press("Escape");
  await expect(page.locator("#dialogo-ajuda-graficos")).toBeHidden();

  await page.locator("#botao-voltar-frequencias").click();
  await expect(page).toHaveURL(/frequencias\.html\?dezena=17&tipo_evento=3VS&concurso_inicial=500&concurso_final=700#evolucao-historica-dezena/);
  await expect(page.locator("#historico-dezena")).toHaveValue("17");
  await expect(page.locator("#historico-tipo-evento")).toHaveValue("3VS");
  await expect(page.locator("#historico-concurso-inicial")).toHaveValue("500");
  await expect(page.locator("#historico-concurso-final")).toHaveValue("700");
});

test("prévia atualizada não permite prosseguir nem criar execução", async ({ page }) => {
  let execucoes = 0;
  await page.route("**/api/frequencias/execucoes", (rota) => {
    execucoes += 1;
    return rota.abort();
  });
  await preparar(page);
  await page.locator("#botao-calcular-previa-frequencia").click();
  await expect(page.locator("#dialogo-previa-frequencia")).toBeVisible();
  await expect(page.locator("#previa-operacao")).toHaveText("Nenhuma alteração");
  await expect(page.locator("#botao-prosseguir-previa-frequencia")).toBeDisabled();
  await page.locator("#botao-cancelar-previa-frequencia").click();
  await expect(page.locator("#dialogo-previa-frequencia")).not.toBeVisible();
  expect(execucoes).toBe(0);
});

test("modal traduz incrementos e reconstruções e fecha por teclado", async ({ page }) => {
  await preparar(page);
  let modo = "INCREMENTAL";
  const rotulos = {
    INCREMENTAL: "Atualização incremental",
    RECONSTRUCAO_CONFIGURACAO: "Reconstrução por configuração",
    RECONSTRUCAO_ORIGEM: "Reconstrução por alteração da origem",
  };
  await page.route("**/api/frequencias/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      modo, motivo: `Motivo ${modo}`, salvar_dados: true,
      concurso_inicial: 500, concurso_final: 3069,
      quantidade_concursos: modo === "INCREMENTAL" ? 2 : 2570,
      linhas_estimadas: modo === "INCREMENTAL" ? 360 : 462600,
      concursos_novos: modo === "INCREMENTAL" ? [3068, 3069] : [],
      divergencias_configuracao: [],
    }),
  }));
  for (const [valor, rotulo] of Object.entries(rotulos)) {
    modo = valor;
    await page.locator("#botao-calcular-previa-frequencia").click();
    await expect(page.locator("#previa-operacao")).toHaveText(rotulo);
    await expect(page.locator("#previa-gravacao")).toContainText("serão gravados");
    const focoNoDialogo = await page.evaluate(() => Boolean(
      document.activeElement?.closest("#dialogo-previa-frequencia")
    ));
    expect(focoNoDialogo).toBeTruthy();
    await page.keyboard.press("Escape");
    await expect(page.locator("#dialogo-previa-frequencia")).not.toBeVisible();
  }
});

test("erro de prévia aparece no modal e não cria execução", async ({ page }) => {
  let execucoes = 0;
  await preparar(page);
  await page.route("**/api/frequencias/previa", (rota) => rota.fulfill({
    status: 503, contentType: "application/json",
    body: JSON.stringify({ erro: { codigo: "BANCO_INDISPONIVEL", mensagem: "Não foi possível consultar o banco." } }),
  }));
  await page.route("**/api/frequencias/execucoes", (rota) => {
    execucoes += 1;
    return rota.abort();
  });
  await page.locator("#botao-calcular-previa-frequencia").click();
  await expect(page.locator("#dialogo-previa-frequencia")).toBeVisible();
  await expect(page.locator("#erro-previa-frequencia")).toHaveText("Não foi possível consultar o banco.");
  await expect(page.locator("#botao-prosseguir-previa-frequencia")).toBeDisabled();
  expect(execucoes).toBe(0);
});

test("prosseguir com gravação envia confirmação explícita uma única vez", async ({ page }) => {
  let solicitacao;
  await preparar(page);
  await page.route("**/api/frequencias/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      modo: "PRIMEIRA_CARGA", motivo: "Primeira geração.", salvar_dados: true,
      concurso_inicial: 500, concurso_final: 3069,
      quantidade_concursos: 2570, linhas_estimadas: 462600,
      concursos_novos: [], divergencias_configuracao: [],
    }),
  }));
  await page.route("**/api/frequencias/execucoes", async (rota) => {
    solicitacao = rota.request().postDataJSON();
    return rota.fulfill({
      status: 202, contentType: "application/json",
      body: JSON.stringify({ id: "gravar", estado: "AGUARDANDO", etapa: "Aguardando", concluido: 0, total: 1, percentual: 0 }),
    });
  });
  await page.route("**/api/frequencias/execucoes/gravar", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({ id: "gravar", estado: "CONCLUIDA", etapa: "Concluída", concluido: 1, total: 1, percentual: 100, resultado: { tipo: "GRAVACAO", linhas_calculadas: 462600 } }),
  }));
  await page.locator("#botao-calcular-previa-frequencia").click();
  await page.locator("#botao-prosseguir-previa-frequencia").click();
  await expect(page.locator(".modal-andamento__resultado")).toContainText("Dados gravados");
  expect(solicitacao.confirmacao_gravacao).toBe(true);
  expect(solicitacao.salvar_dados).toBe(true);
});

test("abre e fecha a ajuda completa da página", async ({ page }) => {
  await preparar(page);
  const dialogo = page.locator("#dialogo-ajuda-frequencias");
  await expect(dialogo).not.toBeVisible();
  await page.locator("#botao-ajuda-frequencias").click();
  await expect(dialogo).toBeVisible();
  await expect(dialogo.getByRole("heading", { name: "Como usar Frequência das dezenas" })).toBeVisible();
  await expect(dialogo.getByRole("heading", { name: "4. Atualização do histórico" })).toBeVisible();
  await expect(dialogo.getByRole("heading", { name: "Fluxo recomendado" })).toBeVisible();
  await expect(dialogo).toContainText("Autorize reconstrução somente depois");
  await dialogo.getByRole("button", { name: "Fechar", exact: true }).click();
  await expect(dialogo).not.toBeVisible();
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
    await expect(page.locator("#botao-calcular-previa-frequencia")).toBeVisible();
  });
}

test("página auxiliar mantém os gráficos roláveis sem alargar a janela estreita", async ({ page }) => {
  await page.setViewportSize({ width: 520, height: 800 });
  await preparar(page);
  await page.locator("#historico-concurso-inicial").fill("500");
  await page.locator("#historico-concurso-final").fill("510");
  await page.locator("#botao-abrir-graficos-historico").click();
  await expect(page.locator(".historico-cartao-ampliado")).toHaveCount(2);
  const medidas = await page.evaluate(() => ({
    pagina: document.documentElement.scrollWidth,
    janela: document.documentElement.clientWidth,
  }));
  expect(medidas.pagina).toBeLessThanOrEqual(medidas.janela + 1);
  const cartaoRolavel = await page.locator(".historico-cartao-ampliado").first().evaluate((elemento) => elemento.scrollWidth > elemento.clientWidth);
  expect(cartaoRolavel).toBeTruthy();
  await page.locator("#botao-ajuda-graficos").click();
  await expect(page.locator("#dialogo-ajuda-graficos")).toBeVisible();
});
