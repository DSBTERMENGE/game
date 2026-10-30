import { criarControleFrequencia, criarEstadoInicialFrequencia, descreverPreviaFrequencia } from "./frequencia-controles.js";
import { criarModalAndamento } from "./modal-andamento.js";
import { MEDICOES_FREQUENCIA, formatarMedicaoFrequencia, prepararBarrasFrequencia } from "./frequencia-graficos.js";
import { caminhoHistorico, criarEscalasHistorico, dominioHistorico, poligonoFaixaHistorico } from "./frequencia-historico.js";

const CAMPOS_FIXOS = {
  regra_janela: "INICIO_FIXO_FINAL_EXPANSIVO",
  metodo_faixa: "MEDIA_MAIS_MENOS_DESVIO_PADRAO",
  unidade_parametro: "MULTIPLICADOR_DESVIO_PADRAO",
  regra_arredondamento: "LIMITES_EXTERNOS",
};
const ROTULOS = {
  nome: "Nome", concurso_inicial: "Concurso inicial", tamanho_inicial: "Tamanho inicial",
  regra_janela: "Regra da janela", tipo_evento: "Eventos calculados",
  metodo_faixa: "Método da faixa", parametro_faixa: "Multiplicador do desvio-padrão",
  unidade_parametro: "Unidade do parâmetro", regra_arredondamento: "Arredondamento",
  versao_calculo: "Versão do cálculo",
};

const e = {
  mensagem: document.querySelector("#mensagem-frequencias"),
  recarregar: document.querySelector("#botao-recarregar-frequencias"),
  resultados: document.querySelector("#resumo-resultados"),
  concursos: document.querySelector("#resumo-concursos"),
  ultimo: document.querySelector("#resumo-ultimo-processado"),
  linhas: document.querySelector("#resumo-linhas"),
  estado: document.querySelector("#resumo-estado"),
  gravada: document.querySelector("#configuracao-gravada"),
  assinatura: document.querySelector("#assinatura-configuracao"),
  formulario: document.querySelector("#form-configuracao-frequencia"),
  nome: document.querySelector("#frequencia-nome"),
  concursoInicial: document.querySelector("#frequencia-concurso-inicial"),
  tamanhoInicial: document.querySelector("#frequencia-tamanho-inicial"),
  tipoEvento: document.querySelector("#frequencia-tipo-evento"),
  parametroFaixa: document.querySelector("#frequencia-parametro-faixa"),
  versaoCalculo: document.querySelector("#frequencia-versao-calculo"),
  salvar: document.querySelector("#frequencia-salvar-dados"),
  reconstruir: document.querySelector("#frequencia-reconstruir-origem"),
  previa: document.querySelector("#previa-frequencia"),
  calcularPrevia: document.querySelector("#botao-calcular-previa-frequencia"),
  executar: document.querySelector("#botao-executar-frequencia"),
  tipoGrafico: document.querySelector("#frequencia-tipo-grafico"),
  mensagemGraficos: document.querySelector("#mensagem-graficos-frequencia"),
  periodoGrafico: document.querySelector("#grafico-periodo"),
  intervalosGrafico: document.querySelector("#grafico-intervalos"),
  unidadeGrafico: document.querySelector("#grafico-unidade"),
  atualizadoGrafico: document.querySelector("#grafico-atualizado"),
  gradeGraficos: document.querySelector("#grade-graficos-frequencia"),
  formHistorico: document.querySelector("#form-historico-frequencia"),
  dezenaHistorico: document.querySelector("#historico-dezena"),
  tipoHistorico: document.querySelector("#historico-tipo-evento"),
  inicioHistorico: document.querySelector("#historico-concurso-inicial"),
  fimHistorico: document.querySelector("#historico-concurso-final"),
  mensagemHistorico: document.querySelector("#mensagem-historico-frequencia"),
  gradeHistorico: document.querySelector("#grade-historico-frequencia"),
  avaliaveis: document.querySelector("#assertividade-avaliaveis"),
  acertos: document.querySelector("#assertividade-acertos"),
  erros: document.querySelector("#assertividade-erros"),
  censurados: document.querySelector("#assertividade-censurados"),
  percentualAcerto: document.querySelector("#assertividade-percentual"),
  erroAbsoluto: document.querySelector("#assertividade-erro-absoluto"),
  erroPercentual: document.querySelector("#assertividade-erro-percentual"),
  corpoErros: document.querySelector("#corpo-erros-assertividade"),
  semErros: document.querySelector("#assertividade-sem-erros"),
};

