function valorIntervalo(item) {
  const valor = Number(typeof item === "object" && item !== null ? item.intervalo : item);
  if (!Number.isInteger(valor) || valor <= 0) {
    throw new RangeError("Cada intervalo deve ser um inteiro positivo em concursos.");
  }
  return valor;
}

function cdfNormalPadrao(valor) {
  const sinal = valor < 0 ? -1 : 1;
  const x = Math.abs(valor) / Math.sqrt(2);
  const t = 1 / (1 + 0.3275911 * x);
  const erf = 1 - (((((1.061405429 * t - 1.453152027) * t)
    + 1.421413741) * t - 0.284496736) * t + 0.254829592)
    * t * Math.exp(-x * x);
  return 0.5 * (1 + sinal * erf);
}

function percentualNormalNoInteiro(intervalo, media, desvioPadrao) {
  if (desvioPadrao === 0) return null;
  const inferior = (intervalo - 0.5 - media) / desvioPadrao;
  const superior = (intervalo + 0.5 - media) / desvioPadrao;
  return (cdfNormalPadrao(superior) - cdfNormalPadrao(inferior)) * 100;
}

export function prepararIntervalosAuxiliares(intervalosOriginais) {
  if (!Array.isArray(intervalosOriginais)) {
    throw new TypeError("intervalos deve ser uma lista.");
  }
  const intervalos = intervalosOriginais.map(valorIntervalo);
  const total = intervalos.length;
  if (total === 0) {
    return {
      total: 0, menorIntervalo: null, maiorIntervalo: null,
      media: null, desvioPadrao: null, limiteInferiorDesvio: null,
      limiteSuperiorDesvio: null, distribuicao: [], ordenados: [],
    };
  }

  const menorIntervalo = Math.min(...intervalos);
  const maiorIntervalo = Math.max(...intervalos);
  const media = intervalos.reduce((soma, valor) => soma + valor, 0) / total;
  const variancia = intervalos.reduce(
    (soma, valor) => soma + ((valor - media) ** 2), 0,
  ) / total;
  const desvioPadrao = Math.sqrt(variancia);
  const contagens = new Map();
  for (const intervalo of intervalos) {
    contagens.set(intervalo, (contagens.get(intervalo) || 0) + 1);
  }

  const distribuicao = [];
  for (let intervalo = 1; intervalo <= maiorIntervalo; intervalo += 1) {
    const quantidade = contagens.get(intervalo) || 0;
    distribuicao.push({
      intervalo,
      quantidade,
      percentual: quantidade / total * 100,
      percentualNormal: percentualNormalNoInteiro(intervalo, media, desvioPadrao),
    });
  }

  const ordenados = [...intervalos].sort((a, b) => a - b).map(
    (intervalo, indice) => ({
      ordem: indice + 1,
      intervalo,
      percentualOcorrencias: (indice + 1) / total * 100,
      percentualMaiorIntervalo: intervalo / maiorIntervalo * 100,
    }),
  );

  return {
    total, menorIntervalo, maiorIntervalo, media, desvioPadrao,
    limiteInferiorDesvio: media - desvioPadrao,
    limiteSuperiorDesvio: media + desvioPadrao,
    distribuicao, ordenados,
  };
}
