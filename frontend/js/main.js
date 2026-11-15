import {
  aplicarConfiguracaoVisual,
  carregarConfiguracaoVisual,
  vincularPainelConfiguracao,
} from "./configuracao-visual.js";
import { prepararManchaDeMedia } from "./manchas-medias.js";
import { plotarCirculo } from "./plotagem-manchas.js";
import { prepararOcorrenciasDasDezenas } from "./ocorrencias-dezenas-painel.js";
import {
  calcularDimensoesDosQuadrados,
  calcularGeometriaDosEixos,
  calcularRetangulosDosQuadrantes,
  classificarQuadrantesPorQuantidade,
  contarQuadrantes,
} from "./quadrantes-painel.js";

const SVG_NS = "http://www.w3.org/2000/svg";
const API_RESULTADOS = "/api/resultados?incluir_geometria=0";
const API_IMPORTAR = "/api/resultados/importar";
const API_MANCHAS = "/api/resultados/manchas";

const grade = document.querySelector("#grade-dezenas");
const mapa = document.querySelector("#mapa-dezenas");
const camadaMarcas = document.querySelector("#camada-marcas");
const jogoNumero = document.querySelector("#jogo-numero");
const coordenadaMediaSaida = document.querySelector("#coordenada-media");
const resumoGeometricoSaida = document.querySelector("#resumo-geometrico");
const mensagemSistema = document.querySelector("#mensagem-sistema");
const arquivoExcel = document.querySelector("#arquivo-excel");
const nomeArquivo = document.querySelector("#nome-arquivo");
const botaoSelecionarExcel = document.querySelector("#botao-selecionar-excel");
const botaoImportarExcel = document.querySelector("#botao-importar-excel");
const seletorResultado = document.querySelector("#seletor-resultado");
const botaoAnterior = document.querySelector("#botao-anterior");
const botaoProximo = document.querySelector("#botao-proximo");
const tempoVoo = document.querySelector("#tempo-voo");
const botaoVoo = document.querySelector("#botao-voo");
const botaoMancha = document.querySelector("#botao-mancha");
const botaoLimpar = document.querySelector("#botao-limpar");
const vooMostrarMedia = document.querySelector("#voo-mostrar-media");
const vooMostrarLinha = document.querySelector("#voo-mostrar-linha");
const vooMostrarPoligono1 = document.querySelector("#voo-mostrar-poligono-1");
const vooMostrarPoligono2 = document.querySelector("#voo-mostrar-poligono-2");
const manchaMostrarDezenas = document.querySelector("#mancha-mostrar-dezenas");
const manchaMostrarMedia = document.querySelector("#mancha-mostrar-media");
const manchaMostrarCg1 = document.querySelector("#mancha-mostrar-cg1");
const manchaMostrarCg2 = document.querySelector("#mancha-mostrar-cg2");
const manchaMostrarQuadrantes = document.querySelector("#mancha-mostrar-quadrantes");

const estado = {
  resultados: [],
  indiceAtual: -1,
  vooAtivo: false,
  temporizadorVoo: null,
  configuracaoVisual: carregarConfiguracaoVisual(),
  pontosManchas: new Map(),
  visualizacaoMancha: false,
};

const formatarDezena = (numero) => String(numero).padStart(2, "0");
const criarElementoSvg = (nome) => document.createElementNS(SVG_NS, nome);

for (let numero = 1; numero <= 60; numero += 1) {
  const celula = document.createElement("div");
  celula.className = "dezena";
  celula.id = `dezena-${formatarDezena(numero)}`;
  celula.dataset.dezena = String(numero);
  celula.textContent = formatarDezena(numero);
  celula.setAttribute("aria-label", `Dezena ${formatarDezena(numero)}`);
  grade.append(celula);
}

function informar(mensagem, tipo = "informacao") {
  mensagemSistema.textContent = mensagem;
  mensagemSistema.dataset.tipo = tipo;
}

function ajustarCamada() {
  camadaMarcas.setAttribute("viewBox", `0 0 ${mapa.clientWidth} ${mapa.clientHeight}`);
}

function limparGrafico() {
  estado.visualizacaoMancha = false;
  camadaMarcas.replaceChildren();
  jogoNumero.textContent = "—";
  coordenadaMediaSaida.textContent = "Média espacial: —";
  resumoGeometricoSaida.textContent = "Geometria: —";
}

