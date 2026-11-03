import assert from "node:assert/strict";
import test from "node:test";

import {
  adicionarFaixaDesvioPadrao, caminhoHistorico, criarEscalasHistorico, dominioHistorico,
  marcasEixoConcursos, poligonoFaixaHistorico, segmentosDegrausIntervalos,
} from "../js/frequencia-historico.js";

test("calcula as duas linhas de um desvio-padrão sem converter unidade", () => {
  const calculados = adicionarFaixaDesvioPadrao([
    { numero_do_concurso: 500, media_intervalos: "10.5", desvio_padrao_intervalos: "2.25" },
    { numero_do_concurso: 501, media_intervalos: null, desvio_padrao_intervalos: "2" },
  ]);
  assert.equal(calculados[0].media_menos_desvio, 8.25);
  assert.equal(calculados[0].media_mais_desvio, 12.75);
  assert.equal(calculados[1].media_menos_desvio, null);
  assert.equal(calculados[1].media_mais_desvio, null);
});

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

test("eixo horizontal marca centenas, extremos e mudanças de degrau", () => {
  const marcas = marcasEixoConcursos(
    { concurso_inicial: 550, concurso_final: 825 },
    [
      { numero_do_concurso: 550, minimo: 1, maximo: 40 },
      { numero_do_concurso: 600, minimo: 1, maximo: 40 },
      { numero_do_concurso: 617, minimo: 2, maximo: 45 },
    ],
    ["minimo", "maximo"],
  );
  assert.deepEqual(marcas.regulares, [550, 600, 700, 800, 825]);
  assert.deepEqual(marcas.degraus, [617]);
});

test("intervalos formam patamares reais e transições somente quando o valor muda", () => {
  const escalas = criarEscalasHistorico(
    { concurso_inicial: 500, concurso_final: 530 },
    { minimo: 0, maximo: 30 }, 960, 245,
  );
  const resultado = segmentosDegrausIntervalos([
    { concurso_anterior: 492, numero_do_concurso: 507, intervalo: 15, concurso_inicial_visivel: 500, concurso_final_visivel: 507 },
    { concurso_anterior: 507, numero_do_concurso: 520, intervalo: 13, concurso_inicial_visivel: 507, concurso_final_visivel: 520 },
    { concurso_anterior: 520, numero_do_concurso: 533, intervalo: 13, concurso_inicial_visivel: 520, concurso_final_visivel: 530 },
  ], escalas);
  assert.equal(resultado.horizontais.length, 3);
  assert.equal(resultado.transicoes.length, 1);
  assert.equal(resultado.transicoes[0].concurso, 507);
  assert.ok(resultado.horizontais[0].larguraProjetada > 8);
  assert.match(resultado.horizontais[0].caminho, /^M/);
  assert.doesNotMatch(resultado.horizontais[0].caminho, /NaN/);
});

test("largura projetada permite identificar intervalo curto sem mover coordenadas", () => {
  const escalas = criarEscalasHistorico(
    { concurso_inicial: 500, concurso_final: 3069 },
    { minimo: 0, maximo: 30 }, 1440, 500, { esquerda: 72, direita: 20 },
  );
  const resultado = segmentosDegrausIntervalos([
    { concurso_anterior: 700, numero_do_concurso: 701, intervalo: 1, concurso_inicial_visivel: 700, concurso_final_visivel: 701 },
  ], escalas);
  assert.ok(resultado.horizontais[0].larguraProjetada < 8);
  assert.equal(resultado.horizontais[0].item.concurso_anterior, 700);
  assert.equal(resultado.horizontais[0].item.numero_do_concurso, 701);
});

test("escala integral distingue casos curtos de 1, 2, 3 e 10 do intervalo longo", () => {
  const escalas = criarEscalasHistorico(
    { concurso_inicial: 500, concurso_final: 3069 },
    { minimo: 0, maximo: 60 }, 1440, 500, { esquerda: 72, direita: 20 },
  );
  let inicio = 600;
  const intervalos = [1, 2, 3, 10, 40].map((intervalo) => {
    const item = {
      concurso_anterior: inicio, numero_do_concurso: inicio + intervalo,
      intervalo, concurso_inicial_visivel: inicio,
      concurso_final_visivel: inicio + intervalo,
    };
    inicio += intervalo;
    return item;
  });
  const resultado = segmentosDegrausIntervalos(intervalos, escalas);
  assert.deepEqual(
    resultado.horizontais.map((item) => item.larguraProjetada < 8),
    [true, true, true, true, false],
  );
  assert.ok(resultado.horizontais.every((item) => !item.caminho.includes("NaN")));
});
