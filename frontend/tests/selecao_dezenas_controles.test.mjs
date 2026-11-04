import test from "node:test";
import assert from "node:assert/strict";

import { formatarDezenas, idsComparacao, montarConfiguracao } from "../js/selecao-dezenas-controles.js";

test("monta configuração MAX sem quantidade fixa", () => {
  const config = montarConfiguracao({
    nome: " Estudo ", fator_k: "1", fator_j: "0", modo_quantidade: "max",
    quantidade_dezenas: "", horizonte_concursos: "2", versao_calculo: "1",
  });
  assert.equal(config.nome, "Estudo");
  assert.equal(config.modo_quantidade, "MAX");
  assert.equal(config.quantidade_dezenas, null);
  assert.equal(config.horizonte_concursos, 2);
});

test("valida quantidade FIXA e limites de j", () => {
  assert.equal(montarConfiguracao({
    nome: "Fixa", fator_k: ".5", fator_j: "-.5", modo_quantidade: "FIXA",
    quantidade_dezenas: "7", horizonte_concursos: "1", versao_calculo: "1",
  }).quantidade_dezenas, 7);
  assert.throws(() => montarConfiguracao({
    nome: "Inválida", fator_k: ".5", fator_j: ".6", modo_quantidade: "MAX",
    horizonte_concursos: "1", versao_calculo: "1",
  }), /entre -k e \+k/);
});

test("normaliza IDs distintos e formata dezenas", () => {
  assert.deepEqual(idsComparacao("3, 8, 12"), [3, 8, 12]);
  assert.throws(() => idsComparacao("3, 3"), /dois IDs distintos/);
  assert.equal(formatarDezenas([1, 9, 10]), "01 · 09 · 10");
});