function centroDaDezena(numero) {
  const celula = document.querySelector(`#dezena-${formatarDezena(numero)}`);

  if (!celula) {
    throw new RangeError(`A dezena ${numero} deve estar entre 1 e 60.`);
  }

  const caixaMapa = mapa.getBoundingClientRect();
  const caixaCelula = celula.getBoundingClientRect();

  return {
    x: caixaCelula.left - caixaMapa.left + caixaCelula.width / 2,
    y: caixaCelula.top - caixaMapa.top + caixaCelula.height / 2,
  };
}

function coordenadaLogica(numero) {
  if (!Number.isInteger(numero) || numero < 1 || numero > 60) {
    throw new RangeError(`A dezena ${numero} deve estar entre 1 e 60.`);
  }

  return {
    x: (numero - 1) % 10,
    y: Math.floor((numero - 1) / 10),
  };
}

function calcularMediaEspacial(dezenas) {
  const pontos = dezenas.map(coordenadaLogica);
  return pontos.reduce(
    (media, ponto) => ({
      x: media.x + ponto.x / pontos.length,
      y: media.y + ponto.y / pontos.length,
    }),
    { x: 0, y: 0 },
  );
}

function coordenadaParaPixel({ x, y }) {
  const origem = centroDaDezena(1);
  const passoHorizontal = centroDaDezena(2).x - origem.x;
  const passoVertical = centroDaDezena(11).y - origem.y;

  return {
    x: origem.x + x * passoHorizontal,
    y: origem.y + y * passoVertical,
  };
}

function adicionarCirculo({ x, y }, raio, classe, destino = camadaMarcas) {
  const circulo = criarElementoSvg("circle");
  circulo.setAttribute("cx", String(x));
  circulo.setAttribute("cy", String(y));
  circulo.setAttribute("r", String(raio));
  circulo.setAttribute("class", classe);
  destino.append(circulo);
}

function adicionarTrajeto(pontos, classe, fechado = false) {
  const elemento = criarElementoSvg(fechado ? "polygon" : "polyline");
  elemento.setAttribute(
    "points",
    pontos.map((ponto) => `${ponto.x},${ponto.y}`).join(" "),
  );
  elemento.setAttribute("class", classe);
  camadaMarcas.append(elemento);
}

function corDaCamada(matiz, intensidade, luminosidadeMinima = 34) {
  const limitada = Math.max(0, Math.min(1, intensidade));
  return `hsl(${matiz} 72% ${Math.round(82 - limitada * (82 - luminosidadeMinima))}%)`;
}

function desenharReferenciasDaMancha(mancha, destino) {
  const centroPixel = coordenadaParaPixel(mancha.centro);
  mancha.referencias.forEach((referencia) => {
    const extremoPixel = coordenadaParaPixel({
      x: mancha.centro.x + referencia.raio,
      y: mancha.centro.y,
    });
    const raioPixel = Math.abs(extremoPixel.x - centroPixel.x);
    const id = `referencia-mancha-${mancha.identificador}-${referencia.percentual}`;
    const circulo = criarElementoSvg("circle");
    circulo.setAttribute("id", id);
    circulo.setAttribute("cx", String(centroPixel.x));
    circulo.setAttribute("cy", String(centroPixel.y));
    circulo.setAttribute("r", String(raioPixel));
    circulo.setAttribute("class", "referencia-mancha-media");
    circulo.setAttribute("data-mancha", mancha.identificador);
    circulo.setAttribute("fill", "none");
    circulo.setAttribute("stroke", referencia.cor);
    destino.append(circulo);

    const rotulo = criarElementoSvg("text");
    rotulo.setAttribute("class", "rotulo-referencia-mancha-media");
    rotulo.setAttribute("data-mancha", mancha.identificador);
    rotulo.setAttribute("fill", referencia.cor);
    const percurso = criarElementoSvg("textPath");
    percurso.setAttribute("href", `#${id}`);
    percurso.setAttribute("startOffset", "12.5%");
    percurso.textContent = `${referencia.percentual}%`;
    rotulo.append(percurso);
    destino.append(rotulo);
  });
}