let previaAtual = null;
let solicitacaoAtual = null;

async function respostaJson(resposta) {
  let dados;
  try { dados = await resposta.json(); }
  catch (_erro) { throw new Error(`O servidor devolveu uma resposta inválida (HTTP ${resposta.status}).`); }
  if (!resposta.ok) throw new Error(dados.erro?.mensagem || `Falha HTTP ${resposta.status}.`);
  return dados;
}

function inteiro(elemento) { return Number.parseInt(elemento.value, 10); }
function configuracaoCalculada() {
  return {
    nome: e.nome.value.trim(),
    concurso_inicial: inteiro(e.concursoInicial),
    tamanho_inicial: inteiro(e.tamanhoInicial),
    ...CAMPOS_FIXOS,
    tipo_evento: e.tipoEvento.value,
    parametro_faixa: e.parametroFaixa.value,
    versao_calculo: inteiro(e.versaoCalculo),
  };
}

function preencherFormulario(configuracao) {
  e.nome.value = configuracao.nome;
  e.concursoInicial.value = configuracao.concurso_inicial;
  e.tamanhoInicial.value = configuracao.tamanho_inicial;
  e.tipoEvento.value = configuracao.tipo_evento;
  e.parametroFaixa.value = configuracao.parametro_faixa;
  e.versaoCalculo.value = configuracao.versao_calculo;
}

function renderizarConfiguracao(configuracao) {
  e.gravada.replaceChildren();
  for (const [campo, rotulo] of Object.entries(ROTULOS)) {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = rotulo;
    dd.textContent = configuracao[campo] ?? "—";
    e.gravada.append(dt, dd);
  }
  e.assinatura.textContent = `Assinatura: ${configuracao.assinatura_sha256 || "—"}`;
}

function intervalo(resultados) {
  if (resultados.concurso_inicial == null) return "—";
  return `${resultados.concurso_inicial.toLocaleString("pt-BR")} a ${resultados.concurso_final.toLocaleString("pt-BR")}`;
}

function renderizarEstado(dados, preencher = false) {
  const resultados = dados.resultados || {};
  const geracao = dados.geracao_ativa;
  e.resultados.textContent = Number(resultados.quantidade || 0).toLocaleString("pt-BR");
  e.concursos.textContent = intervalo(resultados);
  e.ultimo.textContent = geracao?.concurso_final?.toLocaleString("pt-BR") || "Não processado";
  e.linhas.textContent = Number(dados.linhas_historicas || 0).toLocaleString("pt-BR");
  e.estado.textContent = geracao ? geracao.estado : "Sem geração ativa";
  renderizarConfiguracao(dados.configuracao_ativa);
  if (preencher) preencherFormulario(dados.configuracao_ativa);
  if (dados.geracao_ativa && !e.inicioHistorico.value) {
    e.inicioHistorico.value = dados.geracao_ativa.concurso_inicial;
    e.fimHistorico.value = dados.geracao_ativa.concurso_final;
  }
}

async function carregarEstado({ preencher = false } = {}) {
  e.mensagem.textContent = "Consultando o estado da base…";
  e.mensagem.dataset.tipo = "";
  try {
    const dados = await respostaJson(await fetch("/api/frequencias/estado"));
    renderizarEstado(dados, preencher);
    e.mensagem.textContent = "Estado da frequência carregado.";
    e.mensagem.dataset.tipo = "sucesso";
  } catch (erro) {
    e.mensagem.textContent = erro.message;
    e.mensagem.dataset.tipo = "erro";
  }
}

