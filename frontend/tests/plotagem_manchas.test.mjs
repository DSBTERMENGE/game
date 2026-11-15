import assert from "node:assert/strict";
import test from "node:test";

import { plotarCirculo } from "../js/plotagem-manchas.js";


class CirculoFalso {
  constructor() { this.atributos = {}; }
  setAttribute(nome, valor) { this.atributos[nome] = String(valor); }
}

function prepararDocumento() {
  const anterior = globalThis.document;
  globalThis.document = { createElementNS: () => new CirculoFalso() };
  return () => { globalThis.document = anterior; };
}

function destinoFalso() {
  return { filhos: [], append(item) { this.filhos.push(item); } };
}

test("plota um círculo com coordenada decimal exata, cor, diâmetro e intensidade", () => {
  const restaurar = prepararDocumento();
  try {
    const destino = destinoFalso();
    const circulo = plotarCirculo({
      destino,
      coordenada: { x: 4.497284674704, y: 2.501846421201 },
      converterCoordenada: ({ x, y }) => ({ x: 10 + x * 50, y: 20 + y * 40 }),
      diametroMm: 3,
      cor: "#6f4e37",
      intensidade: 0.12,
      classe: "mancha-media-espacial",
    });
    assert.equal(destino.filhos.length, 1);
    assert.equal(circulo.atributos.cx, String(10 + 4.497284674704 * 50));
    assert.equal(circulo.atributos.cy, String(20 + 2.501846421201 * 40));
    assert.equal(Number(circulo.atributos.r), (3 / 25.4) * 96 / 2);
    assert.equal(circulo.atributos.fill, "#6f4e37");
    assert.equal(circulo.atributos["fill-opacity"], "0.12");
    assert.equal(circulo.atributos.class, "mancha-media-espacial");
  } finally { restaurar(); }
});

test("coordenadas coincidentes geram círculos independentes na mesma posição", () => {
  const restaurar = prepararDocumento();
  try {
    const destino = destinoFalso();
    const parametros = {
      destino,
      coordenada: { x: 2.5, y: 3.25 },
      converterCoordenada: ({ x, y }) => ({ x, y }),
      diametroMm: 3,
      cor: "brown",
      intensidade: 0.2,
    };
    plotarCirculo(parametros);
    plotarCirculo(parametros);
    assert.equal(destino.filhos.length, 2);
    assert.equal(destino.filhos[0].atributos.cx, destino.filhos[1].atributos.cx);
    assert.equal(destino.filhos[0].atributos.cy, destino.filhos[1].atributos.cy);
  } finally { restaurar(); }
});

test("não arredonda a coordenada antes de entregá-la ao conversor", () => {
  const restaurar = prepararDocumento();
  try {
    let recebida;
    plotarCirculo({
      destino: destinoFalso(),
      coordenada: { x: 1 / 6, y: 5 / 6 },
      converterCoordenada: (coordenada) => { recebida = coordenada; return coordenada; },
      diametroMm: 2,
      cor: "#123456",
      intensidade: 0.5,
    });
    assert.deepEqual(recebida, { x: 1 / 6, y: 5 / 6 });
  } finally { restaurar(); }
});

test("recusa destino, conversor, coordenadas, diâmetro, cor e intensidade inválidos", () => {
  const restaurar = prepararDocumento();
  const base = {
    destino: destinoFalso(), coordenada: { x: 1, y: 2 },
    converterCoordenada: (ponto) => ponto, diametroMm: 3, cor: "brown", intensidade: 0.12,
  };
  try {
    assert.throws(() => plotarCirculo({ ...base, destino: null }), /destino/);
    assert.throws(() => plotarCirculo({ ...base, converterCoordenada: null }), /conversão/);
    assert.throws(() => plotarCirculo({ ...base, coordenada: { x: NaN, y: 2 } }), /finito/);
    assert.throws(() => plotarCirculo({ ...base, diametroMm: 0 }), /maior que zero/);
    assert.throws(() => plotarCirculo({ ...base, cor: "" }), /cor/);
    assert.throws(() => plotarCirculo({ ...base, intensidade: 1.1 }), /entre 0 e 1/);
  } finally { restaurar(); }
});

