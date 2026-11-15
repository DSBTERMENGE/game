const TOTAL_DEZENAS = 60;
const TOTAL_COLUNAS = 4;
const DEZENAS_POR_COLUNA = TOTAL_DEZENAS / TOTAL_COLUNAS;

export function contarOcorrenciasDasDezenas(dezenasPorResultado) {
  if (!Array.isArray(dezenasPorResultado)) {
    throw new TypeError("As dezenas dos resultados devem ser fornecidas em uma lista.");
  }
  const quantidades = Array(TOTAL_DEZENAS).fill(0);
  dezenasPorResultado.forEach((dezenas, indice) => {
    if (!Array.isArray(dezenas) || dezenas.length !== 6) {
      throw new TypeError(`O resultado ${indice + 1} deve possuir exatamente seis dezenas.`);
    }
    dezenas.forEach((valor) => {
      const dezena = Number(valor);
      if (!Number.isInteger(dezena) || dezena < 1 || dezena > TOTAL_DEZENAS) {
        throw new RangeError(`O resultado ${indice + 1} possui dezena inválida.`);
      }
      quantidades[dezena - 1] += 1;
    });
  });
  return quantidades.map((quantidade, indice) => ({
    dezena: indice + 1,
    quantidade,
  }));
}

export function organizarOcorrenciasEmColunas(ocorrencias) {
  if (!Array.isArray(ocorrencias) || ocorrencias.length !== TOTAL_DEZENAS) {
    throw new TypeError("A organização exige as ocorrências das 60 dezenas.");
  }
  return Array.from({ length: TOTAL_COLUNAS }, (_, coluna) => (
    ocorrencias.slice(
      coluna * DEZENAS_POR_COLUNA,
      (coluna + 1) * DEZENAS_POR_COLUNA,
    )
  ));
}

export function prepararOcorrenciasDasDezenas(dezenasPorResultado) {
  const ocorrencias = contarOcorrenciasDasDezenas(dezenasPorResultado);
  return {
    ocorrencias,
    colunas: organizarOcorrenciasEmColunas(ocorrencias),
    total: ocorrencias.reduce((soma, item) => soma + item.quantidade, 0),
  };
}
