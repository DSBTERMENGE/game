import assert from "node:assert/strict";
import test from "node:test";

import { prepararIntervalosAuxiliares } from "../js/frequencia-intervalos-auxiliares.js";
import { geometriaCurvaDistribuicao } from "../js/frequencia-grafico-distribuicao.js";

test("gera curvas real e normal no mesmo domínio sem coordenadas inválidas", () => {
  const dados = prepararIntervalosAuxiliares([1, 1, 2, 3, 5, 8, 13]);
  const geometria = geometriaCurvaDistribuicao(dados);
  assert.equal(geometria.reais.length, 13);
  assert.equal(geometria.normais.length, 13);
  assert.match(geometria.caminhoReal, /^M/);
  assert.match(geometria.caminhoNormal, /^M/);
  assert.doesNotMatch(`${geometria.caminhoReal}${geometria.caminhoNormal}`, /NaN|Infinity/);
  assert.ok(geometria.yMax >= 100 / 7 * 2);
});

test("marca média e somente os limites de desvio dentro do domínio", () => {
  const dados = prepararIntervalosAuxiliares([1, 1, 1, 10]);
  const geometria = geometriaCurvaDistribuicao(dados);
  assert.ok(geometria.marcadores.some((item) => item.tipo === "media"));
  assert.ok(geometria.marcadores.every((item) => (
    item.valor >= geometria.xMin && item.valor <= geometria.xMax
  )));
});

test("desvio zero omite curva normal sem perder a distribuição real", () => {
  const dados = prepararIntervalosAuxiliares([7, 7, 7]);
  const geometria = geometriaCurvaDistribuicao(dados);
  assert.equal(geometria.normais.length, 0);
  assert.equal(geometria.caminhoNormal, "");
  assert.equal(geometria.reais[6].percentual, 100);
  assert.doesNotMatch(geometria.caminhoReal, /NaN|Infinity/);
});

test("conjunto vazio não cria geometria", () => {
  assert.equal(geometriaCurvaDistribuicao(prepararIntervalosAuxiliares([])), null);
});
