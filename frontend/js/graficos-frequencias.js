import { filtrosGraficosDaUrl, urlRetornoFrequencias } from "./navegacao-graficos-frequencias.js";
import {
  adicionarFaixaDesvioPadrao, caminhoHistorico, criarEscalasHistorico, dominioHistorico,
  marcasEixoConcursos, poligonoFaixaHistorico, segmentosDegrausIntervalos,
} from "./frequencia-historico.js";
import { prepararIntervalosAuxiliares } from "./frequencia-intervalos-auxiliares.js";
import { renderizarCurvaDistribuicao } from "./frequencia-grafico-distribuicao.js";
import { renderizarOcorrenciasOrdenadas } from "./frequencia-grafico-ordenado.js";

const elementos = {
  formulario: document.querySelector("#form-graficos-frequencias"),
  dezena: document.querySelector("#graficos-dezena"),
  tipo: document.querySelector("#graficos-tipo-evento"),
  inicio: document.querySelector("#graficos-concurso-inicial"),
  fim: document.querySelector("#graficos-concurso-final"),
  mensagem: document.querySelector("#mensagem-graficos-auxiliares"),
  estadoGraficos: document.querySelector("#estado-area-graficos"),
  gradeGraficos: document.querySelector("#grade-graficos-historicos"),
  retornos: document.querySelectorAll("#link-voltar-frequencias, #botao-voltar-frequencias"),
  abrirAjuda: document.querySelector("#botao-ajuda-graficos"),
  dialogoAjuda: document.querySelector("#dialogo-ajuda-graficos"),
  dialogoAuxiliar: document.querySelector("#dialogo-grafico-auxiliar"),
  tituloAuxiliar: document.querySelector("#titulo-grafico-auxiliar"),
  legendaAuxiliar: document.querySelector("#legenda-grafico-auxiliar"),
  svgAuxiliar: document.querySelector("#svg-grafico-auxiliar"),
  detalheAuxiliar: document.querySelector("#detalhe-grafico-auxiliar"),
  abrirAjudaAuxiliar: document.querySelector("#botao-ajuda-grafico-auxiliar"),
  dialogoAjudaGrafico: document.querySelector("#dialogo-ajuda-grafico"),
  tituloAjudaGrafico: document.querySelector("#titulo-ajuda-grafico"),
  conteudoAjudaGrafico: document.querySelector("#conteudo-ajuda-grafico"),
};

let dadosAuxiliaresAtuais = null;
let tipoGraficoAuxiliarAtual = null;
let acionadorAjudaGrafico = null;

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

function caminhoSvg(svg, d, classe, descricao = "") {
  if (!d) return;
  const caminho = elementoSvg("path", { d, class: classe, fill: "none" });
  if (descricao) {
    const titulo = elementoSvg("title"); titulo.textContent = descricao; caminho.append(titulo);
  }
  svg.append(caminho);
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

function eixosHistorico(svg, escalas, dominio, marcas) {
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.inferior, x2: escalas.direita, y2: escalas.inferior, class: "historico-eixo" }));
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.topo, x2: escalas.direita, y2: escalas.topo, class: "historico-eixo" }));
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.topo, x2: escalas.esquerda, y2: escalas.inferior, class: "historico-eixo" }));
  for (let indice = 0; indice <= 8; indice += 1) {
    const fracao = indice / 8;
    const yValor = dominio.maximo - fracao * (dominio.maximo - dominio.minimo);
    svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.y(yValor), x2: escalas.direita, y2: escalas.y(yValor), class: "historico-grade-horizontal" }));
    const yTexto = elementoSvg("text", { x: escalas.esquerda - 10, y: escalas.y(yValor) + 4, class: "historico-rotulo", "text-anchor": "end" });
    yTexto.textContent = yValor.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
    svg.append(yTexto);
  }
  for (const concurso of marcas.regulares) {
    const x = escalas.x(concurso);
    svg.append(elementoSvg("line", { x1: x, y1: escalas.inferior, x2: x, y2: escalas.inferior + 6, class: "historico-eixo" }));
    const texto = elementoSvg("text", { x, y: escalas.inferior + 22, class: "historico-rotulo historico-rotulo--concurso", "text-anchor": "middle" });
    texto.textContent = concurso.toLocaleString("pt-BR");
    svg.append(texto);
  }
  for (const concurso of marcas.degraus) {
    const x = escalas.x(concurso);
    svg.append(elementoSvg("line", { x1: x, y1: escalas.topo, x2: x, y2: escalas.inferior, class: "historico-marca-degrau" }));
    const texto = elementoSvg("text", { x, y: escalas.topo - 10, class: "historico-rotulo historico-rotulo--degrau", "text-anchor": "middle" });
    texto.textContent = concurso.toLocaleString("pt-BR");
    svg.append(texto);
  }
  const tituloX = elementoSvg("text", { x: (escalas.esquerda + escalas.direita) / 2, y: escalas.altura - 7, class: "historico-titulo-eixo", "text-anchor": "middle" });
  tituloX.textContent = "Número do concurso";
  svg.append(tituloX);
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
  return { artigo, svg, meta: span, unidade };
}