function desenharManchaDeMediaConfigurada({ identificador, pontos, cor, classePontos, classeCentro }, destino) {
  const pontosValidos = pontos.filter((ponto) => (
    Number.isFinite(Number(ponto?.x)) && Number.isFinite(Number(ponto?.y))
  ));
  if (pontosValidos.length === 0) return null;
  const mancha = prepararManchaDeMedia({
    identificador,
    pontos: pontosValidos,
    cor,
    corReferencias: estado.configuracaoVisual.corReferenciasMancha,
    diametroMm: estado.configuracaoVisual.diametroPontosMancha,
    fatorIntensidade: estado.configuracaoVisual.fatorIntensidadeMancha,
  });

  mancha.pontos.forEach((ponto) => plotarCirculo({
    destino,
    coordenada: ponto,
    converterCoordenada: coordenadaParaPixel,
    diametroMm: ponto.diametroMm,
    cor: ponto.cor,
    intensidade: ponto.intensidade,
    classe: classePontos,
  }));
  plotarCirculo({
    destino,
    coordenada: mancha.centro,
    converterCoordenada: coordenadaParaPixel,
    diametroMm: mancha.pontos[0].diametroMm,
    cor: estado.configuracaoVisual.corReferenciasMancha,
    intensidade: 1,
    classe: classeCentro,
  });
  desenharReferenciasDaMancha(mancha, destino);
  return mancha;
}

function desenharManchaDaMediaEspacial(resultados, destino) {
  return desenharManchaDeMediaConfigurada({
    identificador: "media-espacial",
    pontos: resultados.map((resultado) => calcularMediaEspacial(extrairDezenas(resultado))),
    cor: estado.configuracaoVisual.corMediaEspacial,
    classePontos: "marca-mancha-media",
    classeCentro: "centro-mancha-media",
  }, destino);
}

function desenharManchaDoCg1(resultados, destino) {
  return desenharManchaDeMediaConfigurada({
    identificador: "cg1",
    pontos: resultados.map((resultado) => (
      estado.pontosManchas.get(numeroDoResultado(resultado))?.centro_gravidade_1
      ?? resultado.analise_geometrica?.centro_gravidade
    )),
    cor: estado.configuracaoVisual.corCg1,
    classePontos: "marca-mancha-cg1",
    classeCentro: "centro-mancha-cg1",
  }, destino);
}

function desenharManchaDoCg2(resultados, destino) {
  return desenharManchaDeMediaConfigurada({
    identificador: "cg2",
    pontos: resultados.map((resultado) => (
      estado.pontosManchas.get(numeroDoResultado(resultado))?.centro_gravidade_2
      ?? resultado.analise_geometrica?.poligono_2?.centro_gravidade
    )),
    cor: estado.configuracaoVisual.corCg2,
    classePontos: "marca-mancha-cg2",
    classeCentro: "centro-mancha-cg2",
  }, destino);
}

function resumirFaixasDaMedia(mancha, titulo) {
  const total = mancha.pontos.length;
  const linhas = mancha.faixas.map((faixa, indice) => {
    const intervalo = indice === 0
      ? `Até ${faixa.ate}%`
      : `De ${faixa.de}% a ${faixa.ate}%`;
    const frequencia = faixa.quantidade > 0
      ? `1:${Math.round(total / faixa.quantidade)}`
      : "sem ocorrência";
    return `${intervalo}: ${faixa.quantidade} (${frequencia})`;
  });
  const centro = mancha.centro;
  return `${titulo}: (${centro.x.toFixed(2)}; ${centro.y.toFixed(2)})\n${linhas.join("\n")}`;
}

function resumirQuadrantes({ analise, classificacoes }) {
  const linhas = analise.quadrantes.map((item) => {
    const classificacao = classificacoes.get(item.quadrante);
    const quantidade = item.quantidade.toLocaleString("pt-BR");
    const percentual = item.percentual.toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    return `Q${item.quadrante}: ${quantidade} (${percentual}%) — ${classificacao.posicao}º`;
  });
  return `Quadrantes:\n${linhas.join("\n")}`;
}

function obterGeometriaDosQuadrantes() {
  return calcularGeometriaDosEixos({
    mapa: mapa.getBoundingClientRect(),
    dezena05: document.querySelector("#dezena-05").getBoundingClientRect(),
    dezena06: document.querySelector("#dezena-06").getBoundingClientRect(),
    dezena21: document.querySelector("#dezena-21").getBoundingClientRect(),
    dezena31: document.querySelector("#dezena-31").getBoundingClientRect(),
  });
}

function desenharEixosDosQuadrantes(destino, geometria = obterGeometriaDosQuadrantes()) {
  [
    ["vertical", geometria.eixoVertical],
    ["horizontal", geometria.eixoHorizontal],
  ].forEach(([nome, eixo]) => {
    const retangulo = criarElementoSvg("rect");
    [["x", eixo.x], ["y", eixo.y], ["width", eixo.largura], ["height", eixo.altura]].forEach(([atributo, valor]) => {
      retangulo.setAttribute(atributo, String(valor));
    });
    retangulo.setAttribute("class", "eixo-quadrante");
    retangulo.setAttribute("data-eixo", nome);
    destino.append(retangulo);
  });
  return geometria;
}

