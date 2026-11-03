import assert from "node:assert/strict";
import test from "node:test";

import { prepararIntervalosAuxiliares } from "../js/frequencia-intervalos-auxiliares.js";
import { geometriaOcorrenciasOrdenadas } from "../js/frequencia-grafico-ordenado.js";

test("posiciona intervalos ordenados nos dois eixos percentuais", () => {
  const dados = prepararIntervalosAuxiliares([4, 1, 2, 2]);
  const geometria = geometriaOcorrenciasOrdenadas(dados);
  assert.deepEqual(
    geometria.pontos.map((item) => [
      item.percentualOcorrencias, item.percentualMaiorIntervalo,
    ]),
    [[25, 25], [50, 50], [75, 50], [100, 100]],
  );
  assert.deepEqual(geometria.grade, Array.from({ length: 21 }, (_, indice) => indice * 5));
  assert.ok(geometria.pontos[0].x < geometria.pontos[1].x);
  assert.ok(geometria.pontos[1].x < geometria.pontos[2].x);
  assert.ok(geometria.pontos[2].x < geometria.pontos[3].x);
  assert.ok(geometria.pontos[0].y > geometria.pontos[1].y);
  assert.equal(geometria.pontos[1].y, geometria.pontos[2].y);
  assert.ok(geometria.pontos[2].y > geometria.pontos[3].y);
  const passos = geometria.pontos.slice(1).map(
    (item, indice) => item.x - geometria.pontos[indice].x,
  );
  assert.ok(passos.every((passo) => Math.abs(passo - passos[0]) < 1e-9));
  assert.doesNotMatch(geometria.caminho, /NaN|Infinity/);
});

test("repetições ocupam posições distintas e formam trecho horizontal", () => {
  const dados = prepararIntervalosAuxiliares([1, 1, 1, 4]);
  const geometria = geometriaOcorrenciasOrdenadas(dados);
  assert.equal(geometria.pontos[0].y, geometria.pontos[1].y);
  assert.equal(geometria.pontos[1].y, geometria.pontos[2].y);
  assert.notEqual(geometria.pontos[0].x, geometria.pontos[1].x);
  assert.deepEqual(
    geometria.pontos.map((item) => item.ordem),
    [1, 2, 3, 4],
  );
});

test("último ponto termina exatamente em cem por cento nos dois eixos", () => {
  const dados = prepararIntervalosAuxiliares([2, 5, 9, 12, 20]);
  const geometria = geometriaOcorrenciasOrdenadas(dados);
  assert.equal(geometria.pontos[0].percentualOcorrencias, 20);
  assert.equal(geometria.pontos.at(-1).percentualOcorrencias, 100);
  assert.equal(geometria.pontos.at(-1).percentualMaiorIntervalo, 100);
  assert.equal(geometria.pontos.at(-1).x, geometria.direita);
  assert.equal(geometria.pontos.at(-1).y, geometria.topo);
});

test("conjunto vazio não cria geometria", () => {
  assert.equal(geometriaOcorrenciasOrdenadas(prepararIntervalosAuxiliares([])), null);
});
