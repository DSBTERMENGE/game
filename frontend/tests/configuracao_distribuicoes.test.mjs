import assert from "node:assert/strict";
import test from "node:test";

import {
  CHAVE_CONFIGURACAO_DISTRIBUICOES,
  CONFIGURACAO_DISTRIBUICOES_PADRAO,
  carregarConfiguracaoDistribuicoes,
  criarConsultaDistribuicoes,
  normalizarConfiguracaoDistribuicoes,
  salvarConfiguracaoDistribuicoes,
} from "../js/configuracao-distribuicoes.js";


function armazenamentoFalso(inicial = {}) {
  const dados = new Map(Object.entries(inicial));
  return {
    getItem: (chave) => dados.get(chave) ?? null,
    setItem: (chave, valor) => dados.set(chave, valor),
    dados,
  };
}

test("configuração padrão usa um desvio para cada lado", () => {
  const configuracao = carregarConfiguracaoDistribuicoes(armazenamentoFalso());
  assert.deepEqual(configuracao, CONFIGURACAO_DISTRIBUICOES_PADRAO);
});

test("salva e recupera margens assimétricas sem ativação", () => {
  const armazenamento = armazenamentoFalso();
  const salva = salvarConfiguracaoDistribuicoes({
    metodo_faixa: "percentual_media",
    margem_inferior: "10",
    margem_superior: "20",
  }, armazenamento);
  const recuperada = carregarConfiguracaoDistribuicoes(armazenamento);

  assert.deepEqual(recuperada, salva);
  assert.deepEqual(recuperada, {
    metodo_faixa: "percentual_media", margem_inferior: "10", margem_superior: "20",
  });
  assert.doesNotMatch(armazenamento.dados.get(CHAVE_CONFIGURACAO_DISTRIBUICOES), /ativa|screener/);
});

test("dados inválidos retornam ao padrão e consulta é reproduzível", () => {
  const normalizada = normalizarConfiguracaoDistribuicoes({
    metodo_faixa: "x", margem_inferior: "-1", margem_superior: "NaN",
  });
  assert.deepEqual(normalizada, CONFIGURACAO_DISTRIBUICOES_PADRAO);
  assert.equal(
    criarConsultaDistribuicoes(normalizada),
    "metodo_faixa=desvio_padrao&margem_inferior=1&margem_superior=1",
  );
});

test("JSON corrompido não impede a abertura da página", () => {
  const armazenamento = armazenamentoFalso({ [CHAVE_CONFIGURACAO_DISTRIBUICOES]: "{" });
  assert.deepEqual(
    carregarConfiguracaoDistribuicoes(armazenamento),
    CONFIGURACAO_DISTRIBUICOES_PADRAO,
  );
});
