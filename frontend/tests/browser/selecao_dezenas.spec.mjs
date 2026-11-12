import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const porta = Number(process.env.PLAYWRIGHT_TEST_PORT || 4173);
let servidor;

const configuracao = {
  nome: "Seleção inicial", fator_k: "1.000000", fator_j: "0.000000",
  modo_quantidade: "MAX", quantidade_dezenas: null,
  versao_calculo: 1, assinatura_sha256: "a".repeat(64),
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
      "/js/selecao-dezenas-graficos.js": ["js/selecao-dezenas-graficos.js", "text/javascript; charset=utf-8"],
      "/js/selecao-dezenas-controles.js": ["js/selecao-dezenas-controles.js", "text/javascript; charset=utf-8"],
      "/js/fluxo-cadastro-confirmado.js": ["js/fluxo-cadastro-confirmado.js", "text/javascript; charset=utf-8"],
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
    servidor.listen(porta, "127.0.0.1", resolver);
  });
});

test.afterAll(async () => {
  if (servidor) await new Promise((resolver) => servidor.close(resolver));
});

async function preparar(page, listaConfiguracoes = [{ id_configuracao_selecao: 1, configuracao }]) {
  const chamadas = { registros: 0, corpoRegistro: null, configuracoes: 0, corpoConfiguracao: null, jogosPost: 0 };
  await page.route("**/api/selecao-dezenas/configuracoes", (rota) => {
    if (rota.request().method() === "POST") {
      chamadas.configuracoes += 1;
      chamadas.corpoConfiguracao = rota.request().postDataJSON();
      return rota.fulfill({
        status: 201, contentType: "application/json",
        body: JSON.stringify({ id_configuracao_selecao: 9, configuracao: chamadas.corpoConfiguracao.configuracao }),
      });
    }
    return rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({ configuracoes: listaConfiguracoes }),
    });
  });
  await page.route("**/api/selecao-dezenas/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      resultados: { primeiro: 1, ultimo: 3069, quantidade: 3069 },
      backtest: { concurso_inicial: 500, concurso_final: 3069, quantidade_alvos: 2570 },
      analise_configuracao: {
        concurso_corte: 3069, concurso_alvo: 3070, quantidade_aprovada: 6,
        quantidade_retornada: 6, dezenas_retornadas: [1, 7, 12, 23, 34, 55],
        quantidade_combinacoes: 1,
      },
    }),
  }));
  await page.route("**/api/selecao-dezenas/previsoes", async (rota) => {
    chamadas.registros += 1;
    chamadas.corpoRegistro = rota.request().postDataJSON();
    await rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({
        nova_previsao: { id_execucao_selecao: 8, concurso_corte: 3069, concurso_alvo_inicial: 3070, concurso_alvo_final: 3070, alvos_criados_agora: 1 },
        conferencia: { previsoes_conferidas: 0 },
      }),
    });
  });
  await page.route("**/api/selecao-dezenas/previsoes/8/detalhes", (rota) => rota.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify({ detalhes: [detalhe] }),
  }));
  await page.route("**/api/selecao-dezenas/alvos/9/jogos/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      quantidade_dezenas: 6, quantidade_combinacoes: 1,
      volume_elevado: false, exige_confirmacao: false,
      dezenas: detalhe.dezenas_retornadas,
    }),
  }));
  await page.route("**/api/selecao-dezenas/alvos/9/jogos", (rota) => {
    chamadas.jogosPost += 1;
    return rota.fulfill({ status: 500, contentType: "application/json", body: "{}" });
  });
  await page.goto("/selecao-dezenas.html");
  await expect(page.locator("#mensagem-selecao")).toContainText(`${listaConfiguracoes.length} configuração`);
  return chamadas;
}

