import assert from "node:assert/strict";
import test from "node:test";

import {
  MENSAGEM_CONFIRMACAO_FREQUENCIA,
  criarControleFrequencia,
  criarEstadoInicialFrequencia,
  descreverPreviaFrequencia,
} from "../js/frequencia-controles.js";


test("Salvar dados inicia marcado e usa a mensagem aprovada", () => {
  assert.equal(criarEstadoInicialFrequencia().salvarDados, true);
  assert.equal(
    MENSAGEM_CONFIRMACAO_FREQUENCIA,
    "O tick para salvar está ativo. Você realmente deseja salvar os dados?",
  );
});

test("prévia incremental lista os concursos novos", () => {
  assert.equal(descreverPreviaFrequencia({
    modo: "INCREMENTAL", concursos_novos: [903, 904, 905],
  }), "Serão acrescentados os concursos: 903, 904, 905.");
});

test("configuração diferente mostra valores gravado e calculado", () => {
  const texto = descreverPreviaFrequencia({
    modo: "RECONSTRUCAO_CONFIGURACAO",
    divergencias_configuracao: [{
      campo: "tamanho_inicial", valor_gravado: 500, valor_calculado: 600,
    }],
  });
  assert.match(texto, /tamanho_inicial: 500 → 600/);
  assert.match(texto, /reconstruída e substituída/);
});

test("tick desmarcado simula sem solicitar confirmação", async () => {
  let confirmou = 0;
  let salvou = 0;
  let simulou = 0;
  const controle = criarControleFrequencia({
    confirmar: async () => { confirmou += 1; return true; },
    salvar: async () => { salvou += 1; },
    simular: async () => { simulou += 1; return "simulado"; },
  });
  assert.equal(await controle.executar({ previa: {}, salvarDados: false }), "simulado");
  assert.deepEqual([confirmou, salvou, simulou], [0, 0, 1]);
});

test("gravação depende de confirmação e impede execução dupla", async () => {
  let liberar;
  const espera = new Promise((resolve) => { liberar = resolve; });
  const controle = criarControleFrequencia({
    confirmar: async () => true,
    salvar: async (dados) => { await espera; return dados; },
    simular: async () => null,
  });
  const primeira = controle.executar({ previa: { modo: "PRIMEIRA_CARGA" } });
  assert.equal(controle.estaExecutando(), true);
  assert.equal(await controle.executar({ previa: {} }), null);
  liberar();
  assert.deepEqual(await primeira, { confirmacao_gravacao: true });
  assert.equal(controle.estaExecutando(), false);
});