function desenharQuadradosDosQuadrantes(resultados, destino, geometria) {
  const analise = contarQuadrantes(resultados);
  const dimensoes = calcularDimensoesDosQuadrados({ analise, geometria });
  const retangulos = calcularRetangulosDosQuadrantes({ geometria, dimensoes });
  const classificacoes = new Map(
    classificarQuadrantesPorQuantidade(analise.quadrantes)
      .map((item) => [item.quadrante, item]),
  );
  retangulos.forEach((dados) => {
    const classificacao = classificacoes.get(dados.quadrante);
    const retangulo = criarElementoSvg("rect");
    [["x", dados.x], ["y", dados.y], ["width", dados.largura], ["height", dados.altura]].forEach(([atributo, valor]) => {
      retangulo.setAttribute(atributo, String(valor));
    });
    retangulo.setAttribute("class", "quadrado-quadrante");
    retangulo.setAttribute("data-quadrante", String(dados.quadrante));
    retangulo.setAttribute("data-quantidade", String(dados.quantidade));
    retangulo.setAttribute("data-posicao", String(classificacao.posicao));
    retangulo.setAttribute("fill", classificacao.cor);
    destino.append(retangulo);

    const centroX = dados.x + dados.largura / 2;
    const centroY = dados.y + dados.altura / 2;
    [
      ["quantidade", dados.quantidade.toLocaleString("pt-BR"), centroY - 3],
      ["percentual", `${classificacao.percentual.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}%`, centroY + 13],
    ].forEach(([tipo, conteudo, y]) => {
      const texto = criarElementoSvg("text");
      texto.setAttribute("x", String(centroX));
      texto.setAttribute("y", String(y));
      texto.setAttribute("class", "rotulo-quadrante");
      texto.setAttribute("data-quadrante", String(dados.quadrante));
      texto.setAttribute("data-tipo", tipo);
      texto.textContent = conteudo;
      destino.append(texto);
    });
  });
  return { analise, dimensoes, retangulos, classificacoes };
}

function desenharOcorrenciasDasDezenas(resultados, destino) {
  const preparacao = prepararOcorrenciasDasDezenas(resultados.map(extrairDezenas));
  const totais = new Map(preparacao.ocorrencias.map((item) => [item.dezena, item.quantidade]));
  const media = resultados.reduce((total, resultado) => total + extrairDezenas(resultado).length, 0) / 60;
  const maiorDistancia = Math.max(
    1,
    ...Array.from({ length: 60 }, (_, indice) => Math.abs((totais.get(indice + 1) ?? 0) - media)),
  );
  const raio = (2 / 25.4) * 96 / 2;

  totais.forEach((quantidade, numero) => {
    const proximidade = 1 - Math.abs(quantidade - media) / maiorDistancia;
    const centro = centroDaDezena(numero);
    const celula = document.querySelector(`#dezena-${formatarDezena(numero)}`);
    const inicioX = centro.x - celula.clientWidth / 2 + raio + 2;
    const inicioY = centro.y - celula.clientHeight / 2 + raio + 2;
    const passoX = Math.max(0, (celula.clientWidth - 2 * raio - 4) / 9);
    const passoY = Math.max(0, (celula.clientHeight - 2 * raio - 4) / 9);

    for (let ocorrencia = 0; ocorrencia < quantidade; ocorrencia += 1) {
      const posicao = ocorrencia % 100;
      const circulo = criarElementoSvg("circle");
      circulo.setAttribute("cx", String(inicioX + (posicao % 10) * passoX));
      circulo.setAttribute("cy", String(inicioY + Math.floor(posicao / 10) * passoY));
      circulo.setAttribute("r", String(raio));
      circulo.setAttribute("class", "marca-ocorrencia-dezena");
      circulo.setAttribute("fill", corDaCamada(138, proximidade));
      circulo.setAttribute("fill-opacity", "0.38");
      circulo.setAttribute("data-dezena", String(numero));
      circulo.setAttribute("data-ocorrencias", String(quantidade));
      circulo.setAttribute("data-proximidade-media", String(proximidade));
      destino.append(circulo);
    }
  });
}

