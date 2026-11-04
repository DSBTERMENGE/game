import { formatarDezenas, idsComparacao, montarConfiguracao } from "./selecao-dezenas-controles.js";
import { criarModalAndamento } from "./modal-andamento.js";

const e = Object.fromEntries([
  "mensagem-selecao", "configuracao-gravada-selecao", "selecao-nome", "selecao-fator-k",
  "selecao-fator-j", "selecao-modo-quantidade", "selecao-quantidade", "selecao-horizonte",
  "selecao-versao", "assinatura-selecao", "botao-previa-selecao", "botao-salvar-configuracao",
  "resultado-previa-selecao", "botao-atualizar-previsao", "resumo-previsao", "corpo-previsoes",
  "form-backtest-selecao", "backtest-inicial", "backtest-final",
  "estado-backtest", "resumo-backtest", "classes-backtest",
  "form-comparacao-selecao", "comparacao-ids", "resultado-comparacao",
  "corpo-detalhes-backtest", "painel-jogos", "resumo-jogos", "botao-gerar-jogos",
  "botao-ajuda-selecao", "dialogo-ajuda-selecao",
  "dialogo-previa-backtest", "previa-backtest-resultados", "previa-backtest-periodo",
  "previa-backtest-quantidade", "previa-backtest-configuracao", "botao-confirmar-backtest",
].map((id) => [id.replaceAll("-", "_"), document.getElementById(id)]));

let configuracoes = [];
let alvoJogos = null;
let previaJogos = null;
let solicitacaoBacktest = null;
let modalBacktest = null;

async function respostaJson(resposta) {
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(dados.erro?.mensagem || `Erro HTTP ${resposta.status}.`);
  return dados;
}

function mensagem(texto, tipo = "") {
  e.mensagem_selecao.textContent = texto;
  e.mensagem_selecao.dataset.tipo = tipo;
}

function configuracaoFormulario() {
  return montarConfiguracao({
    nome: e.selecao_nome.value, fator_k: e.selecao_fator_k.value,
    fator_j: e.selecao_fator_j.value, modo_quantidade: e.selecao_modo_quantidade.value,
    quantidade_dezenas: e.selecao_quantidade.value,
    horizonte_concursos: e.selecao_horizonte.value, versao_calculo: e.selecao_versao.value,
  });
}

function preencherConfiguracao(configuracao) {
  e.selecao_nome.value = configuracao.nome;
  e.selecao_fator_k.value = configuracao.fator_k;
  e.selecao_fator_j.value = configuracao.fator_j;
  e.selecao_modo_quantidade.value = configuracao.modo_quantidade;
  e.selecao_quantidade.value = configuracao.quantidade_dezenas ?? "";
  e.selecao_quantidade.disabled = configuracao.modo_quantidade !== "FIXA";
  e.selecao_horizonte.value = configuracao.horizonte_concursos;
  e.selecao_versao.value = configuracao.versao_calculo;
  e.assinatura_selecao.textContent = `Assinatura: ${configuracao.assinatura_sha256 || "será calculada ao salvar"}`;
}

async function carregarConfiguracoes() {
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/configuracoes"));
  configuracoes = dados.configuracoes || [];
  e.configuracao_gravada_selecao.replaceChildren(new Option("Nova configuração", ""));
  for (const item of configuracoes) e.configuracao_gravada_selecao.append(new Option(
    `${item.id_configuracao_selecao} — ${item.configuracao.nome}`,
    item.id_configuracao_selecao,
  ));
  if (configuracoes.length) {
    const ultima = configuracoes.at(-1);
    e.configuracao_gravada_selecao.value = ultima.id_configuracao_selecao;
    preencherConfiguracao(ultima.configuracao);
  }
  mensagem(`${configuracoes.length} configuração(ões) disponível(is).`, "sucesso");
}

