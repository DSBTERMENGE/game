import { filtrosGraficosDaUrl, urlRetornoFrequencias } from "./navegacao-graficos-frequencias.js";
import {
  ampliarDominioHistorico,
  caminhoHistorico,
  contarValoresForaDominio,
  criarEscalasHistorico,
  dominioHistorico,
  poligonoFaixaHistorico,
} from "./frequencia-historico.js";

const elementos = {
  formulario: document.querySelector("#form-graficos-frequencias"),
  dezena: document.querySelector("#graficos-dezena"),
  tipo: document.querySelector("#graficos-tipo-evento"),
  inicio: document.querySelector("#graficos-concurso-inicial"),
  fim: document.querySelector("#graficos-concurso-final"),
  mensagem: document.querySelector("#mensagem-graficos-auxiliares"),
  estadoGraficos: document.querySelector("#estado-area-graficos"),
  gradeGraficos: document.querySelector("#grade-graficos-historicos"),
  escalaVertical: document.querySelector("#escala-vertical-graficos"),
  avisoRecorte: document.querySelector("#aviso-recorte-graficos"),
  retornos: document.querySelectorAll("#link-voltar-frequencias, #botao-voltar-frequencias"),
  abrirAjuda: document.querySelector("#botao-ajuda-graficos"),
  dialogoAjuda: document.querySelector("#dialogo-ajuda-graficos"),
};

let dadosAtuais = null;

for (let dezena = 1; dezena <= 60; dezena += 1) {
  const opcao = document.createElement("option");
  opcao.value = String(dezena);
  opcao.textContent = String(dezena).padStart(2, "0");
  elementos.dezena.append(opcao);
}

const filtros = filtrosGraficosDaUrl(window.location.search);
if (filtros) {
  elementos.dezena.value = filtros.dezena;
  elementos.tipo.value = filtros.tipo_evento;
  elementos.inicio.value = filtros.concurso_inicial;
  elementos.fim.value = filtros.concurso_final;
} else {
  elementos.mensagem.textContent = "Os filtros de origem estão ausentes ou são inválidos. Volte à página de frequências para selecionar a série.";
  elementos.mensagem.dataset.tipo = "erro";
}

function filtrosAtuais() {
  return {
    dezena: elementos.dezena.value,
    tipo_evento: elementos.tipo.value,
    concurso_inicial: elementos.inicio.value,
    concurso_final: elementos.fim.value,
  };
}

function atualizarRetorno() {
  if (!elementos.formulario.checkValidity()) return;
  try {
    const destino = urlRetornoFrequencias(filtrosAtuais());
    for (const retorno of elementos.retornos) retorno.href = destino;
    elementos.mensagem.textContent = "Seleção preservada para a consulta e para o retorno.";
    elementos.mensagem.dataset.tipo = "";
  } catch (erro) {
    elementos.mensagem.textContent = erro.message;
    elementos.mensagem.dataset.tipo = "erro";
  }
}

async function respostaJson(resposta) {
  let dados;
  try { dados = await resposta.json(); }
  catch (_erro) { throw new Error(`O servidor devolveu uma resposta inválida (HTTP ${resposta.status}).`); }
  if (!resposta.ok) throw new Error(dados.erro?.mensagem || `Falha HTTP ${resposta.status}.`);
  return dados;
}

const SVG_NS = "http://www.w3.org/2000/svg";
function elementoSvg(nome, atributos = {}) {
  const elemento = document.createElementNS(SVG_NS, nome);
  for (const [atributo, valor] of Object.entries(atributos)) elemento.setAttribute(atributo, String(valor));
  return elemento;
}

function caminhoSvg(svg, d, classe) {
  if (d) svg.append(elementoSvg("path", { d, class: classe, fill: "none" }));
}

function camadaDados(svg, escalas, identificador) {
  const defs = elementoSvg("defs");
  const recorte = elementoSvg("clipPath", { id: identificador });
  recorte.append(elementoSvg("rect", {
    x: escalas.esquerda, y: escalas.topo,
    width: escalas.direita - escalas.esquerda,
    height: escalas.inferior - escalas.topo,
  }));
  defs.append(recorte);
  const camada = elementoSvg("g", { "clip-path": `url(#${identificador})` });
  svg.append(defs, camada);
  return camada;
}

function eixosHistorico(svg, escalas, dominio, periodo) {
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.inferior, x2: escalas.direita, y2: escalas.inferior, class: "historico-eixo" }));
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.topo, x2: escalas.esquerda, y2: escalas.inferior, class: "historico-eixo" }));
  for (let indice = 0; indice <= 8; indice += 1) {
    const fracao = indice / 8;
    const xValor = Math.round(periodo.concurso_inicial + fracao * (periodo.concurso_final - periodo.concurso_inicial));
    const yValor = dominio.maximo - fracao * (dominio.maximo - dominio.minimo);
    const xTexto = elementoSvg("text", { x: escalas.x(xValor), y: escalas.inferior + 25, class: "historico-rotulo", "text-anchor": "middle" });
    xTexto.textContent = xValor.toLocaleString("pt-BR");
    const yTexto = elementoSvg("text", { x: escalas.esquerda - 10, y: escalas.y(yValor) + 4, class: "historico-rotulo", "text-anchor": "end" });
    yTexto.textContent = yValor.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
    svg.append(xTexto, yTexto);
  }
}

function cartaoHistorico(titulo, unidade) {
  const artigo = document.createElement("article");
  artigo.className = "historico-cartao-ampliado";
  const cabecalho = document.createElement("header");
  const h3 = document.createElement("h3"); h3.textContent = titulo;
  const span = document.createElement("span"); span.textContent = unidade;
  cabecalho.append(h3, span);
  const svg = elementoSvg("svg", {
    class: "grafico-historico-ampliado", viewBox: "0 0 1440 500", role: "img",
    "aria-label": titulo, preserveAspectRatio: "none",
  });
  artigo.append(cabecalho, svg);
  return { artigo, svg };
}

