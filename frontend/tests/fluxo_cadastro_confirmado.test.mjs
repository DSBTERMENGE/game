import test from "node:test";
import assert from "node:assert/strict";

import { criarFluxoCadastroConfirmado } from "../js/fluxo-cadastro-confirmado.js";

test("preparar e cancelar não gravam", async () => {
  let gravacoes = 0;
  const fluxo = criarFluxoCadastroConfirmado({
    validar: (dados) => ({ nome: dados.nome.trim() }),
    gravar: async () => { gravacoes += 1; },
  });
  assert.deepEqual(fluxo.preparar({ nome: " Teste " }), { nome: "Teste" });
  assert.equal(gravacoes, 0);
  assert.equal(fluxo.cancelar(), true);
  assert.equal(await fluxo.confirmar(), null);
  assert.equal(gravacoes, 0);
});

test("duplo confirmar compartilha uma única gravação", async () => {
  let liberar;
  let gravacoes = 0;
  const fluxo = criarFluxoCadastroConfirmado({
    validar: (dados) => dados,
    gravar: async (dados) => {
      gravacoes += 1;
      await new Promise((resolve) => { liberar = resolve; });
      return dados.nome;
    },
  });
  fluxo.preparar({ nome: "Único" });
  const primeira = fluxo.confirmar();
  const segunda = fluxo.confirmar();
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(gravacoes, 1);
  assert.equal(fluxo.cancelar(), false);
  liberar();
  assert.deepEqual(await Promise.all([primeira, segunda]), ["Único", "Único"]);
  assert.equal(fluxo.obterEstado().estado, "CONCLUIDO");
});

test("falha preserva a conferência para nova tentativa", async () => {
  let tentativas = 0;
  const fluxo = criarFluxoCadastroConfirmado({
    validar: (dados) => dados,
    gravar: async () => {
      tentativas += 1;
      if (tentativas === 1) throw new Error("falha esperada");
      return "ok";
    },
  });
  fluxo.preparar({ nome: "Teste" });
  await assert.rejects(fluxo.confirmar(), /falha esperada/);
  assert.deepEqual(fluxo.obterEstado(), { estado: "CONFERENCIA", possuiDadosConferidos: true });
  assert.equal(await fluxo.confirmar(), "ok");
  assert.equal(tentativas, 2);
});