function limparGraficoAuxiliar() {
  elementos.svgAuxiliar.replaceChildren();
  elementos.svgAuxiliar.removeAttribute("viewBox");
  elementos.svgAuxiliar.removeAttribute("role");
  elementos.svgAuxiliar.removeAttribute("aria-label");
  elementos.legendaAuxiliar.replaceChildren();
  elementos.detalheAuxiliar.textContent = "";
  elementos.tituloAuxiliar.textContent = "Gráfico auxiliar";
}

function itemLegenda(classe, texto) {
  const item = document.createElement("span");
  const amostra = document.createElement("i");
  amostra.className = classe;
  item.append(amostra, texto);
  return item;
}

function abrirGraficoAuxiliar(tipo) {
  if (!dadosAuxiliaresAtuais) return;
  limparGraficoAuxiliar();
  if (tipo === "distribuicao") {
    elementos.tituloAuxiliar.textContent = "Curva de distribuição dos intervalos";
    elementos.legendaAuxiliar.append(
      itemLegenda("auxiliar-legenda-real", "Distribuição observada"),
      itemLegenda("auxiliar-legenda-normal", "Curva normal teórica"),
      itemLegenda("auxiliar-legenda-media", "Média"),
      itemLegenda("auxiliar-legenda-desvio", "Média ± desvio-padrão"),
    );
    renderizarCurvaDistribuicao(
      elementos.svgAuxiliar, elementos.detalheAuxiliar, dadosAuxiliaresAtuais,
    );
  } else {
    elementos.tituloAuxiliar.textContent = "Ocorrências em ordem crescente";
    elementos.legendaAuxiliar.append(
      itemLegenda("auxiliar-legenda-ordenada", "Intervalos em ordem crescente"),
    );
    renderizarOcorrenciasOrdenadas(
      elementos.svgAuxiliar, elementos.detalheAuxiliar, dadosAuxiliaresAtuais,
    );
  }
  tipoGraficoAuxiliarAtual = tipo;
  elementos.dialogoAuxiliar.showModal();
}

function secaoAjuda(titulo, paragrafos = [], itens = []) {
  const secao = document.createElement("section");
  const cabecalho = document.createElement("h3");
  cabecalho.textContent = titulo;
  secao.append(cabecalho);
  for (const texto of paragrafos) {
    const paragrafo = document.createElement("p");
    paragrafo.textContent = texto;
    secao.append(paragrafo);
  }
  if (itens.length) {
    const lista = document.createElement("ul");
    for (const texto of itens) {
      const item = document.createElement("li");
      item.textContent = texto;
      lista.append(item);
    }
    secao.append(lista);
  }
  return secao;
}

