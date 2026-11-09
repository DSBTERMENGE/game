import { formatarDezenas, idsComparacao, montarConfiguracao } from "./selecao-dezenas-controles.js";
import { criarModalAndamento } from "./modal-andamento.js";

const e = Object.fromEntries([
  "mensagem-selecao", "configuracao-gravada-selecao", "selecao-nome", "selecao-fator-k",
  "selecao-fator-j", "selecao-modo-quantidade", "selecao-quantidade",
  "selecao-versao", "estado-edicao-configuracao", "botao-previa-selecao", "botao-salvar-configuracao",
  "resultado-previa-selecao", "botao-atualizar-previsao", "resumo-previsao", "corpo-previsoes",
  "form-backtest-selecao", "backtest-inicial", "backtest-final",
  "estado-backtest", "resumo-backtest", "classes-backtest",
  "form-comparacao-selecao", "comparacao-ids", "resultado-comparacao",
  "corpo-detalhes-backtest", "painel-jogos", "resumo-jogos", "botao-gerar-jogos",
  "botao-ajuda-selecao", "dialogo-ajuda-selecao",
  "dialogo-confirmar-registro", "registro-configuracao", "registro-concurso",
  "registro-corte", "registro-quantidade", "registro-dezenas", "registro-combinacoes",
  "botao-cancelar-registro", "botao-confirmar-registro",
  "dialogo-previa-backtest", "previa-backtest-resultados", "previa-backtest-periodo",
  "previa-backtest-quantidade", "previa-backtest-configuracao", "botao-confirmar-backtest",
].map((id) => [id.replaceAll("-", "_"), document.getElementById(id)]));

let configuracoes = [];
let alvoJogos = null;
let previaJogos = null;
let solicitacaoBacktest = null;
let solicitacaoRegistro = null;
let modalBacktest = null;

async function respostaJson(resposta) {
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    const codigo = dados.erro?.codigo;
    const mensagens = {
      ASSINATURA_DIVERGENTE: "Não foi possível salvar porque os dados internos ficaram inconsistentes. Nenhuma configuração foi gravada.",
      FALHA_CONFIGURACAO: "Não foi possível salvar a configuração. Nenhuma configuração foi gravada.",
      CONFIGURACAO_INVALIDA: "Não foi possível usar a configuração. Confira os campos preenchidos.",
      CONFIGURACAO_NAO_ENCONTRADA: "A configuração salva não está mais disponível. Selecione outra configuração.",
    };
    throw new Error(mensagens[codigo] || dados.erro?.mensagem || "Não foi possível concluir a operação. Tente novamente.");
  }
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
    versao_calculo: e.selecao_versao.value,
  });
}

function definirEdicaoConfiguracao(editavel) {
  for (const campo of [
    e.selecao_nome, e.selecao_fator_k, e.selecao_fator_j,
    e.selecao_modo_quantidade, e.selecao_versao,
  ]) campo.disabled = !editavel;
  e.selecao_quantidade.disabled = !editavel || e.selecao_modo_quantidade.value !== "FIXA";
  e.botao_salvar_configuracao.disabled = !editavel;
  e.botao_atualizar_previsao.disabled = editavel;
  e.botao_atualizar_previsao.title = editavel
    ? "Salve a configuração antes de registrar uma seleção."
    : "Registrar a seleção produzida pela configuração salva.";
  e.estado_edicao_configuracao.textContent = editavel
    ? "Nova configuração: preencha e salve os campos antes de registrar uma seleção."
    : "Configuração salva: os campos estão protegidos contra alterações e a seleção pode ser registrada.";
}

function preencherConfiguracao(configuracao, editavel = false) {
  e.selecao_nome.value = configuracao.nome;
  e.selecao_fator_k.value = configuracao.fator_k;
  e.selecao_fator_j.value = configuracao.fator_j;
  e.selecao_modo_quantidade.value = configuracao.modo_quantidade;
  e.selecao_quantidade.value = configuracao.quantidade_dezenas ?? "";
  e.selecao_versao.value = configuracao.versao_calculo;
  definirEdicaoConfiguracao(editavel);
}

function iniciarNovaConfiguracao() {
  preencherConfiguracao({
    nome: "Seleção inicial", fator_k: "1.000000", fator_j: "0.000000",
    modo_quantidade: "MAX", quantidade_dezenas: null, versao_calculo: 1,
  }, true);
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
    mensagem(`${configuracoes.length} configuração(ões) salva(s). A selecionada está disponível somente para leitura.`, "sucesso");
  } else {
    iniciarNovaConfiguracao();
    mensagem("Ainda não há configurações salvas. Preencha uma nova configuração para começar.");
  }
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
  const analise = dados.analise_configuracao;
  e.resultado_previa_selecao.hidden = false;
  e.resultado_previa_selecao.textContent = analise
    ? `Dados analíticos da configuração: último concurso cadastrado ${analise.concurso_corte}; concurso-alvo ${analise.concurso_alvo}; ${analise.quantidade_aprovada.toLocaleString("pt-BR")} dezenas aprovadas; ${analise.quantidade_retornada.toLocaleString("pt-BR")} dezenas retornadas (${formatarDezenas(analise.dezenas_retornadas)}); ${Number(analise.quantidade_combinacoes).toLocaleString("pt-BR")} combinações de seis. Esta análise é momentânea e não foi armazenada.`
    : "Dados analíticos da configuração indisponíveis: não existem resultados cadastrados.";
  if (analise) e.botao_atualizar_previsao.textContent = `Registrar previsão do concurso ${analise.concurso_alvo}`;
  e.backtest_final.value ||= dados.backtest.concurso_final;
  mensagem("Configuração analisada sem salvar dados nem iniciar o backtest.", "sucesso");
}

