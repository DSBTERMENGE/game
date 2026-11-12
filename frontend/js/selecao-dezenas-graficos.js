const SVG_NS = "http://www.w3.org/2000/svg";

function numero(valor, nome) {
  const convertido = Number(valor);
  if (!Number.isFinite(convertido)) throw new TypeError(`${nome} deve ser numérico.`);
  return convertido;
}

export function construirModeloGraficos(pontos, largura = 1200) {
  if (!Array.isArray(pontos) || pontos.length === 0) {
    throw new TypeError("O relatório deve possuir ao menos um ponto.");
  }
  const normalizados = pontos.map((ponto) => ({
    concurso: numero(ponto.concurso, "concurso"),
    quantidade_dezenas: numero(ponto.quantidade_dezenas, "quantidade_dezenas"),
    quantidade_acertos: numero(ponto.quantidade_acertos, "quantidade_acertos"),
  }));
  for (let indice = 0; indice < normalizados.length; indice += 1) {
    const ponto = normalizados[indice];
    if (!Number.isInteger(ponto.concurso) || !Number.isInteger(ponto.quantidade_dezenas)
      || !Number.isInteger(ponto.quantidade_acertos)
      || ponto.quantidade_dezenas < 0 || ponto.quantidade_acertos < 0
      || ponto.quantidade_acertos > 6) {
      throw new RangeError("Os pontos do relatório estão fora do intervalo esperado.");
    }
    if (indice > 0 && ponto.concurso !== normalizados[indice - 1].concurso + 1) {
      throw new RangeError("Os concursos do relatório devem ser consecutivos.");
    }
  }

  const margem = { esquerda: 58, direita: 18, superior: 18, inferior: 34 };
  const alturaQuantidade = 190;
  const alturaAcertos = 300;
  const primeiro = normalizados[0].concurso;
  const ultimo = normalizados.at(-1).concurso;
  const amplitudeX = Math.max(1, ultimo - primeiro);
  const x = (concurso) => margem.esquerda
    + ((concurso - primeiro) / amplitudeX) * (largura - margem.esquerda - margem.direita);

  const quantidades = normalizados.map((ponto) => ponto.quantidade_dezenas);
  const minimo = Math.min(...quantidades);
  const maximo = Math.max(...quantidades);
  const margemVertical = Math.max(1, Math.ceil((maximo - minimo) * 0.05));
  const dominioMinimo = Math.max(0, minimo - margemVertical);
  const dominioMaximo = maximo + margemVertical;
  const amplitudeQuantidade = Math.max(1, dominioMaximo - dominioMinimo);
  const areaQuantidade = alturaQuantidade - margem.superior - margem.inferior;
  const yQuantidade = (valor) => margem.superior
    + ((dominioMaximo - valor) / amplitudeQuantidade) * areaQuantidade;
  const areaAcertos = alturaAcertos - margem.superior - margem.inferior;
  const yAcertos = (valor) => margem.superior + ((6 - valor) / 6) * areaAcertos;

  const primeiraCentena = Math.ceil(primeiro / 100) * 100;
  const centenas = [];
  for (let concurso = primeiraCentena; concurso <= ultimo; concurso += 100) {
    centenas.push({ concurso, x: x(concurso) });
  }
  const caminho = (campo, projetarY) => normalizados.map((ponto, indice) => (
    `${indice === 0 ? "M" : "L"}${x(ponto.concurso).toFixed(2)} ${projetarY(ponto[campo]).toFixed(2)}`
  )).join(" ");

  return {
    largura, margem, alturaQuantidade, alturaAcertos, primeiro, ultimo,
    minimo, maximo, centenas,
    caminhoQuantidade: caminho("quantidade_dezenas", yQuantidade),
    caminhoAcertos: caminho("quantidade_acertos", yAcertos),
    yMinimo: yQuantidade(minimo), yMaximo: yQuantidade(maximo),
    niveisAcertos: Array.from({ length: 7 }, (_, valor) => ({
      valor, y: yAcertos(valor), premiado: valor >= 4,
    })),
  };
}

