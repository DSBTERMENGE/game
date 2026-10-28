import {
  carregarConfiguracaoDistribuicoes,
  criarConsultaDistribuicoes,
  salvarConfiguracaoDistribuicoes,
} from "./configuracao-distribuicoes.js";

const grade = document.querySelector("#grade-distribuicoes");
const mensagem = document.querySelector("#mensagem-distribuicoes");
const botaoAtualizar = document.querySelector("#botao-atualizar-distribuicoes");
const botaoConfigurar = document.querySelector("#botao-configurar-faixas");
const dialogo = document.querySelector("#dialogo-configuracao-faixas");
const formConfiguracao = document.querySelector("#form-configuracao-faixas");
const metodoFaixa = document.querySelector("#config-metodo-faixa");
const margemInferior = document.querySelector("#config-margem-inferior");
const margemSuperior = document.querySelector("#config-margem-superior");
const botaoPrevia = document.querySelector("#botao-calcular-previa");
const botaoSalvar = document.querySelector("#botao-salvar-configuracao");
const mensagemPrevia = document.querySelector("#mensagem-previa");
const corpoPrevia = document.querySelector("#corpo-previa-faixas");
let configuracaoSalva = carregarConfiguracaoDistribuicoes();
let dadosPrevia = null;

const NOMES = {
  EST_SOMA: "Soma",
  EST_MEDIA: "Média aritmética",
  EST_MEDIANA: "Mediana",
  EST_DESVIO_PADRAO: "Desvio-padrão das dezenas",
  GEO_EXTENSAO_ABERTA: "Extensão aberta",
  GEO_PERIMETRO_FECHADO: "Perímetro fechado",
  GEO_QUANTIDADE_REGIOES: "Quantidade de regiões",
  GEO_AREA_TOTAL: "Área total",
  GEO_CENTRO_GRAVIDADE_X: "Centro de gravidade X",
  GEO_CENTRO_GRAVIDADE_Y: "Centro de gravidade Y",
};

const SVG_NS = "http://www.w3.org/2000/svg";
const numero = (valor) => Number.parseFloat(valor);
const formatar = (valor) => Number.isFinite(numero(valor))
  ? numero(valor).toLocaleString("pt-BR", { maximumFractionDigits: 6 })
  : "—";

function elementoSvg(nome, atributos = {}) {
  const elemento = document.createElementNS(SVG_NS, nome);
  Object.entries(atributos).forEach(([chave, valor]) => elemento.setAttribute(chave, valor));
  return elemento;
}

export function construirGeometriaGrafico(parametro) {
  const histograma = parametro.histograma ?? [];
  if (!histograma.length) return { barras: [], normal: [], mediaX: 0, faixa: null };
  const minimo = numero(histograma[0].limite_inferior);
  const maximo = numero(histograma.at(-1).limite_superior);
  const amplitude = maximo - minimo || 1;
  const maxFrequencia = Math.max(...histograma.map((item) => item.frequencia), 1);
  const x = (valor) => 12 + (numero(valor) - minimo) * 276 / amplitude;
  const barras = histograma.map((item, indice) => ({
    x: 12 + indice * 276 / histograma.length + 1,
    y: 105 - item.frequencia * 88 / maxFrequencia,
    largura: Math.max(1, 276 / histograma.length - 2),
    altura: item.frequencia * 88 / maxFrequencia,
  }));
  const pontosNormal = parametro.curva_normal_referencia?.pontos ?? [];
  const maxDensidade = Math.max(...pontosNormal.map((item) => numero(item.densidade)), 0);
  const normal = maxDensidade === 0 ? [] : pontosNormal.map((item) => ({
    x: x(item.x),
    y: 105 - numero(item.densidade) * 82 / maxDensidade,
  }));
  const inferior = numero(parametro.faixa.limite_inferior);
  const superior = numero(parametro.faixa.limite_superior);
  const faixa = {
    x: Math.max(12, x(inferior)),
    largura: Math.max(0, Math.min(288, x(superior)) - Math.max(12, x(inferior))),
  };
  return { barras, normal, mediaX: x(parametro.media), faixa };
}

