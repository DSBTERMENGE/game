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

export function adicionarFaixaDesvioPadrao(pontos) {
  return pontos.map((ponto) => {
    const media = numero(ponto.media_intervalos);
    const desvio = numero(ponto.desvio_padrao_intervalos);
    return {
      ...ponto,
      media_menos_desvio: media === null || desvio === null ? null : media - desvio,
      media_mais_desvio: media === null || desvio === null ? null : media + desvio,
    };
  });
}

export function criarEscalasHistorico(periodo, dominio, largura = 960, altura = 245, margens = {}) {
  const esquerda = margens.esquerda ?? 52;
  const direita = largura - (margens.direita ?? 15);
  const topo = margens.topo ?? 14;
  const inferior = altura - (margens.inferior ?? 30);
  const amplitudeX = Math.max(1, periodo.concurso_final - periodo.concurso_inicial);
  const amplitudeY = dominio.maximo - dominio.minimo;
  return {
    x: (concurso) => esquerda + (concurso - periodo.concurso_inicial) * (direita - esquerda) / amplitudeX,
    y: (valor) => inferior - (valor - dominio.minimo) * (inferior - topo) / amplitudeY,
    esquerda, direita, topo, inferior, largura, altura,
  };
}

export function marcasEixoConcursos(periodo, pontos = [], camposDegrau = []) {
  const regulares = new Set([periodo.concurso_inicial, periodo.concurso_final]);
  const primeiroMultiplo = Math.ceil(periodo.concurso_inicial / 100) * 100;
  for (let concurso = primeiroMultiplo; concurso <= periodo.concurso_final; concurso += 100) regulares.add(concurso);
  const degraus = new Set();
  for (const campo of camposDegrau) {
    let anterior = null;
    for (const ponto of pontos) {
      const atual = numero(ponto[campo]);
      if (atual === null) continue;
      if (anterior !== null && atual !== anterior) degraus.add(Number(ponto.numero_do_concurso));
      anterior = atual;
    }
  }
  return { regulares: [...regulares].sort((a, b) => a - b), degraus: [...degraus].sort((a, b) => a - b) };
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

export function segmentosDegrausIntervalos(intervalos, escalas) {
  const horizontais = [];
  const transicoes = [];
  const validos = intervalos.filter((item) =>
    numero(item.concurso_anterior) !== null
    && numero(item.numero_do_concurso) !== null
    && numero(item.intervalo) !== null
    && numero(item.concurso_inicial_visivel) !== null
    && numero(item.concurso_final_visivel) !== null
  );
  for (const item of validos) {
    const xInicial = escalas.x(numero(item.concurso_inicial_visivel));
    const xFinal = escalas.x(numero(item.concurso_final_visivel));
    const y = escalas.y(numero(item.intervalo));
    horizontais.push({
      item,
      larguraProjetada: Math.abs(xFinal - xInicial),
      caminho: `M${xInicial.toFixed(2)},${y.toFixed(2)} L${xFinal.toFixed(2)},${y.toFixed(2)}`,
    });
  }
  for (let indice = 0; indice < validos.length - 1; indice += 1) {
    const anterior = validos[indice], seguinte = validos[indice + 1];
    if (numero(anterior.numero_do_concurso) !== numero(seguinte.concurso_anterior)
        || numero(anterior.intervalo) === numero(seguinte.intervalo)) continue;
    const x = escalas.x(numero(anterior.numero_do_concurso));
    transicoes.push({
      concurso: numero(anterior.numero_do_concurso), anterior, seguinte,
      caminho: `M${x.toFixed(2)},${escalas.y(numero(anterior.intervalo)).toFixed(2)} L${x.toFixed(2)},${escalas.y(numero(seguinte.intervalo)).toFixed(2)}`,
    });
  }
  return { horizontais, transicoes };
}

export function poligonoFaixaHistorico(pontos, campoInferior, campoSuperior, escalas) {
  const validos = pontos.filter((ponto) => numero(ponto[campoInferior]) !== null && numero(ponto[campoSuperior]) !== null);
  if (validos.length === 0) return "";
  const inferior = validos.map((ponto) => `${escalas.x(ponto.numero_do_concurso).toFixed(2)},${escalas.y(numero(ponto[campoInferior])).toFixed(2)}`);
  const superior = [...validos].reverse().map((ponto) => `${escalas.x(ponto.numero_do_concurso).toFixed(2)},${escalas.y(numero(ponto[campoSuperior])).toFixed(2)}`);
  return [...inferior, ...superior].join(" ");
}
