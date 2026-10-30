import assert from "node:assert/strict";
import test from "node:test";

import {
  MEDICOES_FREQUENCIA, formatarMedicaoFrequencia, prepararBarrasFrequencia,
} from "../js/frequencia-graficos.js";

test("define os seis gráficos contratados com unidade explícita", () => {
  assert.deepEqual(MEDICOES_FREQUENCIA.map((item) => item.campo), [
    "quantidade_ocorrencias", "intervalo_minimo", "intervalo_maximo",
    "media_intervalos", "mediana_intervalos", "desvio_padrao_intervalos",
  ]);
  assert.equal(MEDICOES_FREQUENCIA[0].unidade, "ocorrências");
  assert.ok(MEDICOES_FREQUENCIA.slice(1).every((item) => item.unidade === "concursos"));
});

test("normaliza barras preservando ausência de intervalo", () => {
  const barras = prepararBarrasFrequencia([
    { dezena: 1, quantidade_intervalos: 0, media_intervalos: null },
    { dezena: 2, quantidade_intervalos: 1, media_intervalos: "5.000000" },
    { dezena: 3, quantidade_intervalos: 2, media_intervalos: "10.000000" },
  ], "media_intervalos");
  assert.deepEqual(barras.map((item) => item.valor), [null, 5, 10]);
  assert.deepEqual(barras.map((item) => item.proporcao), [0, 0.5, 1]);
  assert.equal(formatarMedicaoFrequencia(null, 2), "Sem intervalo suficiente");
  assert.equal(formatarMedicaoFrequencia(5, 2), "5,00");
});
