const SVG_NS = "http://www.w3.org/2000/svg";
const API_RESULTADOS = "/api/resultados";
const API_IMPORTAR = "/api/resultados/importar";

const grade = document.querySelector("#grade-dezenas");
const mapa = document.querySelector("#mapa-dezenas");
const camadaMarcas = document.querySelector("#camada-marcas");
const jogoNumero = document.querySelector("#jogo-numero");
const coordenadaMediaSaida = document.querySelector("#coordenada-media");
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

const estado = {
  resultados: [],
  indiceAtual: -1,
  vooAtivo: false,
  temporizadorVoo: null,
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
  camadaMarcas.replaceChildren();
  jogoNumero.textContent = "—";
  coordenadaMediaSaida.textContent = "Média espacial: —";
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
  const dezenas = extrairDezenas(resultado);
  const media = calcularMediaEspacial(dezenas);

  if (!acumular) {
    camadaMarcas.replaceChildren();
  }

  ajustarCamada();
  const raioResultado = document.querySelector(".dezena").clientWidth * 0.34;
  dezenas.forEach((numero) => {
    adicionarCirculo(centroDaDezena(numero), raioResultado, "marca-resultado");
  });
  adicionarCirculo(coordenadaParaPixel(media), Math.max(7, raioResultado * 0.34), "marca-media");

  jogoNumero.textContent = numeroDoResultado(resultado);
  coordenadaMediaSaida.textContent = `Média espacial: (${media.x.toFixed(2)}; ${media.y.toFixed(2)})`;
  return media;
}

function desenharMancha(resultados = estado.resultados) {
  interromperVoo(false);
  camadaMarcas.replaceChildren();
  ajustarCamada();

  const diametroTresMilimetros = (3 / 25.4) * 96;
  const raio = diametroTresMilimetros / 2;
  const contadores = new Map();
  const fragmento = document.createDocumentFragment();

  resultados.forEach((resultado) => {
    const dezenas = extrairDezenas(resultado);
    dezenas.forEach((numero) => {
      const ocorrencia = contadores.get(numero) ?? 0;
      contadores.set(numero, ocorrencia + 1);
      const centro = centroDaDezena(numero);
      const celula = document.querySelector(`#dezena-${formatarDezena(numero)}`);
      const colunas = Math.max(1, Math.floor((celula.clientWidth - 4) / diametroTresMilimetros));
      const linhas = Math.max(1, Math.floor((celula.clientHeight - 4) / diametroTresMilimetros));
      const posicao = ocorrencia % (colunas * linhas);
      const coluna = posicao % colunas;
      const linha = Math.floor(posicao / colunas);
      const inicioX = centro.x - celula.clientWidth / 2 + raio + 2;
      const inicioY = centro.y - celula.clientHeight / 2 + raio + 2;
      adicionarCirculo(
        { x: inicioX + coluna * diametroTresMilimetros, y: inicioY + linha * diametroTresMilimetros },
        raio,
        "marca-mancha-resultado",
        fragmento,
      );
    });

    adicionarCirculo(
      coordenadaParaPixel(calcularMediaEspacial(dezenas)),
      raio,
      "marca-mancha-media",
      fragmento,
    );
  });

  camadaMarcas.append(fragmento);

  jogoNumero.textContent = "Todos";
  coordenadaMediaSaida.textContent = `Mancha: ${resultados.length} resultados`;
  informar(`Mancha desenhada com ${resultados.length} resultados.`, "sucesso");
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
  desenharResultado(estado.resultados[estado.indiceAtual]);
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
    informar(corpo.mensagem ?? "Importação concluída.", "sucesso");
    await carregarResultadosDaApi();
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
botaoMancha.addEventListener("click", () => desenharMancha());
botaoLimpar.addEventListener("click", () => {
  interromperVoo(false);
  limparGrafico();
  informar("Gráfico limpo.");
});
window.addEventListener("resize", () => {
  ajustarCamada();
  if (estado.indiceAtual >= 0 && !estado.vooAtivo) {
    desenharResultado(estado.resultados[estado.indiceAtual]);
  }
});

ajustarCamada();
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
  desenharResultado,
  interromperVoo,
  limparGrafico,
};
