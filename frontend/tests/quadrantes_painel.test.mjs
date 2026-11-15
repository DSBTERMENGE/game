import assert from "node:assert/strict";
import test from "node:test";

import {
  calcularDimensoesDosQuadrados,
  calcularGeometriaDosEixos,
  calcularRetangulosDosQuadrantes,
  classificarQuadrantesPorQuantidade,
  classificarDezenaNoQuadrante,
  contarQuadrantes,
} from "../js/quadrantes-painel.js";

test("classifica as dezenas limítrofes nos quatro quadrantes", () => {
  const esperados = new Map([
    [6, 1], [10, 1], [16, 1], [20, 1], [26, 1], [30, 1],
    [1, 2], [5, 2], [11, 2], [15, 2], [21, 2], [25, 2],
    [31, 3], [35, 3], [41, 3], [45, 3], [51, 3], [55, 3],
    [36, 4], [40, 4], [46, 4], [50, 4], [56, 4], [60, 4],
  ]);
  esperados.forEach((quadrante, dezena) => {
    assert.equal(classificarDezenaNoQuadrante(dezena), quadrante, `dezena ${dezena}`);
  });
});

test("conta integralmente e calcula total, referência média e percentuais", () => {
  const analise = contarQuadrantes([
    { dezenas: [6, 1, 31, 36, 10, 5] },
    { dezenas: [16, 11, 41, 46, 20, 15] },
  ]);

  assert.equal(analise.concursos, 2);
  assert.equal(analise.total, 12);
  assert.equal(analise.referenciaMedia, 3);
  assert.deepEqual(analise.quadrantes.map((item) => item.quantidade), [4, 4, 2, 2]);
  const esperados = [100 / 3, 100 / 3, 100 / 6, 100 / 6];
  analise.quadrantes.forEach((item, indice) => {
    assert.ok(Math.abs(item.percentual - esperados[indice]) < 1e-12);
  });
});

test("aceita os seis campos res quando o vetor dezenas não está presente", () => {
  const analise = contarQuadrantes([{
    res_01: 6, res_02: 1, res_03: 31, res_04: 36, res_05: 10, res_06: 5,
  }]);
  assert.deepEqual(analise.quadrantes.map((item) => item.quantidade), [2, 2, 1, 1]);
});

test("recusa coleção vazia, dezenas inválidas, repetidas ou em quantidade errada", () => {
  assert.throws(() => contarQuadrantes([]), /ao menos um resultado/);
  assert.throws(() => contarQuadrantes([{ dezenas: [1, 2, 3] }]), /exatamente seis/);
  assert.throws(() => contarQuadrantes([{ dezenas: [1, 2, 3, 4, 5, 61] }]), /entre 1 e 60/);
  assert.throws(() => contarQuadrantes([{ dezenas: [1, 1, 2, 3, 4, 5] }]), /repetidas/);
  assert.throws(() => classificarDezenaNoQuadrante(0), /entre 1 e 60/);
});

test("calcula eixos pelas bordas das células e reserva afastamento", () => {
  const geometria = calcularGeometriaDosEixos({
    mapa: { left: 100, top: 50, width: 500, height: 300 },
    dezena05: { left: 300, top: 50, width: 48, height: 48 },
    dezena06: { left: 352, top: 50, width: 48, height: 48 },
    dezena21: { left: 100, top: 150, width: 48, height: 48 },
    dezena31: { left: 100, top: 202, width: 48, height: 48 },
  });
  assert.deepEqual(geometria.origem, { x: 250, y: 150 });
  assert.deepEqual(geometria.espessura, { vertical: 4, horizontal: 4 });
  assert.deepEqual(geometria.afastamento, { x: 4, y: 4 });
  assert.deepEqual(geometria.eixoVertical, { x: 248, y: 0, largura: 4, altura: 300 });
  assert.deepEqual(geometria.eixoHorizontal, { x: 0, y: 148, largura: 500, altura: 4 });
});

test("usa espessura mínima de um pixel quando as células são contíguas", () => {
  const geometria = calcularGeometriaDosEixos({
    mapa: { left: 0, top: 0, width: 400, height: 240 },
    dezena05: { left: 160, top: 0, width: 40, height: 40 },
    dezena06: { left: 200, top: 0, width: 40, height: 40 },
    dezena21: { left: 0, top: 80, width: 40, height: 40 },
    dezena31: { left: 0, top: 120, width: 40, height: 40 },
  });
  assert.deepEqual(geometria.origem, { x: 200, y: 120 });
  assert.deepEqual(geometria.espessura, { vertical: 1, horizontal: 1 });
  assert.deepEqual(geometria.afastamento, { x: 2.5, y: 2.5 });
});