function conteudoAjudaEvolucao() {
  return [
    secaoAjuda("Finalidade", [
      "Mostra como os intervalos entre ocorrências consecutivas da dezena e suas estatísticas acumuladas evoluíram ao longo dos concursos. Ajuda a observar estabilidade, mudanças de comportamento e intervalos excepcionalmente curtos ou longos.",
    ]),
    secaoAjuda("Como ler os eixos", [], [
      "Eixo horizontal: número do concurso.",
      "Eixo vertical: duração do intervalo, medida em concursos.",
    ]),
    secaoAjuda("Linhas e marcadores", [], [
      "Intervalos: cada trecho horizontal representa a distância entre duas ocorrências consecutivas. A transição vertical tracejada inicia o próximo intervalo.",
      "Média dos intervalos: média acumulada dos intervalos conhecidos até aquele momento.",
      "Média menos desvio-padrão: referência inferior de dispersão.",
      "Média mais desvio-padrão: referência superior de dispersão.",
      "Losango com haste tracejada: intervalo estreito demais para aparecer claramente na escala horizontal.",
    ]),
    secaoAjuda("Como consultar", [
      "Passe o mouse, use o foco do teclado ou clique nos marcadores para consultar os concursos inicial e final e a duração exata do intervalo.",
    ]),
    secaoAjuda("Exemplo de leitura", [
      "Concursos 1246 → 1261 · intervalo 15 significa que a dezena ocorreu nos concursos 1246 e 1261, com distância de 15 concursos. Compare esse valor com a média e com as linhas de desvio-padrão para avaliar se foi comum ou distante do comportamento acumulado.",
    ]),
    secaoAjuda("Cuidados de interpretação", [
      "O gráfico descreve o histórico. Média e desvio-padrão mudam quando novos intervalos são concluídos e não garantem quando acontecerá a próxima ocorrência.",
    ]),
  ];
}

function conteudoAjudaDistribuicao() {
  return [
    secaoAjuda("Finalidade", [
      "Mostra com que frequência cada duração de intervalo ocorreu. Ajuda a identificar onde as ocorrências estão concentradas e a partir de qual duração os intervalos se tornam raros.",
    ]),
    secaoAjuda("Como ler os eixos", [], [
      "Eixo horizontal: duração do intervalo em concursos.",
      "Eixo vertical: percentual das ocorrências que tiveram aquela duração.",
    ]),
    secaoAjuda("Curvas e referências", [], [
      "Distribuição observada: frequência percentual realmente encontrada para cada duração.",
      "Curva normal teórica: referência matemática calculada com a mesma média e o mesmo desvio-padrão dos intervalos observados.",
      "Média: duração média dos intervalos.",
      "Média ± desvio-padrão: referências verticais de um desvio abaixo e acima da média.",
    ]),
    secaoAjuda("Como consultar", [
      "Selecione um ponto da distribuição observada para consultar a duração, a quantidade de ocorrências e o percentual exato.",
    ]),
    secaoAjuda("Exemplo de leitura", [
      "Intervalo 4: 28 ocorrências · 11,07% significa que 28 intervalos analisados duraram quatro concursos, representando 11,07% do total.",
    ]),
    secaoAjuda("Cuidados de interpretação", [
      "A curva normal é apenas uma comparação teórica. Como intervalos são valores inteiros e a distribuição pode ser assimétrica e concentrada em durações pequenas, a distribuição observada não precisa acompanhar a curva normal.",
      "O gráfico descreve frequências históricas e não garante quando acontecerá a próxima ocorrência.",
    ]),
  ];
}