const SVG_NS = "http://www.w3.org/2000/svg";
function elementoSvg(nome, atributos = {}) {
  const elemento = document.createElementNS(SVG_NS, nome);
  for (const [atributo, valor] of Object.entries(atributos)) elemento.setAttribute(atributo, String(valor));
  return elemento;
}

function criarGrafico(medicao, dezenas) {
  const artigo = document.createElement("article");
  artigo.className = "frequencias-grafico-cartao";
  const titulo = document.createElement("h3");
  titulo.textContent = medicao.titulo;
  const unidade = document.createElement("span");
  unidade.textContent = medicao.unidade;
  const cabecalho = document.createElement("header");
  cabecalho.append(titulo, unidade);
  const barras = prepararBarrasFrequencia(dezenas, medicao.campo);
  const svg = elementoSvg("svg", {
    class: "grafico-frequencia", viewBox: "0 0 970 235", role: "img",
    "aria-label": `${medicao.titulo} das dezenas 1 a 60`, preserveAspectRatio: "none",
  });
  svg.append(elementoSvg("line", { x1: 35, y1: 195, x2: 960, y2: 195, class: "grafico-frequencia-eixo" }));
  barras.forEach((barra, indice) => {
    const x = 40 + indice * 15.25;
    const altura = barra.proporcao * 165;
    const retangulo = elementoSvg("rect", {
      x, y: 195 - altura, width: 11, height: altura,
      class: barra.valor === null ? "grafico-frequencia-barra grafico-frequencia-barra--nula" : "grafico-frequencia-barra",
    });
    const descricao = elementoSvg("title");
    descricao.textContent = `Dezena ${String(barra.dezena).padStart(2, "0")}: ${formatarMedicaoFrequencia(barra.valor, medicao.casas)} ${barra.valor === null ? "" : medicao.unidade}; ${barra.quantidadeIntervalos} intervalos`;
    retangulo.append(descricao);
    svg.append(retangulo);
    if (indice % 5 === 0 || indice === 59) {
      const rotulo = elementoSvg("text", { x: x + 5.5, y: 214, class: "grafico-frequencia-rotulo", "text-anchor": "middle" });
      rotulo.textContent = String(barra.dezena).padStart(2, "0");
      svg.append(rotulo);
    }
  });
  artigo.append(cabecalho, svg);
  return artigo;
}

function renderizarFotografia(dados) {
  e.gradeGraficos.replaceChildren();
  const dezenas = dados.dezenas || [];
  if (dezenas.length !== 60) {
    e.mensagemGraficos.textContent = `Não há fotografia completa de ${dados.tipo_evento} na geração ativa.`;
    return;
  }
  for (const medicao of MEDICOES_FREQUENCIA) e.gradeGraficos.append(criarGrafico(medicao, dezenas));
  e.periodoGrafico.textContent = `${dados.concurso_inicial.toLocaleString("pt-BR")} a ${dados.concurso_final.toLocaleString("pt-BR")}`;
  e.intervalosGrafico.textContent = dezenas.reduce((total, item) => total + Number(item.quantidade_intervalos || 0), 0).toLocaleString("pt-BR");
  e.unidadeGrafico.textContent = dados.unidade_intervalos === "CONCURSOS" ? "concursos" : dados.unidade_intervalos;
  e.atualizadoGrafico.textContent = dados.atualizado_em ? new Date(dados.atualizado_em).toLocaleString("pt-BR") : "—";
  e.mensagemGraficos.textContent = `Fotografia ${dados.tipo_evento}: 60 dezenas no concurso ${dados.concurso_final.toLocaleString("pt-BR")}.`;
}

