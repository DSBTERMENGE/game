const TIPOS_EVENTO = new Set(["SIMPLES", "2VS", "3VS"]);

function inteiroValido(valor, minimo = 1, maximo = Number.MAX_SAFE_INTEGER) {
  const numero = Number.parseInt(String(valor), 10);
  return Number.isInteger(numero) && numero >= minimo && numero <= maximo ? String(numero) : null;
}

export function normalizarFiltrosGraficos(filtros) {
  const dezena = inteiroValido(filtros?.dezena, 1, 60);
  const tipo_evento = TIPOS_EVENTO.has(filtros?.tipo_evento) ? filtros.tipo_evento : null;
  const concurso_inicial = inteiroValido(filtros?.concurso_inicial);
  const concurso_final = inteiroValido(filtros?.concurso_final);
  if (!dezena || !tipo_evento || !concurso_inicial || !concurso_final) return null;
  if (Number(concurso_final) < Number(concurso_inicial)) return null;
  return { dezena, tipo_evento, concurso_inicial, concurso_final };
}

export function filtrosGraficosDaUrl(consulta) {
  const parametros = new URLSearchParams(consulta || "");
  return normalizarFiltrosGraficos(Object.fromEntries(parametros.entries()));
}

function consultaDosFiltros(filtros) {
  const normalizados = normalizarFiltrosGraficos(filtros);
  if (!normalizados) throw new Error("Os filtros do gráfico são inválidos.");
  return new URLSearchParams(normalizados).toString();
}

export function urlGraficosFrequencias(filtros) {
  return `/graficos-frequencias.html?${consultaDosFiltros(filtros)}`;
}

export function urlRetornoFrequencias(filtros) {
  return `/frequencias.html?${consultaDosFiltros(filtros)}#evolucao-historica-dezena`;
}