function desenharGrafico(parametro) {
  const svg = elementoSvg("svg", {
    class: "grafico-distribuicao",
    viewBox: "0 0 300 120",
    role: "img",
    "aria-label": `Distribuição de ${NOMES[parametro.codigo] ?? parametro.codigo}`,
    preserveAspectRatio: "none",
  });
  const geometria = construirGeometriaGrafico(parametro);
  if (geometria.faixa) svg.append(elementoSvg("rect", {
    class: "grafico-faixa", x: geometria.faixa.x, y: 10,
    width: geometria.faixa.largura, height: 95,
  }));
  geometria.barras.forEach((barra) => svg.append(elementoSvg("rect", {
    class: "grafico-barra", x: barra.x, y: barra.y,
    width: barra.largura, height: barra.altura,
  })));
  if (geometria.normal.length) {
    const d = geometria.normal.map((ponto, indice) =>
      `${indice ? "L" : "M"} ${ponto.x.toFixed(2)} ${ponto.y.toFixed(2)}`).join(" ");
    svg.append(elementoSvg("path", { class: "grafico-normal", d }));
  }
  svg.append(
    elementoSvg("line", { class: "grafico-media", x1: geometria.mediaX, x2: geometria.mediaX, y1: 8, y2: 105 }),
    elementoSvg("line", { class: "grafico-eixo", x1: 12, x2: 288, y1: 105, y2: 105 }),
  );
  return svg;
}

function metrica(rotulo, valor) {
  const item = document.createElement("span");
  item.title = `${rotulo}: ${valor}`;
  item.textContent = `${rotulo}: ${valor}`;
  return item;
}

function criarCartao(parametro) {
  const artigo = document.createElement("article");
  artigo.className = "cartao-distribuicao";
  artigo.dataset.codigo = parametro.codigo;
  const cabecalho = document.createElement("header");
  const titulo = document.createElement("h2");
  titulo.textContent = NOMES[parametro.codigo] ?? parametro.codigo;
  const amostra = document.createElement("span");
  amostra.textContent = `n=${parametro.quantidade} · ausentes=${parametro.ausentes ?? 0}`;
  cabecalho.append(titulo, amostra);
  artigo.append(cabecalho);
  if (parametro.perfil === null || !parametro.histograma?.length) {
    const vazio = document.createElement("div");
    vazio.className = "cartao-vazio";
    vazio.textContent = "Sem valores para este parâmetro";
    artigo.append(vazio);
    return artigo;
  }
  artigo.append(desenharGrafico(parametro));
  const metricas = document.createElement("div");
  metricas.className = "metricas-distribuicao";
  metricas.append(
    metrica("Média", formatar(parametro.media)),
    metrica("Desvio", formatar(parametro.desvio_padrao_populacional)),
    metrica("Mín.", formatar(parametro.minimo)),
    metrica("Máx.", formatar(parametro.maximo)),
    metrica("Faixa mín.", formatar(parametro.faixa.limite_inferior)),
    metrica("Faixa máx.", formatar(parametro.faixa.limite_superior)),
    metrica("Curva", parametro.curva_normal_referencia.disponivel ? "referência" : "indisponível"),
    metrica("Classes", parametro.histograma.length),
  );
  artigo.append(metricas);
  return artigo;
}

function preencherResumo(dados) {
  const janela = dados.janela;
  document.querySelector("#resumo-amostra").textContent = janela.quantidade_resultados.toLocaleString("pt-BR");
  document.querySelector("#resumo-concursos").textContent = `${janela.numero_ap_inicial}–${janela.numero_ap_final}`;
  document.querySelector("#resumo-datas").textContent = `${janela.data_inicial}–${janela.data_final}`;
  const faixa = dados.parametros.find((item) => item.faixa)?.faixa;
  document.querySelector("#resumo-faixa").textContent = faixa
    ? `${faixa.metodo} (${faixa.margem_inferior} / ${faixa.margem_superior})`
    : "—";
}

export function renderizarDistribuicoes(dados) {
  preencherResumo(dados);
  grade.replaceChildren(...dados.parametros.map(criarCartao));
}