function conteudoAjudaOrdenado() {
  return [
    secaoAjuda("Finalidade", [
      "Ordena todos os intervalos do menor para o maior, preservando cada ocorrência repetida. Permite estimar visualmente qual percentual dos intervalos está concentrado até determinada proporção do maior intervalo.",
    ]),
    secaoAjuda("Como ler os eixos", [], [
      "Eixo horizontal: percentual acumulado das ocorrências ordenadas.",
      "Eixo vertical: duração do intervalo como percentual do maior intervalo observado.",
      "Os dois eixos vão de 0% a 100%. As linhas finas de 5% formam apenas um quadriculado de referência; os pontos usam seus percentuais exatos e podem ficar entre as linhas.",
    ]),
    secaoAjuda("Como os pontos são calculados", [
      "Depois de ordenar N intervalos, a posição horizontal do item i é calculada por i dividido por N, vezes 100. Sua altura é a duração daquele intervalo dividida pelo maior intervalo, vezes 100.",
    ]),
    secaoAjuda("Pontos, patamares e saltos", [], [
      "Cada ponto vermelho representa uma ocorrência de intervalo.",
      "Os pontos são igualmente espaçados na horizontal porque representam ocorrências consecutivas da lista ordenada.",
      "Intervalos repetidos ficam na mesma altura e formam um patamar. Quanto maior o patamar, mais vezes essa duração ocorreu.",
      "Um salto vertical maior pode indicar que as durações intermediárias não ocorreram; não significa necessariamente erro de ordenação.",
      "O último ponto é sempre (100%, 100%), pois representa a última ocorrência ordenada e o maior intervalo observado.",
    ]),
    secaoAjuda("Como consultar um ponto", [
      "Passe o mouse, use o foco do teclado ou clique em um ponto vermelho para exibir sua ordem, percentual acumulado, duração real em concursos e percentual do maior intervalo.",
    ]),
    secaoAjuda("Exemplo de leitura", [
      "Ocorrência 32 de 253 · 12,65% acumulado · intervalo 2 · 4% do maior significa que este é o 32º intervalo da lista ordenada, completa 12,65% das ocorrências, durou dois concursos e equivale a 4% do maior intervalo da amostra.",
    ]),
    secaoAjuda("Cuidados de interpretação", [
      "O gráfico descreve concentração e dispersão dos intervalos históricos. Ele não classifica automaticamente as dezenas nem garante maior probabilidade no próximo concurso.",
    ]),
  ];
}

function abrirAjudaGrafico(tipo, acionador) {
  const titulos = {
    evolucao: "Ajuda — Evolução dos intervalos",
    distribuicao: "Ajuda — Curva de distribuição",
    ordenado: "Ajuda — Ocorrências em ordem crescente",
  };
  acionadorAjudaGrafico = acionador;
  elementos.tituloAjudaGrafico.textContent = titulos[tipo];
  elementos.conteudoAjudaGrafico.replaceChildren();
  if (tipo === "evolucao") {
    elementos.conteudoAjudaGrafico.append(...conteudoAjudaEvolucao());
  } else if (tipo === "distribuicao") {
    elementos.conteudoAjudaGrafico.append(...conteudoAjudaDistribuicao());
  } else if (tipo === "ordenado") {
    elementos.conteudoAjudaGrafico.append(...conteudoAjudaOrdenado());
  } else {
    const aviso = document.createElement("p");
    aviso.textContent = "O conteúdo explicativo deste gráfico será inserido na próxima subetapa específica.";
    elementos.conteudoAjudaGrafico.append(aviso);
  }
  elementos.dialogoAjudaGrafico.showModal();
}

function controlesGraficosAuxiliares() {
  const acoes = document.createElement("div");
  acoes.className = "historico-acoes-auxiliares";
  const distribuicao = document.createElement("button");
  distribuicao.type = "button";
  distribuicao.textContent = "Curva de distribuição";
  distribuicao.addEventListener("click", () => abrirGraficoAuxiliar("distribuicao"));
  const ordenado = document.createElement("button");
  ordenado.type = "button";
  ordenado.textContent = "Ocorrências em ordem crescente";
  ordenado.addEventListener("click", () => abrirGraficoAuxiliar("ordenado"));
  const ajuda = document.createElement("button");
  ajuda.type = "button";
  ajuda.className = "botao-ajuda-evolucao-intervalos";
  ajuda.textContent = "Ajuda";
  ajuda.addEventListener("click", () => abrirAjudaGrafico("evolucao", ajuda));
  acoes.append(ajuda, distribuicao, ordenado);
  return acoes;
}

