import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { CODIGOS_FAMILIAS, validarQuadroExtensivel } from "../js/screener-extensivel-contrato.js";


function filtro(codigo, entrada, exclusoes) {
  return {
    codigo, nome: codigo, ordem: 1, entrada, avaliacoes: entrada, exclusoes,
    percentual_total_inicial: "10.000000", percentual_saldo_recebido: "10.000000",
    saldo: entrada - exclusoes,
  };
}

function padrao(codigo, estado, avaliacoes = 0, exclusoes = 0, saldo = null) {
  return {
    padrao_cod: codigo, padrao_nome: codigo, num_ocorrencias: 1,
    total_sorteios: 100, percentual_ocorrencia: "1.000000",
    limite_percentual: "10.000000", operador: "<", estado,
    avaliacoes, correspondencias: exclusoes, exclusoes, saldo,
  };
}

const quadro = {
  escopo: { tipo: "amostra", total_universo: 50063860, total_analisado: 100, processamento_integral: false },
  resumo: { total_analisado: 100, total_excluido: 30, percentual_excluido: "30.000000", total_aprovado: 70, percentual_aprovado: "70.000000", reconciliado: true },
  familias: [
    { codigo: "ESTATISTICA", nome: "Estatística", ordem: 1, entrada: 100, exclusoes: 10, saldo: 90, percentual_total_inicial: "10", percentual_saldo_recebido: "10", filtros: [filtro("EST", 100, 10)] },
    { codigo: "GEOMETRIA", nome: "Geometria", ordem: 2, entrada: 90, exclusoes: 10, saldo: 80, percentual_total_inicial: "10", percentual_saldo_recebido: "11.111111", filtros: [filtro("GEO", 90, 10)] },
    { codigo: "PADROES", nome: "Padrões", ordem: 3, entrada: 80, exclusoes: 10, saldo: 70, percentual_total_inicial: "10", percentual_saldo_recebido: "12.5", filtros: [filtro("PAD", 80, 10)] },
  ],
  fechamento: { equacao: "total_analisado = total_excluido + total_aprovado", lado_esquerdo: 100, lado_direito: 100, valido: true },
  detalhes_padroes: {
    limite_percentual: "10.000000", operador: "<",
    grupos: [
      { grupo_cod: "PG_001", grupo_nome: "Grupo 1", entrada: 80, exclusoes: 10, saldo: 70, reconciliado: true,
        padroes: [padrao("PD_003", "APLICADO_RARO", 80, 10, 70)] },
      { grupo_cod: "PG_002", grupo_nome: "Grupo 2", entrada: 70, exclusoes: 0, saldo: 70, reconciliado: true,
        padroes: [padrao("PD_005", "APLICADO_RARO", 70, 0, 70)] },
      { grupo_cod: "PG_003", grupo_nome: "Grupo 3", entrada: 70, exclusoes: 0, saldo: 70, reconciliado: true,
        padroes: [padrao("PD_009", "APLICADO_RARO", 70, 0, 70)] },
    ],
    fechamento: { entrada: 80, exclusoes: 10, saldo: 70, valido: true },
  },
  configuracao_raridade: {
    limite_percentual: "10.000000", operador: "<",
    padroes_selecionados: ["PD_003", "PD_005", "PD_009"],
  },
};

test("contrato aceita somente quadro reconciliado nas três famílias", () => {
  assert.deepEqual(CODIGOS_FAMILIAS, ["ESTATISTICA", "GEOMETRIA", "PADROES"]);
  assert.equal(validarQuadroExtensivel(quadro), true);
  assert.equal(validarQuadroExtensivel({ ...quadro, resumo: { ...quadro.resumo, total_aprovado: 71 } }), false);
  assert.equal(validarQuadroExtensivel({
    ...quadro,
    detalhes_padroes: {
      ...quadro.detalhes_padroes,
      fechamento: { ...quadro.detalhes_padroes.fechamento, saldo: 999 },
    },
  }), false);
});

test("interface explica que cadastro não substitui função Python", async () => {
  const html = await readFile(new URL("../screener-extensivel.html", import.meta.url), "utf8");
  const javascript = await readFile(new URL("../js/screener-extensivel.js", import.meta.url), "utf8");

  assert.match(html, /Cadastrar um padrão não cria seu filtro/);
  assert.match(html, /função Python, testes e integração validada/);
  assert.match(html, /Executar 5\.000/);
  assert.match(html, /id="limite-raridade-extensivel"/);
  assert.doesNotMatch(html, /dados inteiramente fictícios/i);
  assert.match(javascript, /Função Python validada/);
  assert.match(javascript, /fetch\s*\("\/api\/screener\/quadro-extensivel"/);
  assert.match(javascript, /limite_raridade/);
});
