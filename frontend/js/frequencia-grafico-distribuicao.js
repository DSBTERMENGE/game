const SVG_NS = "http://www.w3.org/2000/svg";

function svgElemento(nome, atributos = {}) {
  const elemento = document.createElementNS(SVG_NS, nome);
  for (const [chave, valor] of Object.entries(atributos)) {
    elemento.setAttribute(chave, String(valor));
  }
  return elemento;
}

function passoBonito(amplitude, alvo = 8) {
  if (!(amplitude > 0)) return 1;
  const bruto = amplitude / alvo;
  const potencia = 10 ** Math.floor(Math.log10(bruto));
  const normalizado = bruto / potencia;
  const fator = normalizado <= 1 ? 1 : normalizado <= 2 ? 2 : normalizado <= 5 ? 5 : 10;
  return fator * potencia;
}

function marcasNumericas(inicio, fim, passo) {
  const marcas = [];
  const primeira = Math.ceil(inicio / passo) * passo;
  for (let valor = primeira; valor <= fim + passo * 1e-9; valor += passo) {
    marcas.push(Number(valor.toFixed(10)));
  }
  if (!marcas.includes(inicio)) marcas.unshift(inicio);
  if (!marcas.includes(fim)) marcas.push(fim);
  return [...new Set(marcas)].sort((a, b) => a - b);
}

function caminho(pontos) {
  return pontos.map((ponto, indice) => (
    `${indice === 0 ? "M" : "L"}${ponto.x.toFixed(2)},${ponto.y.toFixed(2)}`
  )).join(" ");
}

export function geometriaCurvaDistribuicao(dados, largura = 1440, altura = 650) {
  if (!dados || dados.total <= 0 || dados.distribuicao.length === 0) return null;
  const margens = { esquerda: 88, direita: 28, topo: 44, inferior: 72 };
  const esquerda = margens.esquerda, direita = largura - margens.direita;
  const topo = margens.topo, inferior = altura - margens.inferior;
  const xMin = 1, xMax = dados.maiorIntervalo;
  const valoresY = dados.distribuicao.flatMap((item) => [
    item.percentual,
    item.percentualNormal === null ? 0 : item.percentualNormal,
  ]);
  const yMaxDados = Math.max(...valoresY, 1);
  const passoY = passoBonito(yMaxDados, 6);
  const yMax = Math.ceil(yMaxDados / passoY) * passoY;
  const amplitudeX = Math.max(1, xMax - xMin);
  const escalaX = (valor) => esquerda + (valor - xMin) * (direita - esquerda) / amplitudeX;
  const escalaY = (valor) => inferior - valor * (inferior - topo) / yMax;
  const passoX = Math.max(1, Math.round(passoBonito(Math.max(1, xMax - xMin), 12)));
  const marcasX = marcasNumericas(xMin, xMax, passoX);
  const marcasY = marcasNumericas(0, yMax, passoY);
  const reais = dados.distribuicao.map((item) => ({
    ...item, x: escalaX(item.intervalo), y: escalaY(item.percentual),
  }));
  const normais = dados.distribuicao
    .filter((item) => item.percentualNormal !== null)
    .map((item) => ({
      ...item, x: escalaX(item.intervalo), y: escalaY(item.percentualNormal),
    }));
  const marcador = (valor, tipo) => (
    valor >= xMin && valor <= xMax
      ? { tipo, valor, x: escalaX(valor), topo, inferior }
      : null
  );
  return {
    largura, altura, esquerda, direita, topo, inferior, xMin, xMax, yMax,
    marcasX, marcasY, reais, normais,
    caminhoReal: caminho(reais), caminhoNormal: caminho(normais),
    marcadores: [
      marcador(dados.media, "media"),
      marcador(dados.limiteInferiorDesvio, "desvio-inferior"),
      marcador(dados.limiteSuperiorDesvio, "desvio-superior"),
    ].filter(Boolean),
  };
}