test("confirma antes de registrar e exibe o resultado pendente", async ({ page }) => {
  const chamadas = await preparar(page);
  await expect(page.locator("#selecao-nome")).toBeDisabled();
  await expect(page.locator("#selecao-fator-k")).toBeDisabled();
  await expect(page.locator("#botao-salvar-configuracao")).toBeDisabled();
  await expect(page.locator("#estado-edicao-configuracao")).toContainText("protegidos contra alterações");
  await expect(page.locator("#titulo-concurso-alvo")).toHaveText("Registros do screener de dezenas");
  await page.locator("#botao-atualizar-previsao").click();
  await expect(page.locator("#dialogo-confirmar-registro")).toBeVisible();
  await expect(page.locator("#registro-concurso")).toHaveText("3070");
  await expect(page.locator("#registro-quantidade")).toHaveText("6");
  await expect(page.locator("#registro-dezenas")).toHaveText("01 · 07 · 12 · 23 · 34 · 55");
  expect(chamadas.registros).toBe(0);
  await page.locator("#botao-confirmar-registro").click();
  await expect(page.locator("#resumo-previsao")).toContainText("Previsão registrada para o concurso 3070");
  await expect(page.locator("#mensagem-selecao")).toContainText("Nenhum backtest, combinação ou jogo foi criado");
  expect(chamadas.registros).toBe(1);
  expect(chamadas.corpoRegistro).toEqual({ id_configuracao_selecao: 1 });
  const celulas = page.locator("#corpo-previsoes tr").first().locator("td");
  await expect(celulas).toHaveCount(7);
  await expect(celulas.nth(2)).toHaveText("Aguardando resultado");
  await expect(celulas.nth(3)).toHaveText("01 · 07 · 12 · 23 · 34 · 55");
  await expect(celulas.nth(5)).toContainText("k 1; j 0; máximo aprovado");
});

test("cancelar a confirmação não registra", async ({ page }) => {
  const chamadas = await preparar(page);
  await page.locator("#botao-atualizar-previsao").click();
  await expect(page.locator("#dialogo-confirmar-registro")).toBeVisible();
  await page.locator("#botao-cancelar-registro").click();
  await expect(page.locator("#dialogo-confirmar-registro")).not.toBeVisible();
  await expect(page.locator("#mensagem-selecao")).toContainText("Nenhum dado foi gravado");
  expect(chamadas.registros).toBe(0);
});

test("nova configuração libera os campos para preenchimento", async ({ page }) => {
  await preparar(page);
  await page.locator("#configuracao-gravada-selecao").selectOption("");
  await expect(page.locator("#selecao-nome")).toBeEnabled();
  await expect(page.locator("#selecao-fator-k")).toBeEnabled();
  await expect(page.locator("#botao-salvar-configuracao")).toBeEnabled();
  await expect(page.locator("#botao-atualizar-previsao")).toBeDisabled();
  await expect(page.locator("#mensagem-selecao")).toContainText("Nenhum dado foi gravado");
});

test("salvar configuração exige confirmação antes de chamar o banco", async ({ page }) => {
  const chamadas = await preparar(page);
  await page.locator("#configuracao-gravada-selecao").selectOption("");
  await page.locator("#selecao-nome").fill("Estudo confirmado");
  await page.locator("#botao-salvar-configuracao").click();
  await expect(page.locator("#dialogo-confirmar-configuracao")).toBeVisible();
  await expect(page.locator("#configuracao-confirmar-nome")).toHaveText("Estudo confirmado");
  expect(chamadas.configuracoes).toBe(0);
  await page.locator("#dialogo-confirmar-configuracao button[value=cancelar]").last().click();
  await expect(page.locator("#mensagem-selecao")).toContainText("Nenhuma configuração foi criada");
  expect(chamadas.configuracoes).toBe(0);

  await page.locator("#botao-salvar-configuracao").click();
  await page.locator("#botao-confirmar-configuracao").click();
  await expect.poll(() => chamadas.configuracoes).toBe(1);
  expect(chamadas.corpoConfiguracao.configuracao.nome).toBe("Estudo confirmado");
});