async function calcularPrevia() {
  const corpo = { configuracao: configuracaoFormulario() };
  const inicio = Number(e.backtest_inicial.value);
  const final = Number(e.backtest_final.value);
  if (Number.isInteger(inicio)) corpo.concurso_inicial = inicio;
  if (Number.isInteger(final) && final > 0) corpo.concurso_final = final;
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/previa", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo),
  }));
  e.resultado_previa_selecao.hidden = false;
  e.resultado_previa_selecao.textContent = `Base: concursos ${dados.resultados.primeiro} a ${dados.resultados.ultimo}. Backtest: ${dados.backtest.quantidade_alvos.toLocaleString("pt-BR")} concursos (${dados.backtest.concurso_inicial} a ${dados.backtest.concurso_final}). Previsão futura: ${dados.previsao_futura.concurso_inicial} a ${dados.previsao_futura.concurso_final}.`;
  e.backtest_final.value ||= dados.backtest.concurso_final;
  mensagem("Prévia calculada sem iniciar processamento.", "sucesso");
}

async function salvarConfiguracao() {
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/configuracoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ configuracao: configuracaoFormulario() }),
  }));
  preencherConfiguracao(dados.configuracao);
  await carregarConfiguracoes();
  mensagem(`Configuração ${dados.id_configuracao_selecao} preservada.`, "sucesso");
}

function td(texto) { const celula = document.createElement("td"); celula.textContent = texto ?? "—"; return celula; }

function rotuloSituacao(situacao) {
  return ({
    PENDENTE: "Aguardando resultado",
    AVALIADO: "Avaliado",
    NAO_AVALIAVEL: "Não avaliável",
  })[situacao] || situacao;
}

function descricaoParametros(configuracao) {
  const quantidade = configuracao.modo_quantidade === "FIXA"
    ? `${configuracao.quantidade_dezenas} dezenas`
    : "máximo aprovado";
  return `k ${configuracao.fator_k}; j ${configuracao.fator_j}; ${quantidade}`;
}

function criarBotaoAlvo(item) {
  const botao = document.createElement("button"); botao.type = "button"; botao.textContent = "Formar jogos";
  botao.disabled = item.quantidade_retornada < 6;
  botao.addEventListener("click", () => selecionarAlvoJogos(item));
  return botao;
}

function renderizarDetalhes(itens, corpo) {
  corpo.replaceChildren();
  for (const item of itens) {
    const linha = document.createElement("tr");
    linha.append(td(item.numero_concurso_alvo), td(item.numero_concurso_corte), td(rotuloSituacao(item.situacao)),
      td(formatarDezenas(item.dezenas_retornadas)), td(item.quantidade_retornada),
      td(item.quantidade_combinacoes_brutas));
    const acao = td(""); acao.replaceChildren(criarBotaoAlvo(item)); linha.append(acao); corpo.append(linha);
  }
}

async function atualizarPrevisao() {
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/previsoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ configuracao: configuracaoFormulario() }),
  }));
  const nova = dados.nova_previsao;
  const detalhes = await respostaJson(await fetch(`/api/selecao-dezenas/previsoes/${nova.id_execucao_selecao}/detalhes`));
  e.resumo_previsao.textContent = `Origem até o concurso ${nova.concurso_corte}. Alvos ${nova.concurso_alvo_inicial} a ${nova.concurso_alvo_final}. ${dados.conferencia.previsoes_conferidas} previsão(ões) anterior(es) conferida(s).`;
  e.corpo_previsoes.replaceChildren();
  const parametros = descricaoParametros(configuracaoFormulario());
  for (const item of detalhes.detalhes) {
    const linha = document.createElement("tr");
    linha.append(td(item.numero_concurso_alvo), td(item.numero_concurso_corte), td(rotuloSituacao(item.situacao)),
      td(formatarDezenas(item.dezenas_retornadas)), td(item.quantidade_retornada), td(parametros));
    const acao = td(""); acao.replaceChildren(criarBotaoAlvo(item)); linha.append(acao); e.corpo_previsoes.append(linha);
  }
  mensagem("Previsão futura atualizada.", "sucesso");
}