async function carregarDistribuicoes() {
  botaoAtualizar.disabled = true;
  mensagem.textContent = "Carregando os dez perfis…";
  try {
    const consulta = criarConsultaDistribuicoes(configuracaoSalva);
    const resposta = await fetch(`/api/perfis/distribuicoes?${consulta}`);
    const corpo = await resposta.json();
    if (!resposta.ok) throw new Error(corpo.erro?.mensagem || "Não foi possível carregar os perfis.");
    renderizarDistribuicoes(corpo.distribuicoes);
    mensagem.textContent = "Perfis históricos carregados.";
  } catch (erro) {
    grade.replaceChildren();
    mensagem.textContent = erro.message;
  } finally {
    botaoAtualizar.disabled = false;
  }
}

function configuracaoDoFormulario() {
  return {
    metodo_faixa: metodoFaixa.value,
    margem_inferior: margemInferior.value,
    margem_superior: margemSuperior.value,
  };
}

function preencherFormulario() {
  metodoFaixa.value = configuracaoSalva.metodo_faixa;
  margemInferior.value = configuracaoSalva.margem_inferior;
  margemSuperior.value = configuracaoSalva.margem_superior;
  dadosPrevia = null;
  corpoPrevia.replaceChildren();
  botaoSalvar.disabled = true;
  mensagemPrevia.textContent = "Calcule a prévia antes de salvar. O screener permanecerá inativo.";
}

function adicionarCelula(linha, texto) {
  const celula = document.createElement("td");
  celula.textContent = texto;
  linha.append(celula);
}

function renderizarPrevia(dados) {
  corpoPrevia.replaceChildren();
  dados.parametros.forEach((parametro) => {
    const linha = document.createElement("tr");
    adicionarCelula(linha, NOMES[parametro.codigo] ?? parametro.codigo);
    adicionarCelula(linha, parametro.faixa ? formatar(parametro.faixa.limite_inferior) : "Sem valor");
    adicionarCelula(linha, parametro.faixa ? formatar(parametro.faixa.limite_superior) : "Sem valor");
    corpoPrevia.append(linha);
  });
}

async function calcularPrevia() {
  if (!formConfiguracao.reportValidity()) return;
  botaoPrevia.disabled = true;
  botaoSalvar.disabled = true;
  mensagemPrevia.textContent = "Calculando os limites com o histórico…";
  try {
    const consulta = criarConsultaDistribuicoes(configuracaoDoFormulario());
    const resposta = await fetch(`/api/perfis/distribuicoes?${consulta}`);
    const corpo = await resposta.json();
    if (!resposta.ok) throw new Error(corpo.erro?.mensagem || "Não foi possível calcular a prévia.");
    dadosPrevia = corpo.distribuicoes;
    renderizarPrevia(dadosPrevia);
    botaoSalvar.disabled = false;
    mensagemPrevia.textContent = "Prévia calculada. Revise os limites antes de salvar o estudo.";
  } catch (erro) {
    dadosPrevia = null;
    corpoPrevia.replaceChildren();
    mensagemPrevia.textContent = erro.message;
  } finally {
    botaoPrevia.disabled = false;
  }
}

function fecharConfiguracao() {
  dialogo.close();
}

botaoConfigurar.addEventListener("click", () => {
  preencherFormulario();
  dialogo.showModal();
});
document.querySelector("#botao-fechar-configuracao").addEventListener("click", fecharConfiguracao);
document.querySelector("#botao-cancelar-configuracao").addEventListener("click", fecharConfiguracao);
botaoPrevia.addEventListener("click", calcularPrevia);
formConfiguracao.addEventListener("input", () => {
  dadosPrevia = null;
  botaoSalvar.disabled = true;
  mensagemPrevia.textContent = "Os valores mudaram. Calcule uma nova prévia antes de salvar.";
});
formConfiguracao.addEventListener("submit", (evento) => {
  evento.preventDefault();
  if (!dadosPrevia) return;
  configuracaoSalva = salvarConfiguracaoDistribuicoes(configuracaoDoFormulario());
  renderizarDistribuicoes(dadosPrevia);
  fecharConfiguracao();
  mensagem.textContent = "Configuração do estudo salva neste navegador; screener inativo.";
});

botaoAtualizar.addEventListener("click", carregarDistribuicoes);
carregarDistribuicoes();