function desenharResumoDasOcorrencias(resultados, { substituir = true } = {}) {
  const preparacao = prepararOcorrenciasDasDezenas(resultados.map(extrairDezenas));
  if (substituir) resumoGeometricoSaida.replaceChildren();

  const titulo = document.createElement("span");
  titulo.className = "resumo-ocorrencias-dezenas__titulo";
  titulo.textContent = "Ocorrências das dezenas";
  resumoGeometricoSaida.append(titulo);

  const gradeResumo = document.createElement("span");
  gradeResumo.className = "resumo-ocorrencias-dezenas__grade";
  preparacao.colunas.forEach((coluna, indice) => {
    const elementoColuna = document.createElement("span");
    elementoColuna.className = "resumo-ocorrencias-dezenas__coluna";
    elementoColuna.dataset.coluna = String(indice + 1);
    coluna.forEach(({ dezena, quantidade }) => {
      const item = document.createElement("span");
      item.className = "resumo-ocorrencias-dezenas__item";
      item.dataset.dezena = String(dezena);
      item.dataset.quantidade = String(quantidade);
      item.textContent = `${formatarDezena(dezena)}: ${quantidade.toLocaleString("pt-BR")}`;
      elementoColuna.append(item);
    });
    gradeResumo.append(elementoColuna);
  });
  resumoGeometricoSaida.append(gradeResumo);
}

function pontoNumerico(ponto) {
  const convertido = { x: Number(ponto?.x), y: Number(ponto?.y) };
  if (!Number.isFinite(convertido.x) || !Number.isFinite(convertido.y)) {
    throw new TypeError("A API forneceu uma coordenada geométrica inválida.");
  }
  return convertido;
}

function desenharAnaliseGeometrica(resultado, dezenas) {
  const analise = resultado.analise_geometrica;
  const verticesLogicos = analise?.vertices?.map(pontoNumerico)
    ?? [...dezenas].sort((a, b) => a - b).map(coordenadaLogica);
  const vertices = verticesLogicos.map(coordenadaParaPixel);

  if (estado.configuracaoVisual.mostrarRegioes) (analise?.regioes ?? []).forEach((regiao) => {
    adicionarTrajeto(regiao.map(pontoNumerico).map(coordenadaParaPixel), "regiao-geometrica", true);
  });
  if (estado.configuracaoVisual.mostrarLinha && vooMostrarLinha.checked) {
    adicionarTrajeto(vertices, "linha-geometrica");
  }

  if (estado.configuracaoVisual.mostrarPoligono1 && vooMostrarPoligono1.checked) {
    adicionarTrajeto(vertices, "poligono-1-geometrico", true);
  }

  const poligono2 = analise?.poligono_2;
  if (vooMostrarPoligono2.checked && poligono2) {
    adicionarTrajeto(
      poligono2.vertices.map(pontoNumerico).map(coordenadaParaPixel),
      "poligono-2-geometrico",
      true,
    );
  }

  const raioVertices = (estado.configuracaoVisual.diametroVertices / 2 / 25.4) * 96;
  if (
    estado.configuracaoVisual.mostrarVertices
    && (vooMostrarPoligono1.checked || vooMostrarPoligono2.checked)
  ) vertices.forEach((vertice) => adicionarCirculo(
    vertice, raioVertices, "vertice-geometrico",
  ));

  if (
    estado.configuracaoVisual.mostrarCentroGravidade
    && vooMostrarPoligono1.checked
    && analise?.centro_gravidade
  ) {
    adicionarCirculo(
      coordenadaParaPixel(pontoNumerico(analise.centro_gravidade)),
      raioVertices * 1.35,
      "centro-gravidade",
    );
  }
  if (vooMostrarPoligono2.checked && poligono2?.centro_gravidade) {
    adicionarCirculo(
      coordenadaParaPixel(pontoNumerico(poligono2.centro_gravidade)),
      raioVertices * 1.35,
      "centro-gravidade-2",
    );
  }

  if (analise) {
    const extensao = Number(analise.extensao_aberta).toFixed(3).replace(".", ",");
    const perimetro = Number(analise.perimetro_fechado).toFixed(3).replace(".", ",");
    const area = Number(analise.area_total).toFixed(3).replace(".", ",");
    const resumoPoligono2 = poligono2
      ? `\nÁrea P2: ${Number(poligono2.area).toFixed(3).replace(".", ",")}\nCG2: (${Number(poligono2.centro_gravidade.x).toFixed(2)}; ${Number(poligono2.centro_gravidade.y).toFixed(2)})`
      : "";
    resumoGeometricoSaida.textContent = `Extensão: ${extensao}\nPerímetro: ${perimetro}\nÁrea P1: ${area}\nRegiões: ${analise.quantidade_regioes}${resumoPoligono2}`;
  } else {
    resumoGeometricoSaida.textContent = "Geometria: medidas ainda não fornecidas";
  }
}

