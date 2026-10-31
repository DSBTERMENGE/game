import assert from "node:assert/strict";
import test from "node:test";
import {
  filtrosGraficosDaUrl,
  normalizarFiltrosGraficos,
  urlGraficosFrequencias,
  urlRetornoFrequencias,
} from "../js/navegacao-graficos-frequencias.js";

const filtros = { dezena: "17", tipo_evento: "3VS", concurso_inicial: "500", concurso_final: "3069" };

test("normaliza e recupera filtros válidos da navegação", () => {
  assert.deepEqual(normalizarFiltrosGraficos(filtros), filtros);
  assert.deepEqual(filtrosGraficosDaUrl("?dezena=17&tipo_evento=3VS&concurso_inicial=500&concurso_final=3069"), filtros);
});

test("rejeita dezena, evento ou período inválido", () => {
  assert.equal(normalizarFiltrosGraficos({ ...filtros, dezena: "61" }), null);
  assert.equal(normalizarFiltrosGraficos({ ...filtros, tipo_evento: "OUTRO" }), null);
  assert.equal(normalizarFiltrosGraficos({ ...filtros, concurso_final: "499" }), null);
});

test("constrói destinos de ida e retorno ao bloco de origem", () => {
  assert.equal(urlGraficosFrequencias(filtros), "/graficos-frequencias.html?dezena=17&tipo_evento=3VS&concurso_inicial=500&concurso_final=3069");
  assert.equal(urlRetornoFrequencias(filtros), "/frequencias.html?dezena=17&tipo_evento=3VS&concurso_inicial=500&concurso_final=3069#evolucao-historica-dezena");
});
