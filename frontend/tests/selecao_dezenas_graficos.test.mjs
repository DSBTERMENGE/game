import test from "node:test";
import assert from "node:assert/strict";

import { construirModeloGraficos } from "../js/selecao-dezenas-graficos.js";

function pontos(inicio, fim) {
  return Array.from({ length: fim - inicio + 1 }, (_, indice) => ({
    concurso: inicio + indice,
    quantidade_dezenas: 10 + (indice % 9),
    quantidade_acertos: indice % 7,
  }));
}

test("marca somente centenas e alinha os dois trajetos no mesmo eixo", () => {
  const modelo = construirModeloGraficos(pontos(500, 706));
  assert.deepEqual(modelo.centenas.map((item) => item.concurso), [500, 600, 700]);
  assert.equal(modelo.caminhoQuantidade.split("L").length, 207);
  assert.equal(modelo.caminhoAcertos.split("L").length, 207);
  assert.equal(modelo.alturaQuantidade, 190);
  assert.equal(modelo.alturaAcertos, 300);
});

test("mantém mínimo, máximo e sete níveis exclusivos de acerto", () => {
  const modelo = construirModeloGraficos([
    { concurso: 500, quantidade_dezenas: 12, quantidade_acertos: 0 },
    { concurso: 501, quantidade_dezenas: 18, quantidade_acertos: 6 },
  ]);
  assert.equal(modelo.minimo, 12);
  assert.equal(modelo.maximo, 18);
  assert.deepEqual(modelo.niveisAcertos.map((item) => item.valor), [0, 1, 2, 3, 4, 5, 6]);
  assert.deepEqual(modelo.niveisAcertos.map((item) => item.premiado), [
    false, false, false, false, true, true, true,
  ]);
});

test("rejeita concursos não consecutivos e acertos fora da escala", () => {
  assert.throws(() => construirModeloGraficos([
    { concurso: 500, quantidade_dezenas: 12, quantidade_acertos: 2 },
    { concurso: 502, quantidade_dezenas: 13, quantidade_acertos: 3 },
  ]), /consecutivos/);
  assert.throws(() => construirModeloGraficos([
    { concurso: 500, quantidade_dezenas: 12, quantidade_acertos: 7 },
  ]), /intervalo esperado/);
});
