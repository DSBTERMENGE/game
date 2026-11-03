import assert from "node:assert/strict";
import test from "node:test";

import { prepararIntervalosAuxiliares } from "../js/frequencia-intervalos-auxiliares.js";

const perto = (atual, esperado, tolerancia = 1e-10) => {
  assert.ok(Math.abs(atual - esperado) <= tolerancia, `${atual} != ${esperado}`);
};

test("calcula distribuição real, média e desvio populacional", () => {
  const dados = prepararIntervalosAuxiliares([
    { intervalo: 1 }, { intervalo: 1 }, { intervalo: 2 }, { intervalo: 4 },
  ]);
  assert.equal(dados.total, 4);
  assert.equal(dados.menorIntervalo, 1);
  assert.equal(dados.maiorIntervalo, 4);
  perto(dados.media, 2);
  perto(dados.desvioPadrao, Math.sqrt(1.5));
  assert.deepEqual(
    dados.distribuicao.map(({ intervalo, quantidade, percentual }) => (
      { intervalo, quantidade, percentual }
    )),
    [
      { intervalo: 1, quantidade: 2, percentual: 50 },
      { intervalo: 2, quantidade: 1, percentual: 25 },
      { intervalo: 3, quantidade: 0, percentual: 0 },
      { intervalo: 4, quantidade: 1, percentual: 25 },
    ],
  );
  perto(dados.distribuicao.reduce((soma, item) => soma + item.percentual, 0), 100);
});

test("preserva repetições e posições percentuais exatas na ordenação", () => {
  const dados = prepararIntervalosAuxiliares([4, 1, 2, 1]);
  assert.deepEqual(dados.ordenados, [
    { ordem: 1, intervalo: 1, percentualOcorrencias: 25, percentualMaiorIntervalo: 25 },
    { ordem: 2, intervalo: 1, percentualOcorrencias: 50, percentualMaiorIntervalo: 25 },
    { ordem: 3, intervalo: 2, percentualOcorrencias: 75, percentualMaiorIntervalo: 50 },
    { ordem: 4, intervalo: 4, percentualOcorrencias: 100, percentualMaiorIntervalo: 100 },
  ]);
});

test("contrato percentual usa passo constante e não encaixa pontos na grade de cinco", () => {
  for (const total of [20, 14, 17]) {
    const dados = prepararIntervalosAuxiliares(
      Array.from({ length: total }, (_, indice) => indice + 1),
    );
    const passo = 100 / total;
    dados.ordenados.forEach((item, indice) => {
      perto(item.percentualOcorrencias, (indice + 1) * passo);
      perto(item.percentualMaiorIntervalo, (indice + 1) / total * 100);
    });
    perto(dados.ordenados.at(-1).percentualOcorrencias, 100);
    perto(dados.ordenados.at(-1).percentualMaiorIntervalo, 100);
    if (total === 20) {
      assert.ok(dados.ordenados.every(
        (item) => Math.abs(item.percentualOcorrencias % 5) < 1e-10,
      ));
    } else {
      assert.ok(dados.ordenados.slice(0, -1).some(
        (item) => Math.abs(item.percentualOcorrencias % 5) > 1e-10,
      ));
    }
  }
});

test("curva normal usa área de cada faixa inteira e é simétrica", () => {
  const dados = prepararIntervalosAuxiliares([8, 10, 12]);
  perto(dados.media, 10);
  perto(
    dados.distribuicao[7].percentualNormal,
    dados.distribuicao[11].percentualNormal,
    1e-8,
  );
  assert.ok(dados.distribuicao[9].percentualNormal > dados.distribuicao[7].percentualNormal);
});

test("conjunto vazio e desvio zero possuem contrato explícito", () => {
  assert.deepEqual(prepararIntervalosAuxiliares([]), {
    total: 0, menorIntervalo: null, maiorIntervalo: null,
    media: null, desvioPadrao: null, limiteInferiorDesvio: null,
    limiteSuperiorDesvio: null, distribuicao: [], ordenados: [],
  });
  const unico = prepararIntervalosAuxiliares([{ intervalo: 7 }]);
  assert.equal(unico.desvioPadrao, 0);
  assert.equal(unico.distribuicao[6].percentual, 100);
  assert.ok(unico.distribuicao.every((item) => item.percentualNormal === null));
  assert.deepEqual(unico.ordenados, [{
    ordem: 1, intervalo: 7, percentualOcorrencias: 100,
    percentualMaiorIntervalo: 100,
  }]);
});

test("rejeita lista e intervalos fora do contrato", () => {
  assert.throws(() => prepararIntervalosAuxiliares(null), TypeError);
  for (const valor of [0, -1, 1.5, "x", null]) {
    assert.throws(() => prepararIntervalosAuxiliares([valor]), RangeError);
  }
});