async function carregarFotografia() {
  e.mensagemGraficos.textContent = "Carregando fotografia atual…";
  e.tipoGrafico.disabled = true;
  try {
    const tipo = encodeURIComponent(e.tipoGrafico.value);
    renderizarFotografia(await respostaJson(await fetch(`/api/frequencias/fotografia-atual?tipo_evento=${tipo}`)));
  } catch (erro) {
    e.gradeGraficos.replaceChildren();
    e.mensagemGraficos.textContent = erro.message;
  } finally {
    e.tipoGrafico.disabled = false;
  }
}

function caminhoSvg(svg, d, classe) {
  if (!d) return;
  svg.append(elementoSvg("path", { d, class: classe, fill: "none" }));
}

function eixosHistorico(svg, escalas, dominio, periodo) {
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.inferior, x2: escalas.direita, y2: escalas.inferior, class: "historico-eixo" }));
  svg.append(elementoSvg("line", { x1: escalas.esquerda, y1: escalas.topo, x2: escalas.esquerda, y2: escalas.inferior, class: "historico-eixo" }));
  for (let indice = 0; indice <= 4; indice += 1) {
    const fracao = indice / 4;
    const xValor = Math.round(periodo.concurso_inicial + fracao * (periodo.concurso_final - periodo.concurso_inicial));
    const yValor = dominio.maximo - fracao * (dominio.maximo - dominio.minimo);
    const xTexto = elementoSvg("text", { x: escalas.x(xValor), y: escalas.inferior + 18, class: "historico-rotulo", "text-anchor": "middle" });
    xTexto.textContent = xValor.toLocaleString("pt-BR");
    const yTexto = elementoSvg("text", { x: escalas.esquerda - 6, y: escalas.y(yValor) + 3, class: "historico-rotulo", "text-anchor": "end" });
    yTexto.textContent = yValor.toLocaleString("pt-BR", { maximumFractionDigits: 1 });
    svg.append(xTexto, yTexto);
  }
}

function cartaoHistorico(titulo, subtitulo) {
  const artigo = document.createElement("article");
  artigo.className = "historico-cartao";
  const header = document.createElement("header"), h3 = document.createElement("h3"), span = document.createElement("span");
  h3.textContent = titulo; span.textContent = subtitulo; header.append(h3, span);
  const svg = elementoSvg("svg", { class: "grafico-historico", viewBox: "0 0 960 245", role: "img", "aria-label": titulo, preserveAspectRatio: "none" });
  artigo.append(header, svg);
  return { artigo, svg };
}

function textoDecimal(valor, sufixo = "") {
  if (valor === null || valor === undefined) return "—";
  return `${Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}${sufixo}`;
}

function celulaAssertividade(texto) {
  const td = document.createElement("td"); td.textContent = texto ?? "—"; return td;
}

function renderizarAssertividade(assertividade) {
  e.avaliaveis.textContent = Number(assertividade.avaliaveis).toLocaleString("pt-BR");
  e.acertos.textContent = Number(assertividade.acertos).toLocaleString("pt-BR");
  e.erros.textContent = Number(assertividade.erros).toLocaleString("pt-BR");
  e.censurados.textContent = Number(assertividade.censurados).toLocaleString("pt-BR");
  e.percentualAcerto.textContent = textoDecimal(assertividade.percentual_acerto, "%");
  e.erroAbsoluto.textContent = textoDecimal(assertividade.erro_absoluto_medio, " concursos");
  e.erroPercentual.textContent = textoDecimal(assertividade.erro_percentual_medio, "%");
  const erros = assertividade.avaliacoes.filter((item) => item.estado.startsWith("ERRO_"));
  e.corpoErros.replaceChildren();
  for (const item of erros) {
    const tr = document.createElement("tr");
    tr.append(
      celulaAssertividade(item.numero_do_concurso), celulaAssertividade(item.concurso_anterior),
      celulaAssertividade(`${item.limite_inferior} a ${item.limite_superior}`),
      celulaAssertividade(item.concurso_real),
      celulaAssertividade(item.estado === "ERRO_ABAIXO" ? "Abaixo da faixa" : "Acima da faixa"),
      celulaAssertividade(textoDecimal(item.erro_absoluto)),
      celulaAssertividade(textoDecimal(item.erro_percentual, "%")),
    );
    e.corpoErros.append(tr);
  }
  e.semErros.hidden = erros.length !== 0;
}

