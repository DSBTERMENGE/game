import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../selecao-dezenas.html", import.meta.url), "utf8");
const css = await readFile(new URL("../css/selecao-dezenas.css", import.meta.url), "utf8");
const javascript = await readFile(new URL("../js/selecao-dezenas.js", import.meta.url), "utf8");
const graficos = await readFile(new URL("../js/selecao-dezenas-graficos.js", import.meta.url), "utf8");

test("página possui navegação e blocos da subetapa 23.10", () => {
  assert.match(html, /aria-current="page">Seleção de dezenas/);
  for (const id of [
    "form-configuracao-selecao", "titulo-concurso-alvo", "controles-backtest-selecao",
    "backtest-configuracao",
    "painel-jogos",
    "botao-gerar-backtest", "estado-backtest", "relatorio-backtest",
    "grafico-backtest-quantidade", "grafico-backtest-acertos",
  ]) assert.match(html, new RegExp(`id="${id}"`));
  assert.match(html, /js\/selecao-dezenas\.js/);
});

test("página abre a ajuda operacional central", () => {
  assert.match(html, /id="botao-ajuda-selecao"/);
  assert.match(html, /ajuda\.html\?origem=%2Fselecao-dezenas\.html#pagina-selecao-dezenas/);
  assert.doesNotMatch(html, /<dialog id="dialogo-ajuda-selecao"/);
});

test("javascript usa os endpoints da API e prepara jogos sem gravação", () => {
  for (const trecho of [
    "/api/selecao-dezenas/configuracoes", "/api/selecao-dezenas/previa",
    "/api/selecao-dezenas/previsoes",
    "/jogos/previa", "/api/selecao-dezenas/backtests",
  ]) assert.match(javascript, new RegExp(trecho.replaceAll("/", "\\/")));
  assert.match(javascript, /criarModalAndamento/);
  assert.match(javascript, /dialogo_previa_backtest\.showModal/);
  assert.match(javascript, /Dados analíticos da configuração/);
  assert.match(javascript, /Esta análise é momentânea e não foi armazenada/);
  assert.match(html, /id="dialogo-confirmar-registro"/);
  assert.match(html, /id="dialogo-confirmar-configuracao"/);
  assert.match(html, /Nenhuma configuração será criada até sua confirmação/);
  assert.match(html, /Confirmar e salvar/);
  assert.match(javascript, /NOME_CONFIGURACAO_EXISTENTE/);
  assert.doesNotMatch(javascript, /const rotulo = `\$\{item\.id_configuracao_selecao\}/);
  assert.match(html, /Cancelar — não registrar/);
  assert.match(html, /Confirmar e registrar seleção/);
  assert.doesNotMatch(html, /Executar e gravar backtest/);
  assert.doesNotMatch(html, /Confirmar e gravar backtest/);
  assert.match(html, /Selecione uma configuração/);
  assert.doesNotMatch(html, /id="backtest-final"/);
  assert.match(javascript, /id_configuracao_selecao: idConfiguracao/);
  assert.match(javascript, /renderizarGraficosBacktest/);
  assert.match(graficos, /concurso \+= 100/);
  assert.match(graficos, /nivel\.premiado \? "premiado" : "sem-premio"/);
  assert.match(javascript, /Operação cancelada\. Nenhum dado foi gravado/);
  assert.match(html, /Formação de jogos com as dezenas registradas/);
  assert.match(html, /id="jogos-quantidade-solicitada"/);
  assert.match(html, /id="jogos-valor-unitario"/);
  assert.match(html, /id="jogos-valor-previsto"/);
  assert.match(html, /id="dialogo-previa-jogos"/);
  assert.match(html, /id="botao-iniciar-screener-jogos"[^>]*disabled/);
  assert.doesNotMatch(javascript, /autorizar_persistencia/);
  assert.doesNotMatch(javascript, /method:\s*"POST"[^}]*\/jogos/s);
});

test("layout possui duas colunas e adaptação responsiva", () => {
  assert.match(css, /\.selecao-duas-colunas\s*\{[^}]*grid-template-columns:\s*1fr 1fr/s);
  assert.match(css, /@media \(max-width: 950px\)/);
  assert.match(css, /\.selecao-diagrama-faixa svg/);
  assert.match(css, /\.backtest-grafico__grade-vertical/);
  assert.match(css, /\.backtest-grafico__nivel--premiado/);
});