function renderizarResumoBacktest(resumo) {
  const periodo = resumo.primeiro_avaliado == null
    ? "nenhum concurso avaliável"
    : `concursos ${resumo.primeiro_avaliado} a ${resumo.ultimo_avaliado}`;
  const tamanho = resumo.minimo_dezenas == null
    ? "sem conjunto avaliável"
    : `conjuntos de ${resumo.minimo_dezenas} a ${resumo.maximo_dezenas} dezenas`;
  e.resumo_backtest.textContent = `Execução ${resumo.id_execucao_selecao}: ${periodo}; ${resumo.avaliados.toLocaleString("pt-BR")} concursos avaliados e ${resumo.nao_avaliaveis} não avaliáveis; ${tamanho}, média de ${resumo.media_dezenas ?? "—"} dezenas e ${resumo.media_acertos_concurso ?? "—"} acertos por concurso.`;
  e.classes_backtest.replaceChildren();
  for (const item of resumo.classes || []) {
    const quadro = document.createElement("div"); quadro.className = "selecao-classe";
    quadro.innerHTML = `<span>${item.classe} acerto(s)</span><strong>${item.quantidade}</strong><span>${Number(item.percentual).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%</span>`;
    e.classes_backtest.append(quadro);
  }
}

async function carregarResultadoBacktest(idExecucao) {
  const [resumo, detalhes] = await Promise.all([
    respostaJson(await fetch(`/api/selecao-dezenas/backtests/${idExecucao}/resumo`)),
    respostaJson(await fetch(`/api/selecao-dezenas/backtests/${idExecucao}/detalhes`)),
  ]);
  renderizarResumoBacktest(resumo); renderizarDetalhes(detalhes.detalhes, e.corpo_detalhes_backtest);
  e.comparacao_ids.value = [e.comparacao_ids.value, idExecucao].filter(Boolean).join(", ");
}

function corpoBacktest() {
  const corpo = {
    configuracao: configuracaoFormulario(),
    concurso_inicial: Number(e.backtest_inicial.value),
  };
  const final = Number(e.backtest_final.value);
  if (Number.isInteger(final) && final >= 500) corpo.concurso_final = final;
  return corpo;
}

async function abrirPreviaBacktest(evento) {
  evento.preventDefault();
  if (modalBacktest.estaExecutando()) throw new Error("Já existe um backtest em andamento.");
  solicitacaoBacktest = corpoBacktest();
  const previa = await respostaJson(await fetch("/api/selecao-dezenas/previa", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitacaoBacktest),
  }));
  e.previa_backtest_resultados.textContent = `${previa.resultados.quantidade.toLocaleString("pt-BR")} concursos — ${previa.resultados.primeiro} a ${previa.resultados.ultimo}`;
  e.previa_backtest_periodo.textContent = `${previa.backtest.concurso_inicial} a ${previa.backtest.concurso_final}`;
  e.previa_backtest_quantidade.textContent = previa.backtest.quantidade_alvos.toLocaleString("pt-BR");
  e.previa_backtest_configuracao.textContent = descricaoParametros(solicitacaoBacktest.configuracao);
  e.dialogo_previa_backtest.showModal();
  mensagem("Prévia pronta. Confirme no formulário para iniciar o backtest.");
}

async function confirmarBacktest() {
  if (!solicitacaoBacktest || modalBacktest.estaExecutando()) return;
  e.dialogo_previa_backtest.close();
  e.estado_backtest.textContent = "Backtest em andamento; acompanhe o formulário de progresso.";
  const final = await modalBacktest.abrir();
  if (!final || typeof final !== "object") return;
  e.estado_backtest.textContent = `${final.etapa} — ${final.concluido}/${final.total} em ${Number(final.duracao_segundos || 0).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} s.`;
  if (final.estado === "CONCLUIDA") {
    await carregarResultadoBacktest(final.resultado.id_execucao_selecao);
    mensagem("Backtest concluído.", "sucesso");
  } else if (final.estado === "CANCELADA") {
    mensagem("Backtest cancelado com segurança.", "erro");
  }
}

async function comparar(evento) {
  evento.preventDefault();
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/backtests/comparacao", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids_execucoes: idsComparacao(e.comparacao_ids.value) }),
  }));
  const linhas = dados.pesquisas.map((item) => `Execução ${item.id_execucao_selecao}: ${item.avaliados} concursos; média ${item.media_acertos_concurso ?? "—"} acertos; custo ${Number(item.custo_combinatorio_total).toLocaleString("pt-BR")} jogos.`);
  e.resultado_comparacao.textContent = `${dados.comparavel ? "Comparação equivalente." : `Comparação com ressalvas: ${(dados.ressalvas || []).join(" ")}`} ${linhas.join(" ")}`;
}