function renderizarHistorico(dados) {
  e.gradeHistorico.replaceChildren();
  if (!dados.pontos?.length) {
    e.mensagemHistorico.textContent = "Não existem pontos históricos para os filtros selecionados.";
    return;
  }
  const periodo = dados.periodo;
  const intervalos = cartaoHistorico("Evolução dos intervalos", "eixo Y em concursos");
  const dominioIntervalos = dominioHistorico(dados.pontos, ["intervalo_minimo", "media_intervalos", "intervalo_maximo"]);
  if (dominioIntervalos) {
    const escalas = criarEscalasHistorico(periodo, dominioIntervalos);
    eixosHistorico(intervalos.svg, escalas, dominioIntervalos, periodo);
    caminhoSvg(intervalos.svg, caminhoHistorico(dados.pontos, "intervalo_minimo", escalas), "historico-linha historico-linha--minimo");
    caminhoSvg(intervalos.svg, caminhoHistorico(dados.pontos, "media_intervalos", escalas), "historico-linha historico-linha--media");
    caminhoSvg(intervalos.svg, caminhoHistorico(dados.pontos, "intervalo_maximo", escalas), "historico-linha historico-linha--maximo");
  }

  const previsao = cartaoHistorico("Faixa prevista e ocorrências reais", "eixo Y: número do concurso");
  const dominioPrevisao = dominioHistorico(dados.pontos, ["limite_inferior_exato", "previsao_central", "limite_superior_exato"], dados.ocorrencias_reais);
  if (dominioPrevisao) {
    const escalas = criarEscalasHistorico(periodo, dominioPrevisao);
    eixosHistorico(previsao.svg, escalas, dominioPrevisao, periodo);
    const faixa = poligonoFaixaHistorico(dados.pontos, "limite_inferior_exato", "limite_superior_exato", escalas);
    if (faixa) previsao.svg.append(elementoSvg("polygon", { points: faixa, class: "historico-faixa" }));
    caminhoSvg(previsao.svg, caminhoHistorico(dados.pontos, "previsao_central", escalas), "historico-linha historico-linha--media");
    for (const concurso of dados.ocorrencias_reais || []) {
      const circulo = elementoSvg("circle", { cx: escalas.x(concurso), cy: escalas.y(concurso), r: 3.2, class: "historico-ocorrencia" });
      const titulo = elementoSvg("title"); titulo.textContent = `Ocorrência real no concurso ${concurso}`; circulo.append(titulo); previsao.svg.append(circulo);
    }
  }
  e.gradeHistorico.append(intervalos.artigo, previsao.artigo);
  renderizarAssertividade(dados.assertividade);
  e.mensagemHistorico.textContent = `Dezena ${String(dados.dezena).padStart(2, "0")} · ${dados.tipo_evento} · ${dados.total.toLocaleString("pt-BR")} pontos · ${(dados.ocorrencias_reais || []).length.toLocaleString("pt-BR")} ocorrências reais.`;
}

async function carregarHistorico() {
  if (!e.formHistorico.reportValidity()) return;
  e.mensagemHistorico.textContent = "Consultando série histórica…";
  const parametros = new URLSearchParams({
    dezena: e.dezenaHistorico.value, tipo_evento: e.tipoHistorico.value,
    concurso_inicial: e.inicioHistorico.value, concurso_final: e.fimHistorico.value,
  });
  try { renderizarHistorico(await respostaJson(await fetch(`/api/frequencias/serie?${parametros}`))); }
  catch (erro) { e.gradeHistorico.replaceChildren(); e.mensagemHistorico.textContent = erro.message; }
}