test("calcula a escala dinâmica pela menor extensão disponível", () => {
  const analise = contarQuadrantes([
    { dezenas: [6, 1, 31, 36, 10, 5] },
    { dezenas: [16, 11, 41, 46, 20, 15] },
  ]);
  const geometria = calcularGeometriaDosEixos({
    mapa: { left: 100, top: 50, width: 500, height: 300 },
    dezena05: { left: 300, top: 50, width: 48, height: 48 },
    dezena06: { left: 352, top: 50, width: 48, height: 48 },
    dezena21: { left: 100, top: 150, width: 48, height: 48 },
    dezena31: { left: 100, top: 202, width: 48, height: 48 },
  });
  const dimensoes = calcularDimensoesDosQuadrados({ analise, geometria });

  assert.deepEqual(dimensoes.extensoes, {
    esquerda: 246,
    direita: 246,
    superior: 146,
    inferior: 146,
  });
  assert.equal(dimensoes.extensaoDisponivel, 146);
  assert.equal(dimensoes.referencia, 3);
  assert.equal(dimensoes.passo, 146 / 3 / 2);
  assert.deepEqual(
    dimensoes.quadrantes.map(({ quantidade }) => quantidade),
    [4, 4, 2, 2],
  );
  assert.deepEqual(
    dimensoes.quadrantes.map(({ lado }) => lado),
    [4, 4, 2, 2].map((quantidade) => quantidade * 146 / 3 / 2),
  );
});

test("recusa geometria sem espaço e análises de quadrantes inválidas", () => {
  const base = {
    analise: {
      referenciaMedia: 1,
      quadrantes: [1, 2, 3, 4].map((quadrante) => ({ quadrante, quantidade: 1 })),
    },
    geometria: {
      origem: { x: 50, y: 50 },
      afastamento: { x: 4, y: 4 },
      eixoHorizontal: { largura: 100 },
      eixoVertical: { altura: 100 },
    },
  };
  assert.doesNotThrow(() => calcularDimensoesDosQuadrados(base));
  assert.throws(
    () => calcularDimensoesDosQuadrados({
      ...base,
      analise: { ...base.analise, quadrantes: base.analise.quadrantes.slice(0, 3) },
    }),
    /exatamente quatro quadrantes/,
  );
  assert.throws(
    () => calcularDimensoesDosQuadrados({
      ...base,
      geometria: { ...base.geometria, origem: { x: 3, y: 50 } },
    }),
    /extensão esquerda/,
  );
});

test("posiciona um quadrado afastado dos eixos dentro de cada quadrante", () => {
  const geometria = {
    origem: { x: 200, y: 120 },
    afastamento: { x: 4, y: 5 },
  };
  const dimensoes = {
    quadrantes: [
      { quadrante: 1, quantidade: 10, lado: 50 },
      { quadrante: 2, quantidade: 9, lado: 45 },
      { quadrante: 3, quantidade: 8, lado: 40 },
      { quadrante: 4, quantidade: 7, lado: 35 },
    ],
  };

  assert.deepEqual(calcularRetangulosDosQuadrantes({ geometria, dimensoes }), [
    { quadrante: 1, quantidade: 10, x: 204, y: 65, largura: 50, altura: 50 },
    { quadrante: 2, quantidade: 9, x: 151, y: 70, largura: 45, altura: 45 },
    { quadrante: 3, quantidade: 8, x: 156, y: 125, largura: 40, altura: 40 },
    { quadrante: 4, quantidade: 7, x: 204, y: 125, largura: 35, altura: 35 },
  ]);
});

test("classifica por quantidade, aplica quatro cores e preserva empates", () => {
  const classificados = classificarQuadrantesPorQuantidade([
    { quantidade: 20, percentual: 20 },
    { quantidade: 10, percentual: 10 },
    { quantidade: 40, percentual: 40 },
    { quantidade: 30, percentual: 30 },
  ]);
  assert.deepEqual(classificados.map(({ posicao }) => posicao), [3, 4, 1, 2]);
  assert.deepEqual(classificados.map(({ cor }) => cor), [
    "#ca8a04", "#b91c1c", "#166534", "#8bb29a",
  ]);

  const empatados = classificarQuadrantesPorQuantidade([
    { quantidade: 30, percentual: 30 },
    { quantidade: 20, percentual: 20 },
    { quantidade: 30, percentual: 30 },
    { quantidade: 20, percentual: 20 },
  ]);
  assert.deepEqual(empatados.map(({ posicao }) => posicao), [1, 2, 1, 2]);
  assert.equal(empatados[0].cor, empatados[2].cor);
  assert.equal(empatados[1].cor, empatados[3].cor);
});
