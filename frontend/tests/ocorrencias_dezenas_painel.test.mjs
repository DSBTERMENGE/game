import assert from "node:assert/strict";
import test from "node:test";

import {
  contarOcorrenciasDasDezenas,
  organizarOcorrenciasEmColunas,
  prepararOcorrenciasDasDezenas,
} from "../js/ocorrencias-dezenas-painel.js";

test("conta as 60 dezenas e preserva as que não ocorreram", () => {
  const ocorrencias = contarOcorrenciasDasDezenas([
    [1, 2, 3, 4, 5, 60],
    [1, 10, 20, 30, 40, 60],
  ]);
  assert.equal(ocorrencias.length, 60);
  assert.deepEqual(ocorrencias[0], { dezena: 1, quantidade: 2 });
  assert.deepEqual(ocorrencias[5], { dezena: 6, quantidade: 0 });
  assert.deepEqual(ocorrencias[59], { dezena: 60, quantidade: 2 });
  assert.equal(ocorrencias.reduce((soma, item) => soma + item.quantidade, 0), 12);
});

test("organiza quatro colunas sequenciais com quinze dezenas", () => {
  const ocorrencias = contarOcorrenciasDasDezenas([]);
  const colunas = organizarOcorrenciasEmColunas(ocorrencias);
  assert.equal(colunas.length, 4);
  assert.ok(colunas.every((coluna) => coluna.length === 15));
  assert.deepEqual(colunas.map((coluna) => coluna[0].dezena), [1, 16, 31, 46]);
  assert.deepEqual(colunas.map((coluna) => coluna.at(-1).dezena), [15, 30, 45, 60]);
});

test("prepara contagem, colunas e total em uma única operação", () => {
  const preparacao = prepararOcorrenciasDasDezenas([[1, 2, 3, 4, 5, 6]]);
  assert.equal(preparacao.total, 6);
  assert.equal(preparacao.colunas[0][0].quantidade, 1);
  assert.equal(preparacao.colunas[3][14].quantidade, 0);
});

test("recusa resultados e estruturas inválidas", () => {
  assert.throws(() => contarOcorrenciasDasDezenas(null), /lista/);
  assert.throws(() => contarOcorrenciasDasDezenas([[1, 2]]), /seis dezenas/);
  assert.throws(() => contarOcorrenciasDasDezenas([[1, 2, 3, 4, 5, 61]]), /inválida/);
  assert.throws(() => organizarOcorrenciasEmColunas([]), /60 dezenas/);
});