async function salvarConfiguracao() {
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/configuracoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ configuracao: configuracaoFormulario() }),
  }));
  preencherConfiguracao(dados.configuracao);
  await carregarConfiguracoes();
  mensagem("Configuração salva com sucesso. Os campos foram protegidos contra alterações.", "sucesso");
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

async function abrirConfirmacaoRegistro() {
  const idConfiguracao = Number(e.configuracao_gravada_selecao.value);
  if (!Number.isInteger(idConfiguracao) || idConfiguracao <= 0) {
    throw new Error("Salve a configuração antes de registrar uma seleção.");
  }
  const configuracao = configuracaoFormulario();
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/previa", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ configuracao }),
  }));
  const analise = dados.analise_configuracao;
  if (!analise) throw new Error("Não existem resultados cadastrados para calcular a seleção.");
  solicitacaoRegistro = { idConfiguracao, configuracao };
  e.registro_configuracao.textContent = configuracao.nome;
  e.registro_concurso.textContent = analise.concurso_alvo;
  e.registro_corte.textContent = analise.concurso_corte;
  e.registro_quantidade.textContent = analise.quantidade_retornada.toLocaleString("pt-BR");
  e.registro_dezenas.textContent = formatarDezenas(analise.dezenas_retornadas) || "Nenhuma dezena";
  e.registro_combinacoes.textContent = Number(analise.quantidade_combinacoes).toLocaleString("pt-BR");
  e.dialogo_confirmar_registro.showModal();
  mensagem("Confira a seleção. Nenhum dado foi gravado.");
}

async function confirmarRegistro() {
  if (!solicitacaoRegistro) return;
  const { idConfiguracao, configuracao } = solicitacaoRegistro;
  solicitacaoRegistro = null;
  e.dialogo_confirmar_registro.close("confirmado");
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/previsoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_configuracao_selecao: idConfiguracao }),
  }));
  const nova = dados.nova_previsao;
  const detalhes = await respostaJson(await fetch(`/api/selecao-dezenas/previsoes/${nova.id_execucao_selecao}/detalhes`));
  const registro = nova.alvos_criados_agora > 0
    ? `Previsão registrada para o concurso ${nova.concurso_alvo_inicial}, usando somente resultados até o concurso ${nova.concurso_corte}. A lista ficará preservada até a importação do resultado.`
    : `A previsão do concurso ${nova.concurso_alvo_inicial} já estava registrada. A lista original foi mantida sem alterações.`;
  const conferencia = dados.conferencia.previsoes_conferidas > 0
    ? ` ${dados.conferencia.previsoes_conferidas} previsão(ões) anterior(es) também foi(foram) conferida(s).`
    : "";
  e.resumo_previsao.textContent = `${registro}${conferencia}`;
  e.corpo_previsoes.replaceChildren();
  const parametros = descricaoParametros(configuracao);
  for (const item of detalhes.detalhes) {
    const linha = document.createElement("tr");
    linha.append(td(item.numero_concurso_alvo), td(item.numero_concurso_corte), td(rotuloSituacao(item.situacao)),
      td(formatarDezenas(item.dezenas_retornadas)), td(item.quantidade_retornada), td(parametros));
    const acao = td(""); acao.replaceChildren(criarBotaoAlvo(item)); linha.append(acao); e.corpo_previsoes.append(linha);
  }
  mensagem(nova.alvos_criados_agora > 0
    ? `Seleção registrada para o concurso ${nova.concurso_alvo_inicial} com ${detalhes.detalhes[0]?.quantidade_retornada ?? 0} dezenas. Nenhum backtest, combinação ou jogo foi criado.`
    : `A seleção do concurso ${nova.concurso_alvo_inicial} já estava registrada para esta configuração. Nenhum dado foi alterado ou duplicado.`, "sucesso");
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
e.configuracao_gravada_selecao.addEventListener("change", () => {
  const item = configuracoes.find((config) => String(config.id_configuracao_selecao) === e.configuracao_gravada_selecao.value);
  if (item) {
    preencherConfiguracao(item.configuracao);
    mensagem("Configuração salva carregada somente para leitura.");
  } else {
    iniciarNovaConfiguracao();
    mensagem("Nova configuração iniciada. Nenhum dado foi gravado.");
  }
});
e.botao_previa_selecao.addEventListener("click", () => proteger(calcularPrevia));
e.botao_salvar_configuracao.addEventListener("click", () => proteger(salvarConfiguracao));
e.botao_atualizar_previsao.addEventListener("click", () => proteger(abrirConfirmacaoRegistro));
e.botao_confirmar_registro.addEventListener("click", () => proteger(confirmarRegistro));
e.dialogo_confirmar_registro.addEventListener("close", () => {
  if (e.dialogo_confirmar_registro.returnValue === "confirmado") return;
  solicitacaoRegistro = null;
  mensagem("Operação cancelada. Nenhum dado foi gravado.");
});
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