function textoPercentual(valor) {
  return `${Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;
}

export function renderizarCurvaDistribuicao(svg, detalhe, dados) {
  svg.replaceChildren();
  const geometria = geometriaCurvaDistribuicao(dados);
  if (!geometria) {
    detalhe.textContent = "Não existem intervalos concluídos para construir a distribuição.";
    return { pontos: 0, curvaNormal: false };
  }
  svg.setAttribute("viewBox", `0 0 ${geometria.largura} ${geometria.altura}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Distribuição percentual das durações dos intervalos");

  for (const valor of geometria.marcasY) {
    const y = geometria.inferior - valor * (geometria.inferior - geometria.topo) / geometria.yMax;
    svg.append(svgElemento("line", {
      x1: geometria.esquerda, x2: geometria.direita, y1: y, y2: y,
      class: "distribuicao-grade",
    }));
    const rotulo = svgElemento("text", {
      x: geometria.esquerda - 12, y: y + 4,
      class: "distribuicao-rotulo", "text-anchor": "end",
    });
    rotulo.textContent = textoPercentual(valor); svg.append(rotulo);
  }
  for (const valor of geometria.marcasX) {
    const x = geometria.xMin === geometria.xMax
      ? (geometria.esquerda + geometria.direita) / 2
      : geometria.esquerda + (valor - geometria.xMin)
        * (geometria.direita - geometria.esquerda) / (geometria.xMax - geometria.xMin);
    const rotulo = svgElemento("text", {
      x, y: geometria.inferior + 25,
      class: "distribuicao-rotulo", "text-anchor": "middle",
    });
    rotulo.textContent = String(valor); svg.append(rotulo);
  }
  svg.append(
    svgElemento("line", { x1: geometria.esquerda, x2: geometria.esquerda, y1: geometria.topo, y2: geometria.inferior, class: "distribuicao-eixo" }),
    svgElemento("line", { x1: geometria.esquerda, x2: geometria.direita, y1: geometria.inferior, y2: geometria.inferior, class: "distribuicao-eixo" }),
  );

  const tituloX = svgElemento("text", {
    x: (geometria.esquerda + geometria.direita) / 2,
    y: geometria.altura - 18, class: "distribuicao-titulo-eixo", "text-anchor": "middle",
  });
  tituloX.textContent = "Duração do intervalo (concursos)"; svg.append(tituloX);
  const tituloY = svgElemento("text", {
    x: 20, y: (geometria.topo + geometria.inferior) / 2,
    class: "distribuicao-titulo-eixo", "text-anchor": "middle",
    transform: `rotate(-90 20 ${(geometria.topo + geometria.inferior) / 2})`,
  });
  tituloY.textContent = "Ocorrências (%)"; svg.append(tituloY);

  if (geometria.caminhoNormal) {
    svg.append(svgElemento("path", {
      d: geometria.caminhoNormal, class: "distribuicao-curva-normal",
    }));
  }
  svg.append(svgElemento("path", {
    d: geometria.caminhoReal, class: "distribuicao-curva-real",
  }));
  for (const item of geometria.reais.filter((ponto) => ponto.quantidade > 0)) {
    const descricao = `Intervalo ${item.intervalo}: ${item.quantidade} ocorrências · ${textoPercentual(item.percentual)}`;
    const ponto = svgElemento("circle", {
      cx: item.x, cy: item.y, r: 4, class: "distribuicao-ponto-real",
      tabindex: 0, role: "button", "aria-label": descricao,
    });
    const title = svgElemento("title"); title.textContent = descricao; ponto.append(title);
    const mostrar = () => { detalhe.textContent = descricao; };
    ponto.addEventListener("mouseenter", mostrar);
    ponto.addEventListener("focus", mostrar);
    ponto.addEventListener("click", mostrar);
    svg.append(ponto);
  }
  for (const item of geometria.marcadores) {
    const linha = svgElemento("line", {
      x1: item.x, x2: item.x, y1: item.topo, y2: item.inferior,
      class: `distribuicao-marcador distribuicao-marcador--${item.tipo}`,
    });
    const title = svgElemento("title");
    title.textContent = `${item.tipo === "media" ? "Média" : "Limite de um desvio-padrão"}: ${item.valor.toLocaleString("pt-BR", { maximumFractionDigits: 3 })} concursos`;
    linha.append(title); svg.append(linha);
  }
  const limitesFora = [dados.limiteInferiorDesvio, dados.limiteSuperiorDesvio]
    .filter((valor) => valor < geometria.xMin || valor > geometria.xMax);
  detalhe.textContent = limitesFora.length
    ? `Distribuição carregada. ${limitesFora.length} limite de desvio está fora do domínio observado.`
    : "Distribuição carregada. Selecione um ponto para consultar seus valores exatos.";
  return {
    pontos: geometria.reais.filter((ponto) => ponto.quantidade > 0).length,
    curvaNormal: geometria.normais.length > 0,
  };
}
