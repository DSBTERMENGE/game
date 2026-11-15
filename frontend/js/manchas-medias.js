const FAIXAS_PERCENTUAIS = Object.freeze([20, 40, 60]);

function numeroFinito(valor, nome) {
  const numero = Number(valor);
  if (!Number.isFinite(numero)) throw new TypeError(`${nome} deve ser um número finito.`);
  return numero;
}

function normalizarPontos(pontos) {
  if (!Array.isArray(pontos) || pontos.length === 0) {
    throw new TypeError("A mancha exige ao menos uma coordenada.");
  }
  return pontos.map((ponto, indice) => ({
    x: numeroFinito(ponto?.x, `pontos[${indice}].x`),
    y: numeroFinito(ponto?.y, `pontos[${indice}].y`),
  }));
}

function calcularCentro(pontos) {
  const soma = pontos.reduce(
    (total, ponto) => ({ x: total.x + ponto.x, y: total.y + ponto.y }),
    { x: 0, y: 0 },
  );
  return { x: soma.x / pontos.length, y: soma.y / pontos.length };
}

function distancia(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function identificarFaixa(percentual) {
  if (percentual <= 20) return 0;
  if (percentual <= 40) return 1;
  if (percentual <= 60) return 2;
  return 3;
}

export function analisarManchaDeMedias(pontosRecebidos, fatorIntensidade = 0.12) {
  const pontos = normalizarPontos(pontosRecebidos);
  const fator = numeroFinito(fatorIntensidade, "fatorIntensidade");
  if (fator < 0 || fator > 1) throw new RangeError("O fator de intensidade deve estar entre 0 e 1.");

  const centro = calcularCentro(pontos);
  const distancias = pontos.map((ponto) => distancia(ponto, centro));
  const distanciaMaxima = Math.max(...distancias);
  const quantidades = [0, 0, 0, 0];
  const pontosAnalisados = pontos.map((ponto, indice) => {
    const distanciaCentro = distancias[indice];
    const proporcao = distanciaMaxima === 0 ? 0 : distanciaCentro / distanciaMaxima;
    const percentual = proporcao * 100;
    const faixa = identificarFaixa(percentual);
    quantidades[faixa] += 1;
    const concentracao = 1 - proporcao;
    return {
      ...ponto,
      distanciaCentro,
      percentualDistanciaMaxima: percentual,
      faixa,
      intensidade: Math.min(1, fator * (1 + concentracao)),
    };
  });

  const limites = [
    { de: 0, ate: 20 },
    { de: 20, ate: 40 },
    { de: 40, ate: 60 },
    { de: 60, ate: 100 },
  ];
  return {
    centro,
    distanciaCentroAOrigem: Math.hypot(centro.x, centro.y),
    distanciaMaxima,
    raios: Object.fromEntries(FAIXAS_PERCENTUAIS.map((nivel) => [nivel, distanciaMaxima * nivel / 100])),
    faixas: limites.map((limite, indice) => ({ ...limite, quantidade: quantidades[indice] })),
    pontos: pontosAnalisados,
    fatorIntensidade: fator,
  };
}

function textoObrigatorio(valor, nome) {
  if (typeof valor !== "string" || !valor.trim()) {
    throw new TypeError(`${nome} deve ser um texto não vazio.`);
  }
  return valor.trim();
}

export function prepararManchaDeMedia({
  identificador,
  pontos,
  cor,
  corReferencias,
  diametroMm,
  fatorIntensidade = 0.12,
}) {
  const nome = textoObrigatorio(identificador, "identificador");
  const corPontos = textoObrigatorio(cor, "cor");
  const corDosNiveis = textoObrigatorio(corReferencias, "corReferencias");
  const diametro = numeroFinito(diametroMm, "diametroMm");
  if (diametro <= 0) throw new RangeError("O diâmetro deve ser maior que zero.");

  const analise = analisarManchaDeMedias(pontos, fatorIntensidade);
  return {
    identificador: nome,
    centro: { ...analise.centro },
    distanciaCentroAOrigem: analise.distanciaCentroAOrigem,
    distanciaMaxima: analise.distanciaMaxima,
    fatorIntensidade: analise.fatorIntensidade,
    pontos: analise.pontos.map((ponto, indice) => ({
      ...ponto,
      indice,
      cor: corPontos,
      diametroMm: diametro,
    })),
    referencias: FAIXAS_PERCENTUAIS.map((percentual) => ({
      percentual,
      centro: { ...analise.centro },
      raio: analise.raios[percentual],
      cor: corDosNiveis,
    })),
    faixas: analise.faixas.map((faixa) => ({ ...faixa })),
  };
}

