const QUANTIDADE_QUADRANTES = 4;
const DEZENAS_POR_RESULTADO = 6;
const CORES_CLASSIFICACAO = ["#166534", "#8bb29a", "#ca8a04", "#b91c1c"];

function dezenaValida(valor, contexto) {
  const dezena = Number(valor);
  if (!Number.isInteger(dezena) || dezena < 1 || dezena > 60) {
    throw new RangeError(`${contexto} deve ser uma dezena inteira entre 1 e 60.`);
  }
  return dezena;
}

export function classificarDezenaNoQuadrante(valor) {
  const dezena = dezenaValida(valor, "A dezena");
  const coluna = ((dezena - 1) % 10) + 1;
  const linha = Math.floor((dezena - 1) / 10) + 1;

  if (linha <= 3) return coluna >= 6 ? 1 : 2;
  return coluna <= 5 ? 3 : 4;
}

function extrairDezenas(resultado, indice) {
  const fonte = resultado?.dezenas ?? [
    resultado?.res_01,
    resultado?.res_02,
    resultado?.res_03,
    resultado?.res_04,
    resultado?.res_05,
    resultado?.res_06,
  ];
  if (!Array.isArray(fonte) || fonte.length !== DEZENAS_POR_RESULTADO) {
    throw new TypeError(`O resultado ${indice + 1} deve possuir exatamente seis dezenas.`);
  }
  const dezenas = fonte.map((valor, posicao) => (
    dezenaValida(valor, `A dezena ${posicao + 1} do resultado ${indice + 1}`)
  ));
  if (new Set(dezenas).size !== DEZENAS_POR_RESULTADO) {
    throw new TypeError(`O resultado ${indice + 1} possui dezenas repetidas.`);
  }
  return dezenas;
}

export function contarQuadrantes(resultados) {
  if (!Array.isArray(resultados) || resultados.length === 0) {
    throw new TypeError("A contagem exige ao menos um resultado.");
  }

  const quantidades = [0, 0, 0, 0];
  resultados.forEach((resultado, indice) => {
    extrairDezenas(resultado, indice).forEach((dezena) => {
      quantidades[classificarDezenaNoQuadrante(dezena) - 1] += 1;
    });
  });

  const total = quantidades.reduce((soma, quantidade) => soma + quantidade, 0);
  const referenciaMedia = total / QUANTIDADE_QUADRANTES;
  return {
    concursos: resultados.length,
    total,
    referenciaMedia,
    quadrantes: quantidades.map((quantidade, indice) => ({
      quadrante: indice + 1,
      quantidade,
      percentual: quantidade / total * 100,
    })),
  };
}

function medidaCaixa(caixa, nome) {
  const valores = Object.fromEntries(["left", "top", "width", "height"].map((campo) => {
    const valor = Number(caixa?.[campo]);
    if (!Number.isFinite(valor)) throw new TypeError(`${nome}.${campo} deve ser finito.`);
    return [campo, valor];
  }));
  if (valores.width <= 0 || valores.height <= 0) {
    throw new RangeError(`${nome} deve possuir largura e altura positivas.`);
  }
  return valores;
}

export function calcularGeometriaDosEixos({ mapa, dezena05, dezena06, dezena21, dezena31 }) {
  const painel = medidaCaixa(mapa, "mapa");
  const d05 = medidaCaixa(dezena05, "dezena05");
  const d06 = medidaCaixa(dezena06, "dezena06");
  const d21 = medidaCaixa(dezena21, "dezena21");
  const d31 = medidaCaixa(dezena31, "dezena31");
  const direita05 = d05.left + d05.width;
  const baixo21 = d21.top + d21.height;
  const espessuraVertical = Math.max(1, d06.left - direita05);
  const espessuraHorizontal = Math.max(1, d31.top - baixo21);
  const origemX = ((direita05 + d06.left) / 2) - painel.left;
  const origemY = ((baixo21 + d31.top) / 2) - painel.top;

  return {
    origem: { x: origemX, y: origemY },
    espessura: { vertical: espessuraVertical, horizontal: espessuraHorizontal },
    afastamento: {
      x: espessuraVertical / 2 + 2,
      y: espessuraHorizontal / 2 + 2,
    },
    eixoVertical: {
      x: origemX - espessuraVertical / 2,
      y: 0,
      largura: espessuraVertical,
      altura: painel.height,
    },
    eixoHorizontal: {
      x: 0,
      y: origemY - espessuraHorizontal / 2,
      largura: painel.width,
      altura: espessuraHorizontal,
    },
  };
}

function numeroPositivo(valor, nome) {
  const numero = Number(valor);
  if (!Number.isFinite(numero) || numero <= 0) {
    throw new RangeError(`${nome} deve ser um número positivo.`);
  }
  return numero;
}