function elemento(nome, atributos = {}, texto = null) {
  const item = document.createElementNS(SVG_NS, nome);
  for (const [chave, valor] of Object.entries(atributos)) item.setAttribute(chave, valor);
  if (texto !== null) item.textContent = texto;
  return item;
}

function prepararSvg(svg, largura, altura, titulo, descricao) {
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${largura} ${altura}`);
  svg.setAttribute("role", "img");
  svg.append(elemento("title", {}, titulo), elemento("desc", {}, descricao));
}

function desenharEixoComCentenas(svg, modelo, altura) {
  const base = altura - modelo.margem.inferior;
  for (const marca of modelo.centenas) {
    svg.append(
      elemento("line", {
        x1: marca.x, y1: modelo.margem.superior, x2: marca.x, y2: base,
        class: "backtest-grafico__grade-vertical",
      }),
      elemento("text", {
        x: marca.x, y: altura - 10, class: "backtest-grafico__rotulo-x",
      }, String(marca.concurso)),
    );
  }
  svg.append(elemento("line", {
    x1: modelo.margem.esquerda, y1: base,
    x2: modelo.largura - modelo.margem.direita, y2: base,
    class: "backtest-grafico__eixo",
  }));
}

export function renderizarGraficosBacktest(svgQuantidade, svgAcertos, pontos) {
  const modelo = construirModeloGraficos(pontos);
  prepararSvg(
    svgQuantidade, modelo.largura, modelo.alturaQuantidade,
    "Quantidade de dezenas retornadas por concurso",
    "Linha histórica com limites mínimo e máximo observados; linhas verticais somente a cada cem concursos.",
  );
  desenharEixoComCentenas(svgQuantidade, modelo, modelo.alturaQuantidade);
  for (const limite of [
    { valor: modelo.minimo, y: modelo.yMinimo, classe: "minimo" },
    { valor: modelo.maximo, y: modelo.yMaximo, classe: "maximo" },
  ]) {
    svgQuantidade.append(
      elemento("line", {
        x1: modelo.margem.esquerda, y1: limite.y,
        x2: modelo.largura - modelo.margem.direita, y2: limite.y,
        class: `backtest-grafico__limite backtest-grafico__limite--${limite.classe}`,
      }),
      elemento("text", {
        x: modelo.margem.esquerda - 8, y: limite.y + 4,
        class: "backtest-grafico__rotulo-y",
      }, String(limite.valor)),
    );
  }
  svgQuantidade.append(elemento("path", {
    d: modelo.caminhoQuantidade, class: "backtest-grafico__trajeto backtest-grafico__trajeto--quantidade",
  }));

  prepararSvg(
    svgAcertos, modelo.largura, modelo.alturaAcertos,
    "Quantidade de acertos por concurso",
    "Linha histórica entre zero e seis acertos; níveis zero a três em vermelho e quatro a seis em verde.",
  );
  desenharEixoComCentenas(svgAcertos, modelo, modelo.alturaAcertos);
  for (const nivel of modelo.niveisAcertos) {
    svgAcertos.append(
      elemento("line", {
        x1: modelo.margem.esquerda, y1: nivel.y,
        x2: modelo.largura - modelo.margem.direita, y2: nivel.y,
        class: `backtest-grafico__nivel backtest-grafico__nivel--${nivel.premiado ? "premiado" : "sem-premio"}`,
      }),
      elemento("text", {
        x: modelo.margem.esquerda - 8, y: nivel.y + 4,
        class: `backtest-grafico__rotulo-y backtest-grafico__rotulo-y--${nivel.premiado ? "premiado" : "sem-premio"}`,
      }, String(nivel.valor)),
    );
  }
  svgAcertos.append(elemento("path", {
    d: modelo.caminhoAcertos, class: "backtest-grafico__trajeto backtest-grafico__trajeto--acertos",
  }));
  return modelo;
}