async function calcularPrevia() {
  if (!e.formulario.reportValidity()) return null;
  e.previa.textContent = "Calculando prévia…";
  const dados = await respostaJson(await fetch("/api/frequencias/previa", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ configuracao: configuracaoCalculada(), salvar_dados: e.salvar.checked }),
  }));
  previaAtual = dados;
  e.previa.textContent = descreverPreviaFrequencia(dados);
  return dados;
}

function corpoExecucao(confirmacaoGravacao) {
  return {
    configuracao: configuracaoCalculada(),
    salvar_dados: e.salvar.checked,
    confirmacao_gravacao: confirmacaoGravacao,
    reconstruir_origem: e.reconstruir.checked,
  };
}

function diagnosticoExecucao(resultado) {
  const linhas = Number(resultado?.linhas_calculadas ?? resultado?.fotografias_inseridas ?? 0);
  const tipo = resultado?.tipo === "GRAVACAO" ? "Dados gravados" : "Simulação concluída sem gravação";
  return { aprovado: true, mensagem: `${tipo}. ${linhas.toLocaleString("pt-BR")} linhas processadas.` };
}

const modal = criarModalAndamento({
  titulo: "Processando frequência das dezenas",
  iniciar: async () => respostaJson(await fetch("/api/frequencias/execucoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitacaoAtual),
  })),
  consultar: async (id) => respostaJson(await fetch(`/api/frequencias/execucoes/${encodeURIComponent(id)}`)),
  cancelar: async (id) => respostaJson(await fetch(`/api/frequencias/execucoes/${encodeURIComponent(id)}/cancelamento`, { method: "POST" })),
  apresentarResultado: diagnosticoExecucao,
});

async function abrirExecucao(confirmacaoGravacao) {
  solicitacaoAtual = corpoExecucao(confirmacaoGravacao);
  const final = await modal.abrir();
  if (final?.estado === "CONCLUIDA" && solicitacaoAtual.salvar_dados) {
    await Promise.all([carregarEstado(), carregarFotografia()]);
  }
  return final;
}

const controle = criarControleFrequencia({
  confirmar: async (mensagem, detalhe) => window.confirm(`${mensagem}\n\n${detalhe}`),
  salvar: async ({ confirmacao_gravacao }) => abrirExecucao(confirmacao_gravacao),
  simular: async () => abrirExecucao(false),
});

function invalidarPrevia() {
  previaAtual = null;
  e.previa.textContent = "A configuração mudou. Calcule novamente a prévia antes de executar.";
}

e.formulario.addEventListener("input", invalidarPrevia);
e.salvar.addEventListener("change", invalidarPrevia);
e.reconstruir.addEventListener("change", invalidarPrevia);
e.calcularPrevia.addEventListener("click", async () => {
  e.calcularPrevia.disabled = true;
  try { await calcularPrevia(); }
  catch (erro) { e.previa.textContent = erro.message; }
  finally { e.calcularPrevia.disabled = false; }
});
e.executar.addEventListener("click", async () => {
  if (controle.estaExecutando() || modal.estaExecutando()) return;
  e.executar.disabled = true;
  try {
    const previa = previaAtual || await calcularPrevia();
    if (previa) await controle.executar({ previa, salvarDados: e.salvar.checked });
  } catch (erro) {
    e.previa.textContent = erro.message;
  } finally {
    e.executar.disabled = false;
  }
});
e.recarregar.addEventListener("click", () => carregarEstado());
e.tipoGrafico.addEventListener("change", carregarFotografia);
e.formHistorico.addEventListener("submit", (evento) => { evento.preventDefault(); carregarHistorico(); });

const inicial = criarEstadoInicialFrequencia();
e.salvar.checked = inicial.salvarDados;
for (let dezena = 1; dezena <= 60; dezena += 1) {
  const opcao = document.createElement("option"); opcao.value = String(dezena); opcao.textContent = String(dezena).padStart(2, "0"); e.dezenaHistorico.append(opcao);
}
Promise.all([carregarEstado({ preencher: true }), carregarFotografia()]);