test("listas exibem somente os nomes das configurações", async ({ page }) => {
  const outra = { ...configuracao, nome: "Outra configuração" };
  await preparar(page, [
    { id_configuracao_selecao: 2, configuracao },
    { id_configuracao_selecao: 5, configuracao: outra },
  ]);
  await expect(page.locator("#configuracao-gravada-selecao option").nth(1)).toHaveText(configuracao.nome);
  await expect(page.locator("#configuracao-gravada-selecao option").nth(2)).toHaveText("Outra configuração");
  await expect(page.locator("#backtest-configuracao option").nth(2)).toHaveText("Outra configuração");
});

test("configura formação de jogos sem processar nem gravar", async ({ page }) => {
  const chamadas = await preparar(page);
  await page.locator("#botao-atualizar-previsao").click();
  await page.locator("#botao-confirmar-registro").click();
  await page.getByRole("button", { name: "Formar jogos" }).click();

  await expect(page.locator("#titulo-formacao-jogos")).toHaveText("Formação de jogos com as dezenas registradas");
  await expect(page.locator("#painel-jogos")).toBeVisible();
  await expect(page.locator("#jogos-origem-concurso")).toHaveText("3070");
  await expect(page.locator("#jogos-origem-configuracao")).toHaveText(configuracao.nome);
  await expect(page.locator("#jogos-origem-dezenas")).toHaveText("01 · 07 · 12 · 23 · 34 · 55");

  await page.locator("#jogos-quantidade-solicitada").fill("100");
  await page.locator("#jogos-valor-unitario").fill("5,00");
  await expect(page.locator("#jogos-valor-previsto")).toHaveText("R$ 500,00");
  await page.locator("#botao-conferir-jogos").click();

  await expect(page.locator("#dialogo-previa-jogos")).toBeVisible();
  await expect(page.locator("#previa-jogos-quantidade")).toHaveText("100");
  await expect(page.locator("#previa-jogos-valor-unitario")).toHaveText("R$ 5,00");
  await expect(page.locator("#previa-jogos-valor-previsto")).toHaveText("R$ 500,00");
  await expect(page.locator("#botao-iniciar-screener-jogos")).toBeDisabled();
  await expect(page.locator("#mensagem-selecao")).toContainText("sem processar combinações nem gravar dados");
  expect(chamadas.jogosPost).toBe(0);
});

test("configuração do estudo é independente da configuração superior", async ({ page }) => {
  const outra = { ...configuracao, nome: "Outra configuração", fator_k: "0.500000" };
  await preparar(page, [
    { id_configuracao_selecao: 1, configuracao },
    { id_configuracao_selecao: 2, configuracao: outra },
  ]);
  await expect(page.locator("#configuracao-gravada-selecao")).toHaveValue("2");
  await expect(page.locator("#backtest-configuracao")).toHaveValue("");
  await page.locator("#botao-gerar-backtest").click();
  await expect(page.locator("#estado-backtest")).toContainText("Selecione uma configuração salva");
  await page.locator("#backtest-configuracao").selectOption("1");
  let corpoRecebido;
  await page.route("**/api/selecao-dezenas/backtests/previa", (rota) => {
    corpoRecebido = rota.request().postDataJSON();
    return rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({
        id_configuracao_selecao: 1, configuracao,
        resultados: { primeiro: 1, ultimo: 3069, quantidade: 3069 },
        periodo: { concurso_inicial: 500, concurso_final: 3069, quantidade_concursos: 2570 },
        persistira_resultados: false,
      }),
    });
  });
  await page.locator("#botao-gerar-backtest").click();
  await expect(page.locator("#dialogo-previa-backtest")).toBeVisible();
  expect(corpoRecebido).toEqual({ id_configuracao_selecao: 1, concurso_inicial: 500 });
});