function renderizarGraficos(dados) {
  if (elementos.dialogoAuxiliar.open) elementos.dialogoAuxiliar.close();
  dadosAuxiliaresAtuais = prepararIntervalosAuxiliares(
    (dados.intervalos_individuais || []).map((item) => item.intervalo),
  );
  elementos.gradeGraficos.replaceChildren();
  if (!dados.pontos?.length) {
    elementos.estadoGraficos.textContent = "Não existem pontos históricos para os filtros selecionados.";
    return;
  }
  const periodo = dados.periodo;
  const margens = { esquerda: 72, direita: 20, topo: 48, inferior: 58 };
  const fatorX = (escalas) => ((escalas.direita - escalas.esquerda) / Math.max(1, periodo.concurso_final - periodo.concurso_inicial)).toFixed(3);
  const fatorY = (escalas, dominio) => ((escalas.inferior - escalas.topo) / (dominio.maximo - dominio.minimo)).toFixed(3);

  const intervalos = cartaoHistorico("Evolução dos intervalos", "eixo Y: intervalo em concursos");
  intervalos.artigo.insertBefore(controlesGraficosAuxiliares(), intervalos.svg);
  const pontosIntervalos = adicionarFaixaDesvioPadrao(dados.pontos);
  const camposIntervalos = [
    "media_menos_desvio", "media_intervalos", "media_mais_desvio",
  ];
  const valoresIndividuais = (dados.intervalos_individuais || []).map((item) => item.intervalo);
  const dominioIntervalos = dominioHistorico(pontosIntervalos, camposIntervalos, valoresIndividuais);
  if (dominioIntervalos) {
    const escalas = criarEscalasHistorico(periodo, dominioIntervalos, 1440, 500, margens);
    const marcas = marcasEixoConcursos(periodo);
    eixosHistorico(intervalos.svg, escalas, dominioIntervalos, marcas);
    intervalos.meta.textContent = `${intervalos.unidade} · fator X ${fatorX(escalas)} · fator Y ${fatorY(escalas, dominioIntervalos)}`;
    const camada = camadaDados(intervalos.svg, escalas, "recorte-intervalos");
    caminhoSvg(camada, caminhoHistorico(pontosIntervalos, "media_menos_desvio", escalas), "historico-linha historico-linha--desvio-inferior", "Média dos intervalos menos um desvio-padrão");
    caminhoSvg(camada, caminhoHistorico(pontosIntervalos, "media_intervalos", escalas), "historico-linha historico-linha--media");
    caminhoSvg(camada, caminhoHistorico(pontosIntervalos, "media_mais_desvio", escalas), "historico-linha historico-linha--desvio-superior", "Média dos intervalos mais um desvio-padrão");
    const degraus = segmentosDegrausIntervalos(dados.intervalos_individuais || [], escalas);
    const detalheCurto = document.createElement("p");
    detalheCurto.className = "historico-detalhe-intervalo-curto";
    detalheCurto.textContent = "Marcadores em losango identificam intervalos estreitos; selecione um para consultar os concursos.";
    for (const segmento of degraus.horizontais) {
      const linha = elementoSvg("path", { d: segmento.caminho, class: "historico-intervalo-degrau" });
      const titulo = elementoSvg("title");
      titulo.textContent = `Concursos ${segmento.item.concurso_anterior} a ${segmento.item.numero_do_concurso}: intervalo ${segmento.item.intervalo}`;
      linha.append(titulo); camada.append(linha);
      if (segmento.larguraProjetada < 8) {
        const x = (escalas.x(segmento.item.concurso_inicial_visivel) + escalas.x(segmento.item.concurso_final_visivel)) / 2;
        const y = escalas.y(segmento.item.intervalo);
        const descricao = `Concursos ${segmento.item.concurso_anterior} → ${segmento.item.numero_do_concurso} · intervalo ${segmento.item.intervalo}`;
        const marcador = elementoSvg("g", {
          class: "historico-intervalo-curto", tabindex: "0", role: "button",
          "aria-label": descricao,
        });
        marcador.append(
          elementoSvg("path", { d: `M${x.toFixed(2)},${(y - 10).toFixed(2)} L${x.toFixed(2)},${(y + 10).toFixed(2)}`, class: "historico-intervalo-curto__haste" }),
          elementoSvg("path", { d: `M${x.toFixed(2)},${(y - 5).toFixed(2)} L${(x + 5).toFixed(2)},${y.toFixed(2)} L${x.toFixed(2)},${(y + 5).toFixed(2)} L${(x - 5).toFixed(2)},${y.toFixed(2)} Z`, class: "historico-intervalo-curto__marca" }),
        );
        const tituloCurto = elementoSvg("title"); tituloCurto.textContent = descricao; marcador.append(tituloCurto);
        const mostrar = () => { detalheCurto.textContent = descricao; };
        marcador.addEventListener("mouseenter", mostrar);
        marcador.addEventListener("focus", mostrar);
        marcador.addEventListener("click", mostrar);
        camada.append(marcador);
      }
    }
    for (const transicao of degraus.transicoes) {
      const linha = elementoSvg("path", { d: transicao.caminho, class: "historico-intervalo-transicao" });
      const titulo = elementoSvg("title");
      titulo.textContent = `Nova ocorrência no concurso ${transicao.concurso}`;
      linha.append(titulo); camada.append(linha);
    }
    intervalos.artigo.append(detalheCurto);
  }

  const previsao = cartaoHistorico("Faixa prevista e ocorrências reais", "eixo Y: número previsto do concurso");
  const camposPrevisao = ["limite_inferior_exato", "previsao_central", "limite_superior_exato"];
  const dominioPrevisao = dominioHistorico(dados.pontos, camposPrevisao, dados.ocorrencias_reais);
  if (dominioPrevisao) {
    const escalas = criarEscalasHistorico(periodo, dominioPrevisao, 1440, 500, margens);
    eixosHistorico(previsao.svg, escalas, dominioPrevisao, marcasEixoConcursos(periodo));
    previsao.meta.textContent = `${previsao.unidade} · fator X ${fatorX(escalas)} · fator Y ${fatorY(escalas, dominioPrevisao)}`;
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
  elementos.estadoGraficos.textContent = `Dezena ${String(dados.dezena).padStart(2, "0")}: ${dados.total.toLocaleString("pt-BR")} concursos · ${(dados.ocorrencias_reais || []).length.toLocaleString("pt-BR")} ocorrências`;
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
elementos.abrirAjuda.addEventListener("click", () => elementos.dialogoAjuda.showModal());
elementos.dialogoAjuda.addEventListener("click", (evento) => {
  if (evento.target === elementos.dialogoAjuda) elementos.dialogoAjuda.close();
});
elementos.dialogoAuxiliar.addEventListener("close", limparGraficoAuxiliar);
elementos.dialogoAuxiliar.addEventListener("click", (evento) => {
  if (evento.target === elementos.dialogoAuxiliar) elementos.dialogoAuxiliar.close();
});
elementos.abrirAjudaAuxiliar.addEventListener("click", () => {
  if (tipoGraficoAuxiliarAtual) {
    abrirAjudaGrafico(tipoGraficoAuxiliarAtual, elementos.abrirAjudaAuxiliar);
  }
});
elementos.dialogoAjudaGrafico.addEventListener("click", (evento) => {
  if (evento.target === elementos.dialogoAjudaGrafico) elementos.dialogoAjudaGrafico.close();
});
elementos.dialogoAjudaGrafico.addEventListener("close", () => {
  elementos.conteudoAjudaGrafico.replaceChildren();
  if (acionadorAjudaGrafico?.isConnected) acionadorAjudaGrafico.focus();
  acionadorAjudaGrafico = null;
});
if (filtros) {
  atualizarRetorno();
  consultarGraficos();
}
