import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../selecao-dezenas.html", import.meta.url), "utf8");
const css = await readFile(new URL("../css/selecao-dezenas.css", import.meta.url), "utf8");
const javascript = await readFile(new URL("../js/selecao-dezenas.js", import.meta.url), "utf8");

test("página possui navegação e blocos da subetapa 23.10", () => {
  assert.match(html, /aria-current="page">Seleção de dezenas/);
  for (const id of [
    "form-configuracao-selecao", "titulo-previsao-futura", "form-backtest-selecao",
    "form-comparacao-selecao", "corpo-detalhes-backtest", "painel-jogos",
  ]) assert.match(html, new RegExp(`id="${id}"`));
  assert.match(html, /js\/selecao-dezenas\.js/);
});

test("página contém ajuda modal por blocos", () => {
  assert.match(html, /id="botao-ajuda-selecao"/);
  assert.match(html, /id="dialogo-ajuda-selecao"/);
  assert.match(html, /Como usar Seleção de dezenas/);
  assert.match(html, /formação de jogos/i);
  assert.match(html, /última ocorrência \+ média dos intervalos \+ j × desvio-padrão/);
  assert.match(html, /C\(N,6\)/);
  assert.match(html, /Fluxo recomendado/);
  assert.match(html, /não garante desempenho futuro/);
});

test("javascript usa os endpoints da API e confirma jogos", () => {
  for (const trecho of [
    "/api/selecao-dezenas/configuracoes", "/api/selecao-dezenas/previa",
    "/api/selecao-dezenas/backtests", "/api/selecao-dezenas/previsoes",
    "/jogos/previa",
  ]) assert.match(javascript, new RegExp(trecho.replaceAll("/", "\\/")));
  assert.match(javascript, /window\.confirm/);
  assert.match(javascript, /criarModalAndamento/);
  assert.match(javascript, /dialogo_previa_backtest\.showModal/);
});

test("layout possui duas colunas e adaptação responsiva", () => {
  assert.match(css, /\.selecao-duas-colunas\s*\{[^}]*grid-template-columns:\s*1fr 1fr/s);
  assert.match(css, /@media \(max-width: 950px\)/);
});
