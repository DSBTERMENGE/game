function numero(valor) {
  if (valor === null || valor === undefined || valor === "") return null;
  const convertido = Number(valor);
  return Number.isFinite(convertido) ? convertido : null;
}

export function dominioHistorico(pontos, campos, adicionais = []) {
  const valores = adicionais.map(numero).filter((valor) => valor !== null);
  for (const ponto of pontos) {
    for (const campo of campos) {
      const valor = numero(ponto[campo]);
      if (valor !== null) valores.push(valor);
    }
  }
  if (valores.length === 0) return null;
  let minimo = Math.min(...valores), maximo = Math.max(...valores);
  if (minimo === maximo) { minimo -= 1; maximo += 1; }
  const margem = (maximo - minimo) * 0.05;
  return { minimo: minimo - margem, maximo: maximo + margem };
}

export function ampliarDominioHistorico(dominio, fator = 10) {
  const ampliacao = Number(fator);
  if (!dominio || !Number.isFinite(ampliacao) || ampliacao <= 1) return dominio;
  const centro = (dominio.minimo + dominio.maximo) / 2;
  const meiaAmplitude = (dominio.maximo - dominio.minimo) / (2 * ampliacao);
  return { minimo: centro - meiaAmplitude, maximo: centro + meiaAmplitude };
}

export function contarValoresForaDominio(pontos, campos, dominio, adicionais = []) {
  if (!dominio) return 0;
  let total = 0;
  for (const valorOriginal of adicionais) {
    const valor = numero(valorOriginal);
    if (valor !== null && (valor < dominio.minimo || valor > dominio.maximo)) total += 1;
  }
  for (const ponto of pontos) {
    for (const campo of campos) {
      const valor = numero(ponto[campo]);
      if (valor !== null && (valor < dominio.minimo || valor > dominio.maximo)) total += 1;
    }
  }
  return total;
}

export function criarEscalasHistorico(periodo, dominio, largura = 960, altura = 245) {
  const esquerda = 52, direita = largura - 15, topo = 14, inferior = altura - 30;
  const amplitudeX = Math.max(1, periodo.concurso_final - periodo.concurso_inicial);
  const amplitudeY = dominio.maximo - dominio.minimo;
  return {
    x: (concurso) => esquerda + (concurso - periodo.concurso_inicial) * (direita - esquerda) / amplitudeX,
    y: (valor) => inferior - (valor - dominio.minimo) * (inferior - topo) / amplitudeY,
    esquerda, direita, topo, inferior, largura, altura,
  };
}

export function caminhoHistorico(pontos, campo, escalas) {
  let caminho = "", desenhando = false;
  for (const ponto of pontos) {
    const valor = numero(ponto[campo]);
    if (valor === null) { desenhando = false; continue; }
    caminho += `${desenhando ? " L" : "M"}${escalas.x(ponto.numero_do_concurso).toFixed(2)},${escalas.y(valor).toFixed(2)}`;
    desenhando = true;
  }
  return caminho;
}

export function poligonoFaixaHistorico(pontos, campoInferior, campoSuperior, escalas) {
  const validos = pontos.filter((ponto) => numero(ponto[campoInferior]) !== null && numero(ponto[campoSuperior]) !== null);
  if (validos.length === 0) return "";
  const inferior = validos.map((ponto) => `${escalas.x(ponto.numero_do_concurso).toFixed(2)},${escalas.y(numero(ponto[campoInferior])).toFixed(2)}`);
  const superior = [...validos].reverse().map((ponto) => `${escalas.x(ponto.numero_do_concurso).toFixed(2)},${escalas.y(numero(ponto[campoSuperior])).toFixed(2)}`);
  return [...inferior, ...superior].join(" ");
}