export function calcularDimensoesDosQuadrados({ analise, geometria }) {
  const referencia = numeroPositivo(analise?.referenciaMedia, "analise.referenciaMedia");
  if (!Array.isArray(analise?.quadrantes) || analise.quadrantes.length !== QUANTIDADE_QUADRANTES) {
    throw new TypeError("A análise deve possuir exatamente quatro quadrantes.");
  }

  const larguraMapa = numeroPositivo(geometria?.eixoHorizontal?.largura, "largura do mapa");
  const alturaMapa = numeroPositivo(geometria?.eixoVertical?.altura, "altura do mapa");
  const origemX = numeroPositivo(geometria?.origem?.x, "geometria.origem.x");
  const origemY = numeroPositivo(geometria?.origem?.y, "geometria.origem.y");
  const afastamentoX = numeroPositivo(geometria?.afastamento?.x, "geometria.afastamento.x");
  const afastamentoY = numeroPositivo(geometria?.afastamento?.y, "geometria.afastamento.y");
  const extensoes = {
    esquerda: origemX - afastamentoX,
    direita: larguraMapa - origemX - afastamentoX,
    superior: origemY - afastamentoY,
    inferior: alturaMapa - origemY - afastamentoY,
  };
  Object.entries(extensoes).forEach(([nome, valor]) => numeroPositivo(valor, `extensão ${nome}`));

  const extensaoDisponivel = Math.min(...Object.values(extensoes));
  const passo = extensaoDisponivel / referencia / 2;
  const quadrantes = analise.quadrantes.map((item, indice) => {
    const quantidade = Number(item?.quantidade);
    if (!Number.isInteger(quantidade) || quantidade < 0) {
      throw new RangeError(`A quantidade do quadrante ${indice + 1} deve ser um inteiro não negativo.`);
    }
    return {
      quadrante: indice + 1,
      quantidade,
      lado: quantidade * passo,
    };
  });

  return {
    referencia,
    extensoes,
    extensaoDisponivel,
    passo,
    quadrantes,
  };
}

export function calcularRetangulosDosQuadrantes({ geometria, dimensoes }) {
  const origemX = numeroPositivo(geometria?.origem?.x, "geometria.origem.x");
  const origemY = numeroPositivo(geometria?.origem?.y, "geometria.origem.y");
  const afastamentoX = numeroPositivo(geometria?.afastamento?.x, "geometria.afastamento.x");
  const afastamentoY = numeroPositivo(geometria?.afastamento?.y, "geometria.afastamento.y");
  if (!Array.isArray(dimensoes?.quadrantes) || dimensoes.quadrantes.length !== QUANTIDADE_QUADRANTES) {
    throw new TypeError("As dimensões devem possuir exatamente quatro quadrantes.");
  }

  return dimensoes.quadrantes.map((item, indice) => {
    const quadrante = indice + 1;
    const lado = numeroPositivo(item?.lado, `lado do quadrante ${quadrante}`);
    const direita = quadrante === 1 || quadrante === 4;
    const abaixo = quadrante === 3 || quadrante === 4;
    return {
      quadrante,
      quantidade: item.quantidade,
      x: direita ? origemX + afastamentoX : origemX - afastamentoX - lado,
      y: abaixo ? origemY + afastamentoY : origemY - afastamentoY - lado,
      largura: lado,
      altura: lado,
    };
  });
}

export function classificarQuadrantesPorQuantidade(quadrantes) {
  if (!Array.isArray(quadrantes) || quadrantes.length !== QUANTIDADE_QUADRANTES) {
    throw new TypeError("A classificação exige exatamente quatro quadrantes.");
  }
  const validados = quadrantes.map((item, indice) => {
    const quantidade = Number(item?.quantidade);
    const percentual = Number(item?.percentual);
    if (!Number.isInteger(quantidade) || quantidade < 0) {
      throw new RangeError(`A quantidade do quadrante ${indice + 1} deve ser um inteiro não negativo.`);
    }
    if (!Number.isFinite(percentual) || percentual < 0 || percentual > 100) {
      throw new RangeError(`O percentual do quadrante ${indice + 1} deve estar entre 0 e 100.`);
    }
    return { quadrante: indice + 1, quantidade, percentual };
  });
  const quantidadesUnicas = [...new Set(validados.map(({ quantidade }) => quantidade))]
    .sort((a, b) => b - a);

  return validados.map((item) => {
    const posicao = quantidadesUnicas.indexOf(item.quantidade) + 1;
    return {
      ...item,
      posicao,
      cor: CORES_CLASSIFICACAO[posicao - 1],
    };
  });
}