async function selecionarAlvoJogos(item) {
  alvoJogos = item.id_alvo_selecao;
  previaJogos = await respostaJson(await fetch(`/api/selecao-dezenas/alvos/${alvoJogos}/jogos/previa`));
  e.painel_jogos.hidden = false;
  e.resumo_jogos.textContent = `Concurso ${item.numero_concurso_alvo}: ${previaJogos.quantidade_dezenas} dezenas formarão ${Number(previaJogos.quantidade_combinacoes).toLocaleString("pt-BR")} jogos de seis dezenas.${previaJogos.volume_elevado ? " Volume elevado: será exigida confirmação adicional." : ""}`;
}

async function gerarJogos() {
  if (!alvoJogos || !previaJogos) return;
  if (!window.confirm(`Deseja realmente salvar ${Number(previaJogos.quantidade_combinacoes).toLocaleString("pt-BR")} jogos?`)) return;
  let confirmarVolume = false;
  if (previaJogos.volume_elevado) confirmarVolume = window.confirm("Este é um volume elevado. Confirma novamente a gravação?");
  if (previaJogos.volume_elevado && !confirmarVolume) return;
  const dados = await respostaJson(await fetch(`/api/selecao-dezenas/alvos/${alvoJogos}/jogos`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ autorizar_persistencia: true, confirmar_volume_elevado: confirmarVolume }),
  }));
  e.resumo_jogos.textContent = `Lote ${dados.id_lote_jogos} concluído com ${Number(dados.quantidade_combinacoes).toLocaleString("pt-BR")} jogos.`;
  mensagem("Jogos gerados e vinculados à pesquisa.", "sucesso");
}

async function proteger(acao) { try { await acao(); } catch (erro) { mensagem(erro.message, "erro"); } }

e.selecao_modo_quantidade.addEventListener("change", () => { e.selecao_quantidade.disabled = e.selecao_modo_quantidade.value !== "FIXA"; if (e.selecao_quantidade.disabled) e.selecao_quantidade.value = ""; });
e.configuracao_gravada_selecao.addEventListener("change", () => { const item = configuracoes.find((config) => String(config.id_configuracao_selecao) === e.configuracao_gravada_selecao.value); if (item) preencherConfiguracao(item.configuracao); });
e.botao_previa_selecao.addEventListener("click", () => proteger(calcularPrevia));
e.botao_salvar_configuracao.addEventListener("click", () => proteger(salvarConfiguracao));
e.botao_atualizar_previsao.addEventListener("click", () => proteger(atualizarPrevisao));
e.form_backtest_selecao.addEventListener("submit", (evento) => proteger(() => abrirPreviaBacktest(evento)));
e.botao_confirmar_backtest.addEventListener("click", () => proteger(confirmarBacktest));
e.form_comparacao_selecao.addEventListener("submit", (evento) => proteger(() => comparar(evento)));
e.botao_gerar_jogos.addEventListener("click", () => proteger(gerarJogos));
e.botao_ajuda_selecao.addEventListener("click", () => e.dialogo_ajuda_selecao.showModal());

modalBacktest = criarModalAndamento({
  titulo: "Execução do backtest da seleção de dezenas",
  iniciar: async () => respostaJson(await fetch("/api/selecao-dezenas/backtests", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(solicitacaoBacktest),
  })),
  consultar: async (id) => respostaJson(await fetch(`/api/selecao-dezenas/execucoes/${id}`)),
  cancelar: async (id) => respostaJson(await fetch(`/api/selecao-dezenas/execucoes/${id}/cancelamento`, { method: "POST" })),
  apresentarResultado: (resultado) => ({
    aprovado: true,
    mensagem: `Backtest concluído. Pesquisa ${resultado.id_execucao_selecao} preservada para consulta e comparação.`,
  }),
});

proteger(carregarConfiguracoes);
