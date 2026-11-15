import assert from "node:assert/strict";
import test from "node:test";

import { analisarManchaDeMedias, prepararManchaDeMedia } from "../js/manchas-medias.js";


test("calcula centro, origem, distâncias e raios sem arredondar coordenadas", () => {
  const analise = analisarManchaDeMedias([
    { x: 0, y: 0 },
    { x: 2, y: 0 },
    { x: 0, y: 2 },
    { x: 2, y: 2 },
  ]);

  assert.deepEqual(analise.centro, { x: 1, y: 1 });
  assert.equal(analise.distanciaCentroAOrigem, Math.SQRT2);
  assert.equal(analise.distanciaMaxima, Math.SQRT2);
  assert.ok(Math.abs(analise.raios[20] - Math.SQRT2 * 0.2) < 1e-12);
  assert.ok(Math.abs(analise.raios[40] - Math.SQRT2 * 0.4) < 1e-12);
  assert.ok(Math.abs(analise.raios[60] - Math.SQRT2 * 0.6) < 1e-12);
  assert.deepEqual(analise.faixas.map((faixa) => faixa.quantidade), [0, 0, 0, 4]);
});

test("classifica os limites de 20, 40 e 60 por distância ao centro", () => {
  const analise = analisarManchaDeMedias([
    { x: -10, y: 0 }, { x: -6, y: 0 }, { x: -4, y: 0 }, { x: -2, y: 0 },
    { x: 2, y: 0 }, { x: 4, y: 0 }, { x: 6, y: 0 }, { x: 10, y: 0 },
  ]);
  assert.deepEqual(analise.faixas.map((faixa) => faixa.quantidade), [2, 2, 2, 2]);
});

test("fator preserva pontos externos e escurece toda a mancha proporcionalmente", () => {
  const pontos = [{ x: -1, y: 0 }, { x: 0, y: 0 }, { x: 1, y: 0 }];
  const inicial = analisarManchaDeMedias(pontos, 0.12);
  const ampliada = analisarManchaDeMedias(pontos, 0.24);

  assert.deepEqual(inicial.pontos.map((ponto) => ponto.intensidade), [0.12, 0.24, 0.12]);
  assert.deepEqual(ampliada.pontos.map((ponto) => ponto.intensidade), [0.24, 0.48, 0.24]);
});

test("usa o fator informado em vez de fixar o padrão 0,12", () => {
  const configurada = prepararManchaDeMedia({
    identificador: "media-espacial",
    pontos: [{ x: -1, y: 0 }, { x: 0, y: 0 }, { x: 1, y: 0 }],
    cor: "#8b4513",
    corReferencias: "#f1c40f",
    diametroMm: 3,
    fatorIntensidade: 0.18,
  });

  assert.deepEqual(configurada.pontos.map((ponto) => ponto.intensidade), [0.18, 0.36, 0.18]);
  assert.equal(configurada.fatorIntensidade, 0.18);
});

test("pontos coincidentes permanecem individuais e visíveis", () => {
  const analise = analisarManchaDeMedias([
    { x: 2.5, y: 3.25 },
    { x: 2.5, y: 3.25 },
  ]);
  assert.equal(analise.pontos.length, 2);
  assert.deepEqual(analise.centro, { x: 2.5, y: 3.25 });
  assert.equal(analise.pontos[0].intensidade, 0.24);
  assert.equal(analise.pontos[1].intensidade, 0.24);
});

test("recusa conjunto vazio, coordenadas inválidas e fator fora do limite", () => {
  assert.throws(() => analisarManchaDeMedias([]), /ao menos uma/);
  assert.throws(() => analisarManchaDeMedias([{ x: "x", y: 0 }]), /número finito/);
  assert.throws(() => analisarManchaDeMedias([{ x: 0, y: 0 }], 1.1), /entre 0 e 1/);
});

test("prepara Média espacial, CG1 e CG2 pelo mesmo cálculo comum", () => {
  const pontos = [{ x: 1.125, y: 2.375 }, { x: 4.625, y: 5.875 }];
  const definicoes = [
    ["media-espacial", "#8b4513"],
    ["cg1", "#7566d9"],
    ["cg2", "#2471a3"],
  ];

  definicoes.forEach(([identificador, cor]) => {
    const mancha = prepararManchaDeMedia({
      identificador,
      pontos,
      cor,
      corReferencias: "#f1c40f",
      diametroMm: 3,
      fatorIntensidade: 0.12,
    });
    assert.equal(mancha.identificador, identificador);
    assert.equal(mancha.pontos.length, pontos.length);
    assert.deepEqual(
      mancha.pontos.map(({ x, y }) => ({ x, y })),
      pontos,
    );
    assert.ok(mancha.pontos.every((ponto) => ponto.cor === cor && ponto.diametroMm === 3));
    assert.deepEqual(mancha.referencias.map((item) => item.percentual), [20, 40, 60]);
    assert.ok(mancha.referencias.every((item) => item.cor === "#f1c40f"));
  });
});

test("mantém pontos coincidentes individuais na preparação comum", () => {
  const mancha = prepararManchaDeMedia({
    identificador: "cg1",
    pontos: [{ x: 2.125, y: 3.875 }, { x: 2.125, y: 3.875 }],
    cor: "#7566d9",
    corReferencias: "#f1c40f",
    diametroMm: 2.5,
    fatorIntensidade: 0.2,
  });

  assert.equal(mancha.pontos.length, 2);
  assert.deepEqual(mancha.pontos.map((ponto) => ponto.indice), [0, 1]);
  assert.deepEqual(mancha.pontos.map((ponto) => ponto.intensidade), [0.4, 0.4]);
});

test("recusa parâmetros visuais inválidos na preparação comum", () => {
  const base = {
    identificador: "media-espacial",
    pontos: [{ x: 1, y: 1 }],
    cor: "#8b4513",
    corReferencias: "#f1c40f",
    diametroMm: 3,
  };
  assert.throws(() => prepararManchaDeMedia({ ...base, identificador: "" }), /identificador/);
  assert.throws(() => prepararManchaDeMedia({ ...base, cor: "" }), /cor deve/);
  assert.throws(() => prepararManchaDeMedia({ ...base, corReferencias: "" }), /corReferencias/);
  assert.throws(() => prepararManchaDeMedia({ ...base, diametroMm: 0 }), /maior que zero/);
});