function renderizarGraficos(dados) {
  dadosAtuais = dados;
  elementos.gradeGraficos.replaceChildren();
  if (!dados.pontos?.length) {
    elementos.estadoGraficos.textContent = "Não existem pontos históricos para os filtros selecionados.";
    return;
  }
  const periodo = dados.periodo;
  const ampliada = elementos.escalaVertical.value === "AMPLIADA_10X";
  let totalFora = 0;
  const intervalos = cartaoHistorico("Evolução dos intervalos", "eixo Y em concursos");
  const camposIntervalos = ["intervalo_minimo", "media_intervalos", "intervalo_maximo"];
  const dominioAutomaticoIntervalos = dominioHistorico(dados.pontos, camposIntervalos);
  const dominioIntervalos = ampliada ? ampliarDominioHistorico(dominioAutomaticoIntervalos, 10) : dominioAutomaticoIntervalos;
  if (dominioIntervalos) {
    if (ampliada) totalFora += contarValoresForaDominio(dados.pontos, camposIntervalos, dominioIntervalos);
    const escalas = criarEscalasHistorico(periodo, dominioIntervalos, 1440, 500);
    eixosHistorico(intervalos.svg, escalas, dominioIntervalos, periodo);
    const camada = camadaDados(intervalos.svg, escalas, "recorte-intervalos");
    caminhoSvg(camada, caminhoHistorico(dados.pontos, "intervalo_minimo", escalas), "historico-linha historico-linha--minimo");
    caminhoSvg(camada, caminhoHistorico(dados.pontos, "media_intervalos", escalas), "historico-linha historico-linha--media");
    caminhoSvg(camada, caminhoHistorico(dados.pontos, "intervalo_maximo", escalas), "historico-linha historico-linha--maximo");
  }

  const previsao = cartaoHistorico("Faixa prevista e ocorrências reais", "eixo Y: número do concurso");
  const camposPrevisao = ["limite_inferior_exato", "previsao_central", "limite_superior_exato"];
  const dominioAutomaticoPrevisao = dominioHistorico(dados.pontos, camposPrevisao, dados.ocorrencias_reais);
  const dominioPrevisao = ampliada ? ampliarDominioHistorico(dominioAutomaticoPrevisao, 10) : dominioAutomaticoPrevisao;
  if (dominioPrevisao) {
    if (ampliada) totalFora += contarValoresForaDominio(dados.pontos, camposPrevisao, dominioPrevisao, dados.ocorrencias_reais);
    const escalas = criarEscalasHistorico(periodo, dominioPrevisao, 1440, 500);
    eixosHistorico(previsao.svg, escalas, dominioPrevisao, periodo);
    const camada = camadaDados(previsao.svg, escalas, "recorte-previsao");
    const faixa = poligonoFaixaHistorico(dados.pontos, "limite_inferior_exato", "limite_superior_exato", escalas);
    if (faixa) camada.append(elementoSvg("polygon", { points: faixa, class: "historico-faixa" }));
    caminhoSvg(camada, caminhoHistorico(dados.pontos, "previsao_central", escalas), "historico-linha historico-linha--media");
    for (const concurso of dados.ocorrencias_reais || []) {
      const circulo = elementoSvg("circle", { cx: escalas.x(concurso), cy: escalas.y(concurso), r: 4.2, class: "historico-ocorrencia" });
      const titulo = elementoSvg("title"); titulo.textContent = `Ocorrência real no concurso ${concurso}`;
      circulo.append(titulo); camada.append(circulo);
    }
  }
  elementos.gradeGraficos.append(intervalos.artigo, previsao.artigo);
  elementos.avisoRecorte.hidden = !ampliada || totalFora === 0;
  elementos.avisoRecorte.textContent = ampliada && totalFora > 0
    ? `Ampliação vertical 10× ativa: ${totalFora.toLocaleString("pt-BR")} valores ficaram fora da área visível. Use Escala automática para ver todas as séries.`
    : "";
  elementos.estadoGraficos.textContent = `Dezena ${String(dados.dezena).padStart(2, "0")} · ${dados.tipo_evento} · ${dados.total.toLocaleString("pt-BR")} pontos · ${(dados.ocorrencias_reais || []).length.toLocaleString("pt-BR")} ocorrências reais.`;
}

async function consultarGraficos() {
  if (!elementos.formulario.reportValidity()) return;
  atualizarRetorno();
  elementos.estadoGraficos.textContent = "Consultando série histórica…";
  const parametros = new URLSearchParams(filtrosAtuais());
  try {
    renderizarGraficos(await respostaJson(await fetch(`/api/frequencias/serie?${parametros}`)));
  } catch (erro) {
    elementos.gradeGraficos.replaceChildren();
    elementos.estadoGraficos.textContent = erro.message;
  }
}

elementos.formulario.addEventListener("input", atualizarRetorno);
elementos.formulario.addEventListener("change", atualizarRetorno);
elementos.formulario.addEventListener("submit", (evento) => { evento.preventDefault(); consultarGraficos(); });
elementos.escalaVertical.addEventListener("change", () => {
  if (dadosAtuais) renderizarGraficos(dadosAtuais);
});
elementos.abrirAjuda.addEventListener("click", () => elementos.dialogoAjuda.showModal());
elementos.dialogoAjuda.addEventListener("click", (evento) => {
  if (evento.target === elementos.dialogoAjuda) elementos.dialogoAjuda.close();
});
if (filtros) {
  atualizarRetorno();
  consultarGraficos();
}