test("desenha relatório do Backtest com centenas, limites e níveis de acerto", async ({ page }) => {
  await preparar(page);
  await page.locator("#backtest-configuracao").selectOption("1");
  const pontos = [
    { concurso: 500, quantidade_dezenas: 12, quantidade_acertos: 2 },
    { concurso: 501, quantidade_dezenas: 18, quantidade_acertos: 4 },
    { concurso: 502, quantidade_dezenas: 15, quantidade_acertos: 6 },
  ];
  await page.route("**/api/selecao-dezenas/backtests/previa", (rota) => rota.fulfill({
    status: 200, contentType: "application/json",
    body: JSON.stringify({
      id_configuracao_selecao: 1, configuracao,
      resultados: { primeiro: 1, ultimo: 3069, quantidade: 3069 },
      periodo: { concurso_inicial: 500, concurso_final: 502, quantidade_concursos: 3 },
      persistira_resultados: false,
    }),
  }));
  await page.route(/\/api\/selecao-dezenas\/backtests$/, (rota) => rota.fulfill({
    status: 202, contentType: "application/json",
    body: JSON.stringify({
      id: "backtest-1", estado: "AGUARDANDO", etapa: "Aguardando início",
      concluido: 0, total: 3, percentual: 0, duracao_segundos: 0,
    }),
  }));
  await page.route("**/api/selecao-dezenas/backtests/backtest-1", (rota) => {
    if (rota.request().method() === "DELETE") {
      return rota.fulfill({ status: 204, body: "" });
    }
    return rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({
        id: "backtest-1", estado: "CONCLUIDA", etapa: "Concluída",
        concluido: 3, total: 3, percentual: 100, duracao_segundos: 0.2,
        resultado: {
          id_configuracao_selecao: 1, concurso_inicial: 500, concurso_final: 502,
          pontos, duracao_segundos: 0.18, persistido: false,
          resumo: {
            testes_efetuados: 3, minimo_dezenas: 12, maximo_dezenas: 18,
            media_dezenas: 15, media_acertos: 4, concursos_premiados: 2,
            percentual_premiados: 66.666667,
            classes: Array.from({ length: 7 }, (_, classe) => ({
              classe, quantidade: [0, 0, 1, 0, 1, 0, 1][classe],
              percentual: [0, 0, 33.333333, 0, 33.333333, 0, 33.333333][classe],
            })),
          },
        },
      }),
    });
  });

  await page.locator("#botao-gerar-backtest").click();
  await expect(page.locator("#dialogo-previa-backtest")).toBeVisible();
  await expect(page.locator("#previa-backtest-quantidade")).toHaveText("3");
  await page.locator("#botao-confirmar-backtest").click();
  const andamento = page.getByRole("dialog", { name: "Cálculo do Backtest" });
  await expect(andamento.locator(".modal-andamento__contexto")).toContainText("Seleção inicial");
  await expect(andamento.locator(".modal-andamento__contexto")).not.toContainText("Configuração 1 —");
  await expect(andamento.locator(".modal-andamento__contexto")).toContainText("3 concursos");
  await expect(page.locator("#relatorio-backtest")).toBeVisible();
  await expect(page.locator("#resumo-backtest")).toContainText("Testes efetuados");
  await expect(page.locator("#classes-backtest .selecao-classe")).toHaveCount(7);
  await expect(page.locator("#grafico-backtest-quantidade path.backtest-grafico__trajeto")).toHaveCount(1);
  await expect(page.locator("#grafico-backtest-quantidade line.backtest-grafico__grade-vertical")).toHaveCount(1);
  await expect(page.locator("#grafico-backtest-acertos line.backtest-grafico__nivel")).toHaveCount(7);
  await expect(page.locator("#mensagem-selecao")).toContainText("Relatório gráfico concluído");
  await expect(page.locator("#periodo-backtest")).toContainText("k=1.000000; j=0.000000; modo MAX; versão 1");
});