function extrairDezenas(resultado) {
  const fonte = resultado.dezenas ?? [
    resultado.res_01,
    resultado.res_02,
    resultado.res_03,
    resultado.res_04,
    resultado.res_05,
    resultado.res_06,
  ];
  const dezenas = fonte.map(Number);

  if (
    dezenas.length !== 6
    || dezenas.some((numero) => !Number.isInteger(numero) || numero < 1 || numero > 60)
    || new Set(dezenas).size !== 6
  ) {
    throw new TypeError("O resultado deve conter seis dezenas diferentes entre 01 e 60.");
  }

  return dezenas;
}

function numeroDoResultado(resultado) {
  return resultado.numero_ap ?? resultado.numero_concurso ?? resultado.id_resultado ?? "—";
}

function desenharResultado(resultado, { acumular = false } = {}) {
  estado.visualizacaoMancha = false;
  const dezenas = extrairDezenas(resultado);
  const media = calcularMediaEspacial(dezenas);

  if (!acumular) {
    camadaMarcas.replaceChildren();
  }

  ajustarCamada();
  desenharAnaliseGeometrica(resultado, dezenas);
  const raioResultado = document.querySelector(".dezena").clientWidth * 0.34;
  if (estado.configuracaoVisual.mostrarResultado) dezenas.forEach((numero) => {
    adicionarCirculo(centroDaDezena(numero), raioResultado, "marca-resultado");
  });
  if (estado.configuracaoVisual.mostrarMedia && vooMostrarMedia.checked) adicionarCirculo(
    coordenadaParaPixel(media), Math.max(7, raioResultado * 0.34), "marca-media",
  );

  jogoNumero.textContent = numeroDoResultado(resultado);
  coordenadaMediaSaida.textContent = `Média espacial: (${media.x.toFixed(2)}; ${media.y.toFixed(2)})`;
  return media;
}

function desenharMancha(resultados = estado.resultados) {
  estado.visualizacaoMancha = true;
  interromperVoo(false);
  camadaMarcas.replaceChildren();
  ajustarCamada();

  const fragmento = document.createDocumentFragment();
  let quadrantesDesenhados = null;

  if (manchaMostrarQuadrantes.checked) {
    const geometriaQuadrantes = obterGeometriaDosQuadrantes();
    quadrantesDesenhados = desenharQuadradosDosQuadrantes(
      resultados,
      fragmento,
      geometriaQuadrantes,
    );
    desenharEixosDosQuadrantes(fragmento, geometriaQuadrantes);
  }
  if (manchaMostrarDezenas.checked) desenharOcorrenciasDasDezenas(resultados, fragmento);

  let manchaMedia = null;
  let manchaCg1 = null;
  let manchaCg2 = null;
  if (manchaMostrarMedia.checked) manchaMedia = desenharManchaDaMediaEspacial(resultados, fragmento);
  if (manchaMostrarCg1.checked) manchaCg1 = desenharManchaDoCg1(resultados, fragmento);
  if (manchaMostrarCg2.checked) manchaCg2 = desenharManchaDoCg2(resultados, fragmento);

  camadaMarcas.append(fragmento);

  jogoNumero.textContent = "Todos";
  coordenadaMediaSaida.textContent = `Mancha: ${resultados.length} resultados`;
  const resumos = [];
  if (quadrantesDesenhados) resumos.push(resumirQuadrantes(quadrantesDesenhados));
  if (manchaMedia) resumos.push(resumirFaixasDaMedia(manchaMedia, "Média das médias"));
  if (manchaCg1) resumos.push(resumirFaixasDaMedia(manchaCg1, "Média do CG1"));
  if (manchaCg2) resumos.push(resumirFaixasDaMedia(manchaCg2, "Média do CG2"));
  if (resumos.length > 0) {
    resumoGeometricoSaida.textContent = resumos.join("\n\n");
    if (manchaMostrarDezenas.checked) {
      desenharResumoDasOcorrencias(resultados, { substituir: false });
    }
  } else if (manchaMostrarDezenas.checked) {
    desenharResumoDasOcorrencias(resultados);
  } else {
    resumoGeometricoSaida.textContent = "Geometria: —";
  }
  informar(`Mancha desenhada com ${resultados.length} resultados.`, "sucesso");
}

