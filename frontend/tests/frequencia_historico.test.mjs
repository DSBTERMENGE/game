import assert from "node:assert/strict";
import test from "node:test";

import {
  ampliarDominioHistorico, caminhoHistorico, contarValoresForaDominio,
  criarEscalasHistorico, dominioHistorico, poligonoFaixaHistorico,
} from "../js/frequencia-historico.js";

const pontos = [
  { numero_do_concurso: 500, media_intervalos: null, limite_inferior_exato: null, limite_superior_exato: null },
  { numero_do_concurso: 501, media_intervalos: "10", limite_inferior_exato: "510", limite_superior_exato: "520" },
  { numero_do_concurso: 502, media_intervalos: "12", limite_inferior_exato: "512", limite_superior_exato: "524" },
];

test("domínio histórico ignora nulos e inclui ocorrências reais", () => {
  const dominio = dominioHistorico(pontos, ["limite_inferior_exato", "limite_superior_exato"], [501, 525]);
  assert.ok(dominio.minimo < 501);
  assert.ok(dominio.maximo > 525);
});

test("caminho começa somente quando existe valor e usa concurso no eixo X", () => {
  const dominio = dominioHistorico(pontos, ["media_intervalos"]);
  const escalas = criarEscalasHistorico({ concurso_inicial: 500, concurso_final: 502 }, dominio);
  const caminho = caminhoHistorico(pontos, "media_intervalos", escalas);
  assert.match(caminho, /^M/);
  assert.match(caminho, / L/);
  assert.equal((caminho.match(/[ML]/g) || []).length, 2);
});

test("faixa estatística gera polígono somente com pontos completos", () => {
  const dominio = dominioHistorico(pontos, ["limite_inferior_exato", "limite_superior_exato"]);
  const escalas = criarEscalasHistorico({ concurso_inicial: 500, concurso_final: 502 }, dominio);
  const poligono = poligonoFaixaHistorico(pontos, "limite_inferior_exato", "limite_superior_exato", escalas);
  assert.equal(poligono.split(" ").length, 4);
});

test("ampliação 10x reduz o domínio ao redor do mesmo centro sem alterar valores", () => {
  const dominio = { minimo: 0, maximo: 100 };
  const ampliado = ampliarDominioHistorico(dominio, 10);
  assert.deepEqual(ampliado, { minimo: 45, maximo: 55 });
  assert.deepEqual(dominio, { minimo: 0, maximo: 100 });
});

test("conta valores recortados pelo domínio ampliado", () => {
  const total = contarValoresForaDominio(
    [{ valor: 10 }, { valor: 50 }, { valor: 90 }, { valor: null }],
    ["valor"], { minimo: 45, maximo: 55 }, [44, 51, 56],
  );
  assert.equal(total, 4);
});