async function prepararEDesenharMancha() {
  informar("Preparando as manchas históricas...");
  try {
    const resposta = await fetch(API_MANCHAS, { headers: { Accept: "application/json" } });
    if (resposta.ok) {
      const corpo = await resposta.json();
      estado.pontosManchas = new Map((corpo.pontos ?? []).map((item) => [item.numero_ap, item]));
    }
  } catch (_erro) {
    // Média espacial, quadrantes e ocorrências continuam disponíveis sem CG1/CG2.
  }
  desenharMancha();
}

function atualizarControles() {
  const possuiResultados = estado.resultados.length > 0;
  const possuiNavegacao = estado.resultados.length > 1;
  seletorResultado.disabled = !possuiResultados;
  botaoAnterior.disabled = !possuiNavegacao;
  botaoProximo.disabled = !possuiNavegacao;
  botaoVoo.disabled = !possuiNavegacao;
  botaoMancha.disabled = !possuiResultados;
}

function selecionarIndice(indice) {
  if (estado.resultados.length === 0) {
    return;
  }

  estado.indiceAtual = (indice + estado.resultados.length) % estado.resultados.length;
  seletorResultado.value = String(estado.indiceAtual);
  const resultado = estado.resultados[estado.indiceAtual];
  desenharResultado(resultado);
  if (!resultado.analise_geometrica) {
    const numero = numeroDoResultado(resultado);
    fetch(`/api/resultados/${numero}/geometria`, { headers: { Accept: "application/json" } })
      .then((resposta) => {
        if (!resposta.ok) throw new Error(`A API respondeu com status ${resposta.status}.`);
        return resposta.json();
      })
      .then((corpo) => {
        resultado.analise_geometrica = corpo.analise_geometrica;
        if (estado.resultados[estado.indiceAtual] === resultado) desenharResultado(resultado);
      })
      .catch((erro) => informar(`Geometria indisponível: ${erro.message}`, "erro"));
  }
}

function definirResultados(resultados) {
  interromperVoo(false);
  estado.resultados = Array.isArray(resultados) ? resultados : [];
  estado.indiceAtual = estado.resultados.length > 0 ? 0 : -1;
  seletorResultado.replaceChildren();

  if (estado.resultados.length === 0) {
    const opcao = new Option("Nenhum resultado carregado", "");
    seletorResultado.append(opcao);
    limparGrafico();
    informar("Nenhum resultado foi carregado.");
  } else {
    estado.resultados.forEach((resultado, indice) => {
      const numero = numeroDoResultado(resultado);
      const data = resultado.data_resultado ?? resultado.data_sorteio ?? "";
      seletorResultado.append(new Option(`${numero}${data ? ` — ${data}` : ""}`, String(indice)));
    });
    selecionarIndice(0);
    const quantidade = estado.resultados.length;
    informar(
      `${quantidade} ${quantidade === 1 ? "resultado carregado" : "resultados carregados"}.`,
      "sucesso",
    );
  }

  atualizarControles();
}

function intervaloVooEmMilissegundos() {
  const segundos = Number(tempoVoo.value);
  if (!Number.isFinite(segundos) || segundos < 0.1 || segundos > 30) {
    throw new RangeError("O tempo do voo deve estar entre 0,1 e 30 segundos.");
  }
  return segundos * 1000;
}

function interromperVoo(mostrarMensagem = true) {
  if (estado.temporizadorVoo !== null) {
    window.clearTimeout(estado.temporizadorVoo);
    estado.temporizadorVoo = null;
  }
  estado.vooAtivo = false;
  botaoVoo.textContent = "Iniciar voo dos pássaros";
  if (mostrarMensagem) {
    informar("Voo interrompido.");
  }
}

function executarPassoDoVoo() {
  if (!estado.vooAtivo) {
    return;
  }
  selecionarIndice(estado.indiceAtual + 1);
  estado.temporizadorVoo = window.setTimeout(executarPassoDoVoo, intervaloVooEmMilissegundos());
}

function alternarVoo() {
  if (estado.vooAtivo) {
    interromperVoo();
    return;
  }

  try {
    intervaloVooEmMilissegundos();
    estado.vooAtivo = true;
    botaoVoo.textContent = "Pausar voo dos pássaros";
    selecionarIndice(estado.indiceAtual < 0 ? 0 : estado.indiceAtual);
    estado.temporizadorVoo = window.setTimeout(executarPassoDoVoo, intervaloVooEmMilissegundos());
    informar("Voo dos pássaros iniciado.", "sucesso");
  } catch (erro) {
    informar(erro.message, "erro");
  }
}

async function carregarResultadosDaApi() {
  try {
    const resposta = await fetch(API_RESULTADOS, { headers: { Accept: "application/json" } });
    if (!resposta.ok) {
      throw new Error(`A API respondeu com status ${resposta.status}.`);
    }
    const corpo = await resposta.json();
    definirResultados(corpo.resultados ?? corpo);
  } catch (erro) {
    informar(`API ainda indisponível: ${erro.message}`, "erro");
  }
}

async function importarExcel() {
  const arquivo = arquivoExcel.files[0];
  if (!arquivo) {
    informar("Selecione uma planilha Excel.", "erro");
    return;
  }

  const formulario = new FormData();
  formulario.append("arquivo", arquivo);
  botaoImportarExcel.disabled = true;
  informar("Enviando a planilha para leitura, cálculos e armazenamento...");

  try {
    const resposta = await fetch(API_IMPORTAR, { method: "POST", body: formulario });
    const corpo = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      const detalhe = typeof corpo.erro === "object" ? corpo.erro.mensagem : corpo.erro;
      throw new Error(detalhe ?? `A API respondeu com status ${resposta.status}.`);
    }
    await carregarResultadosDaApi();
    const relatorio = corpo.relatorio;
    const mensagem = relatorio
      ? `Importação concluída: ${relatorio.inseridas} inseridos, ${relatorio.iguais} iguais, ${relatorio.alteradas} alterados e ${relatorio.invalidas} inválidos.`
      : (corpo.mensagem ?? "Importação concluída.");
    informar(mensagem, "sucesso");
  } catch (erro) {
    informar(`Não foi possível importar: ${erro.message}`, "erro");
  } finally {
    botaoImportarExcel.disabled = false;
  }
}

botaoSelecionarExcel.addEventListener("click", () => arquivoExcel.click());
arquivoExcel.addEventListener("change", () => {
  const arquivo = arquivoExcel.files[0];
  nomeArquivo.textContent = arquivo?.name ?? "Nenhum arquivo selecionado";
  botaoImportarExcel.disabled = !arquivo;
});
botaoImportarExcel.addEventListener("click", importarExcel);
seletorResultado.addEventListener("change", () => selecionarIndice(Number(seletorResultado.value)));
botaoAnterior.addEventListener("click", () => selecionarIndice(estado.indiceAtual - 1));
botaoProximo.addEventListener("click", () => selecionarIndice(estado.indiceAtual + 1));
botaoVoo.addEventListener("click", alternarVoo);
botaoMancha.addEventListener("click", prepararEDesenharMancha);
[vooMostrarMedia, vooMostrarLinha, vooMostrarPoligono1, vooMostrarPoligono2].forEach((campo) => {
  campo.addEventListener("change", () => {
    if (estado.indiceAtual >= 0) desenharResultado(estado.resultados[estado.indiceAtual]);
  });
});
botaoLimpar.addEventListener("click", () => {
  interromperVoo(false);
  limparGrafico();
  informar("Gráfico limpo.");
});
window.addEventListener("resize", () => {
  ajustarCamada();
  if (estado.visualizacaoMancha) {
    desenharMancha();
  } else if (estado.indiceAtual >= 0) {
    desenharResultado(estado.resultados[estado.indiceAtual]);
  }
});

ajustarCamada();
aplicarConfiguracaoVisual(mapa, estado.configuracaoVisual);
vincularPainelConfiguracao(estado.configuracaoVisual, (configuracao) => {
  estado.configuracaoVisual = aplicarConfiguracaoVisual(mapa, configuracao);
  if (estado.indiceAtual >= 0) desenharResultado(estado.resultados[estado.indiceAtual]);
});
atualizarControles();
carregarResultadosDaApi();

// Interface pública para testes e para a futura integração com a API Python.
window.gameAnalysis = {
  calcularMediaEspacial,
  centroDaDezena,
  coordenadaLogica,
  coordenadaParaPixel,
  definirResultados,
  desenharMancha,
  desenharAnaliseGeometrica,
  desenharResultado,
  interromperVoo,
  limparGrafico,
};
