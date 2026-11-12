import { formatarDezenas, montarConfiguracao } from "./selecao-dezenas-controles.js";
import { criarModalAndamento } from "./modal-andamento.js";
import { renderizarGraficosBacktest } from "./selecao-dezenas-graficos.js";
import { criarFluxoCadastroConfirmado } from "./fluxo-cadastro-confirmado.js";

const e = Object.fromEntries([
  "mensagem-selecao", "configuracao-gravada-selecao", "selecao-nome", "selecao-fator-k",
  "selecao-fator-j", "selecao-modo-quantidade", "selecao-quantidade",
  "selecao-versao", "estado-edicao-configuracao", "botao-previa-selecao", "botao-salvar-configuracao",
  "resultado-previa-selecao", "botao-atualizar-previsao", "resumo-previsao", "corpo-previsoes",
  "backtest-configuracao", "backtest-inicial", "estado-backtest",
  "painel-jogos", "jogos-origem-concurso", "jogos-origem-configuracao",
  "jogos-origem-dezenas", "jogos-origem-combinacoes", "jogos-quantidade-solicitada",
  "jogos-valor-unitario", "jogos-valor-previsto", "estado-configuracao-jogos",
  "botao-conferir-jogos", "dialogo-previa-jogos", "previa-jogos-concurso",
  "previa-jogos-configuracao", "previa-jogos-dezenas", "previa-jogos-combinacoes",
  "previa-jogos-quantidade", "previa-jogos-valor-unitario",
  "previa-jogos-valor-previsto", "botao-iniciar-screener-jogos",
  "dialogo-confirmar-registro", "registro-configuracao", "registro-concurso",
  "registro-corte", "registro-quantidade", "registro-dezenas", "registro-combinacoes",
  "botao-cancelar-registro", "botao-confirmar-registro",
  "dialogo-confirmar-configuracao", "configuracao-confirmar-nome",
  "configuracao-confirmar-k", "configuracao-confirmar-j", "configuracao-confirmar-modo",
  "configuracao-confirmar-quantidade", "configuracao-confirmar-versao",
  "botao-confirmar-configuracao",
  "botao-gerar-backtest", "relatorio-backtest",
  "periodo-backtest", "resumo-backtest",
  "classes-backtest", "grafico-backtest-quantidade", "grafico-backtest-acertos",
  "botao-fechar-backtest", "dialogo-previa-backtest",
  "previa-backtest-configuracao", "previa-backtest-resultados",
  "previa-backtest-periodo", "previa-backtest-quantidade",
  "botao-confirmar-backtest",
].map((id) => [id.replaceAll("-", "_"), document.getElementById(id)]));

let configuracoes = [];
let alvoJogos = null;
let previaJogos = null;
let solicitacaoRegistro = null;
let modalBacktest = null;
let solicitacaoBacktest = null;
let idBacktest = null;
let contextoBacktest = null;

async function respostaJson(resposta) {
  const dados = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    const codigo = dados.erro?.codigo;
    const mensagens = {
      ASSINATURA_DIVERGENTE: "Não foi possível salvar porque os dados internos ficaram inconsistentes. Nenhuma configuração foi gravada.",
      FALHA_CONFIGURACAO: "Não foi possível salvar a configuração. Nenhuma configuração foi gravada.",
      CONFIGURACAO_INVALIDA: "Não foi possível usar a configuração. Confira os campos preenchidos.",
      CONFIGURACAO_NAO_ENCONTRADA: "A configuração salva não está mais disponível. Selecione outra configuração.",
      NOME_CONFIGURACAO_EXISTENTE: "Já existe uma configuração salva com esse nome. Escolha outro nome.",
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
  e.botao_gerar_backtest.title = "Calcular com a configuração escolhida no bloco Backtest.";
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
  e.backtest_configuracao.replaceChildren(new Option("Selecione uma configuração", ""));
  for (const item of configuracoes) {
    const rotulo = item.configuracao.nome;
    e.configuracao_gravada_selecao.append(new Option(rotulo, item.id_configuracao_selecao));
    e.backtest_configuracao.append(new Option(rotulo, item.id_configuracao_selecao));
  }
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
  if (Number.isInteger(inicio)) corpo.concurso_inicial = inicio;
  const dados = await respostaJson(await fetch("/api/selecao-dezenas/previa", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo),
  }));
  const analise = dados.analise_configuracao;
  e.resultado_previa_selecao.hidden = false;
  e.resultado_previa_selecao.textContent = analise
    ? `Dados analíticos da configuração: último concurso cadastrado ${analise.concurso_corte}; concurso-alvo ${analise.concurso_alvo}; ${analise.quantidade_aprovada.toLocaleString("pt-BR")} dezenas aprovadas; ${analise.quantidade_retornada.toLocaleString("pt-BR")} dezenas retornadas (${formatarDezenas(analise.dezenas_retornadas)}); ${Number(analise.quantidade_combinacoes).toLocaleString("pt-BR")} combinações de seis. Esta análise é momentânea e não foi armazenada.`
    : "Dados analíticos da configuração indisponíveis: não existem resultados cadastrados.";
  if (analise) e.botao_atualizar_previsao.textContent = `Registrar previsão do concurso ${analise.concurso_alvo}`;
  mensagem("Configuração analisada sem salvar dados nem iniciar o backtest.", "sucesso");
}

function nomeNormalizado(nome) {
  return nome.trim().toLocaleLowerCase("pt-BR");
}

function abrirConfirmacaoConfiguracao() {
  const configuracao = configuracaoFormulario();
  if (configuracoes.some((item) => nomeNormalizado(item.configuracao.nome) === nomeNormalizado(configuracao.nome))) {
    throw new Error("Já existe uma configuração salva com esse nome. Escolha outro nome.");
  }
  fluxoConfiguracao.preparar(configuracao);
  e.configuracao_confirmar_nome.textContent = configuracao.nome;
  e.configuracao_confirmar_k.textContent = configuracao.fator_k;
  e.configuracao_confirmar_j.textContent = configuracao.fator_j;
  e.configuracao_confirmar_modo.textContent = configuracao.modo_quantidade;
  e.configuracao_confirmar_quantidade.textContent = configuracao.modo_quantidade === "FIXA"
    ? configuracao.quantidade_dezenas : "Máxima aprovada";
  e.configuracao_confirmar_versao.textContent = configuracao.versao_calculo;
  e.dialogo_confirmar_configuracao.showModal();
  mensagem("Confira os parâmetros. Nenhuma configuração foi criada.");
}

async function confirmarSalvarConfiguracao() {
  e.dialogo_confirmar_configuracao.close("confirmado");
  const dados = await fluxoConfiguracao.confirmar();
  if (!dados) return;
  preencherConfiguracao(dados.configuracao);
  await carregarConfiguracoes();
  mensagem("Configuração salva com sucesso. Os campos foram protegidos contra alterações.", "sucesso");
}

const fluxoConfiguracao = criarFluxoCadastroConfirmado({
  validar: (configuracao) => montarConfiguracao(configuracao),
  gravar: async (configuracao) => respostaJson(await fetch("/api/selecao-dezenas/configuracoes", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ configuracao }),
  })),
});

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

function configuracaoEstudoSelecionada() {
  const identificador = Number(e.backtest_configuracao.value);
  const item = configuracoes.find(
    (configuracao) => configuracao.id_configuracao_selecao === identificador,
  );
  if (!item) throw new Error("Selecione uma configuração salva no bloco Backtest.");
  return item;
}

function descricaoConfiguracaoEstudo(item) {
  const config = item.configuracao;
  const modo = config.modo_quantidade === "FIXA"
    ? `FIXA (${config.quantidade_dezenas} dezenas)` : "MAX";
  return `${config.nome}; k=${config.fator_k}; j=${config.fator_j}; modo ${modo}; versão ${config.versao_calculo}`;
}

function corpoBacktest() {
  const item = configuracaoEstudoSelecionada();
  const inicio = Number(e.backtest_inicial.value);
  if (!Number.isInteger(inicio) || inicio < 500) {
    throw new Error("Informe um concurso inicial igual ou superior a 500.");
  }
  return {
    id_configuracao_selecao: item.id_configuracao_selecao,
    concurso_inicial: inicio,
    itemConfiguracao: item,
  };
}

async function abrirPreviaBacktest() {
  if (modalBacktest.estaExecutando()) {
    throw new Error("Já existe um relatório gráfico em andamento.");
  }
  e.estado_backtest.textContent = "Consultando o período disponível…";
  const estudo = corpoBacktest();
  solicitacaoBacktest = {
    id_configuracao_selecao: estudo.id_configuracao_selecao,
    concurso_inicial: estudo.concurso_inicial,
  };
  const previa = await respostaJson(await fetch(
    "/api/selecao-dezenas/backtests/previa",
    {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(solicitacaoBacktest),
    },
  ));
  contextoBacktest = {
    item: estudo.itemConfiguracao,
    periodo: previa.periodo,
  };
  e.previa_backtest_configuracao.textContent = previa.configuracao.nome;
  e.previa_backtest_resultados.textContent = `${previa.resultados.quantidade.toLocaleString("pt-BR")} concursos — ${previa.resultados.primeiro} a ${previa.resultados.ultimo}`;
  e.previa_backtest_periodo.textContent = `${previa.periodo.concurso_inicial} a ${previa.periodo.concurso_final}`;
  e.previa_backtest_quantidade.textContent = previa.periodo.quantidade_concursos.toLocaleString("pt-BR");
  e.dialogo_previa_backtest.showModal();
  e.estado_backtest.textContent = `Conferência pronta: concursos ${previa.periodo.concurso_inicial} a ${previa.periodo.concurso_final}. Confirme para calcular.`;
  mensagem("Dados do Backtest prontos para conferência.");
}

function metricaResumo(rotulo, valor) {
  const item = document.createElement("div");
  item.className = "backtest-relatorio__metrica";
  const titulo = document.createElement("span"); titulo.textContent = rotulo;
  const numeroMetrica = document.createElement("strong"); numeroMetrica.textContent = valor;
  item.append(titulo, numeroMetrica);
  return item;
}

function renderizarRelatorioBacktest(relatorio) {
  const resumo = relatorio.resumo;
  const identificacao = descricaoConfiguracaoEstudo(contextoBacktest.item);
  e.relatorio_backtest.hidden = false;
  e.periodo_backtest.textContent = `${identificacao}; concursos ${relatorio.concurso_inicial} a ${relatorio.concurso_final}; cálculo concluído em ${Number(relatorio.duracao_segundos).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} s.`;
  e.resumo_backtest.replaceChildren(
    metricaResumo("Testes efetuados", resumo.testes_efetuados.toLocaleString("pt-BR")),
    metricaResumo("Mínimo de dezenas", resumo.minimo_dezenas.toLocaleString("pt-BR")),
    metricaResumo("Máximo de dezenas", resumo.maximo_dezenas.toLocaleString("pt-BR")),
    metricaResumo("Média de dezenas", Number(resumo.media_dezenas).toLocaleString("pt-BR", { maximumFractionDigits: 2 })),
    metricaResumo("Média de acertos", Number(resumo.media_acertos).toLocaleString("pt-BR", { maximumFractionDigits: 2 })),
    metricaResumo("Concursos com 4 a 6", `${resumo.concursos_premiados.toLocaleString("pt-BR")} (${Number(resumo.percentual_premiados).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%)`),
  );
  e.classes_backtest.replaceChildren();
  for (const item of resumo.classes) {
    const quadro = document.createElement("div");
    quadro.className = `selecao-classe ${item.classe >= 4 ? "selecao-classe--premiada" : "selecao-classe--sem-premio"}`;
    const rotulo = document.createElement("span"); rotulo.textContent = `${item.classe} acerto(s)`;
    const quantidade = document.createElement("strong"); quantidade.textContent = item.quantidade.toLocaleString("pt-BR");
    const percentual = document.createElement("span"); percentual.textContent = `${Number(item.percentual).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}%`;
    quadro.append(rotulo, quantidade, percentual);
    e.classes_backtest.append(quadro);
  }
  renderizarGraficosBacktest(
    e.grafico_backtest_quantidade, e.grafico_backtest_acertos, relatorio.pontos,
  );
  e.relatorio_backtest.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function confirmarBacktest() {
  if (!solicitacaoBacktest || modalBacktest.estaExecutando()) return;
  e.dialogo_previa_backtest.close("confirmado");
  e.estado_backtest.textContent = "Calculando o Backtest…";
  const final = await modalBacktest.abrir();
  if (!final || typeof final !== "object") return;
  if (final.estado === "CONCLUIDA" && final.resultado) {
    idBacktest = final.id;
    renderizarRelatorioBacktest(final.resultado);
    e.estado_backtest.textContent = "Relatório concluído e exibido abaixo.";
    mensagem("Relatório gráfico concluído.", "sucesso");
  } else if (final.estado === "CANCELADA") {
    e.estado_backtest.textContent = "Cálculo cancelado.";
    mensagem("Cálculo do Backtest cancelado.", "erro");
  }
}

async function descartarBacktest() {
  if (idBacktest) {
    await respostaJson(await fetch(
      `/api/selecao-dezenas/backtests/${idBacktest}`,
      { method: "DELETE" },
    ));
  }
  idBacktest = null;
  contextoBacktest = null;
  e.relatorio_backtest.hidden = true;
  e.resumo_backtest.replaceChildren();
  e.classes_backtest.replaceChildren();
  e.grafico_backtest_quantidade.replaceChildren();
  e.grafico_backtest_acertos.replaceChildren();
  e.estado_backtest.textContent = "Escolha uma configuração salva e o concurso inicial. O estudo seguirá automaticamente até o último concurso cadastrado.";
  mensagem("Relatório fechado. Nenhum dado foi apagado do banco.");
}

async function selecionarAlvoJogos(item) {
  alvoJogos = item.id_alvo_selecao;
  previaJogos = await respostaJson(await fetch(`/api/selecao-dezenas/alvos/${alvoJogos}/jogos/previa`));
  e.painel_jogos.hidden = false;
  previaJogos.configuracao_nome = configuracaoFormulario().nome;
  previaJogos.concurso = item.numero_concurso_alvo;
  e.jogos_origem_concurso.textContent = item.numero_concurso_alvo;
  e.jogos_origem_configuracao.textContent = previaJogos.configuracao_nome;
  e.jogos_origem_dezenas.textContent = formatarDezenas(previaJogos.dezenas);
  e.jogos_origem_combinacoes.textContent = Number(previaJogos.quantidade_combinacoes).toLocaleString("pt-BR");
  e.jogos_quantidade_solicitada.value = "";
  e.jogos_valor_unitario.value = "";
  e.jogos_valor_previsto.textContent = "—";
  e.estado_configuracao_jogos.textContent = "Informe a quantidade máxima e o valor unitário. Nenhuma combinação será processada ou gravada.";
  e.painel_jogos.scrollIntoView({ behavior: "smooth", block: "center" });
}

function centavosValorJogo(texto) {
  const normalizado = texto.trim();
  if (!/^\d+(?:[.,]\d{1,2})?$/.test(normalizado)) {
    throw new Error("Informe o valor de um jogo com até duas casas decimais, por exemplo 5,00.");
  }
  const [inteiros, decimais = ""] = normalizado.replace(",", ".").split(".");
  const centavos = BigInt(inteiros) * 100n + BigInt(decimais.padEnd(2, "0"));
  if (centavos <= 0n) throw new Error("O valor de um jogo deve ser maior que zero.");
  return centavos;
}

function formatarMoeda(centavos) {
  const reais = centavos / 100n;
  const fracao = String(centavos % 100n).padStart(2, "0");
  return `R$ ${reais.toLocaleString("pt-BR")},${fracao}`;
}

function configuracaoFormacaoJogos() {
  if (!alvoJogos || !previaJogos) throw new Error("Escolha primeiro um registro de dezenas em Formar jogos.");
  const quantidade = Number(e.jogos_quantidade_solicitada.value);
  if (!Number.isSafeInteger(quantidade) || quantidade < 1 || quantidade > 50_063_860) {
    throw new Error("Informe um número máximo de jogos entre 1 e 50.063.860.");
  }
  const valorUnitarioCentavos = centavosValorJogo(e.jogos_valor_unitario.value);
  return {
    quantidade,
    valorUnitarioCentavos,
    valorPrevistoCentavos: BigInt(quantidade) * valorUnitarioCentavos,
  };
}

function atualizarValorPrevisto() {
  try {
    const configuracao = configuracaoFormacaoJogos();
    e.jogos_valor_previsto.textContent = formatarMoeda(configuracao.valorPrevistoCentavos);
    e.estado_configuracao_jogos.textContent = "Valores preenchidos. Use Conferir configuração para revisar; nenhum processamento será iniciado.";
  } catch (_erro) {
    e.jogos_valor_previsto.textContent = "—";
  }
}

function conferirFormacaoJogos() {
  const configuracao = configuracaoFormacaoJogos();
  e.jogos_valor_previsto.textContent = formatarMoeda(configuracao.valorPrevistoCentavos);
  e.previa_jogos_concurso.textContent = previaJogos.concurso;
  e.previa_jogos_configuracao.textContent = previaJogos.configuracao_nome;
  e.previa_jogos_dezenas.textContent = formatarDezenas(previaJogos.dezenas);
  e.previa_jogos_combinacoes.textContent = Number(previaJogos.quantidade_combinacoes).toLocaleString("pt-BR");
  e.previa_jogos_quantidade.textContent = configuracao.quantidade.toLocaleString("pt-BR");
  e.previa_jogos_valor_unitario.textContent = formatarMoeda(configuracao.valorUnitarioCentavos);
  e.previa_jogos_valor_previsto.textContent = formatarMoeda(configuracao.valorPrevistoCentavos);
  e.dialogo_previa_jogos.showModal();
  e.estado_configuracao_jogos.textContent = "Configuração conferida. A execução do Screener será disponibilizada em uma etapa posterior.";
  mensagem("Configuração dos jogos conferida sem processar combinações nem gravar dados.", "sucesso");
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
e.botao_salvar_configuracao.addEventListener("click", () => proteger(abrirConfirmacaoConfiguracao));
e.botao_confirmar_configuracao.addEventListener("click", () => proteger(confirmarSalvarConfiguracao));
e.dialogo_confirmar_configuracao.addEventListener("close", () => {
  if (e.dialogo_confirmar_configuracao.returnValue === "confirmado") return;
  fluxoConfiguracao.cancelar();
  mensagem("Salvamento cancelado. Nenhuma configuração foi criada.");
});
e.botao_atualizar_previsao.addEventListener("click", () => proteger(abrirConfirmacaoRegistro));
e.botao_confirmar_registro.addEventListener("click", () => proteger(confirmarRegistro));
e.dialogo_confirmar_registro.addEventListener("close", () => {
  if (e.dialogo_confirmar_registro.returnValue === "confirmado") return;
  solicitacaoRegistro = null;
  mensagem("Operação cancelada. Nenhum dado foi gravado.");
});
e.botao_gerar_backtest.addEventListener("click", async () => {
  try {
    await abrirPreviaBacktest();
  } catch (erro) {
    e.estado_backtest.textContent = `Não foi possível preparar o relatório: ${erro.message}`;
    mensagem(erro.message, "erro");
  }
});
e.botao_confirmar_backtest.addEventListener("click", () => proteger(confirmarBacktest));
e.botao_fechar_backtest.addEventListener("click", () => proteger(descartarBacktest));
e.jogos_quantidade_solicitada.addEventListener("input", atualizarValorPrevisto);
e.jogos_valor_unitario.addEventListener("input", atualizarValorPrevisto);
e.botao_conferir_jogos.addEventListener("click", () => proteger(conferirFormacaoJogos));

modalBacktest = criarModalAndamento({
  titulo: "Cálculo do Backtest",
  descricao: () => {
    if (!contextoBacktest) return "Preparando o cálculo do Backtest.";
    const periodo = contextoBacktest.periodo;
    return `${descricaoConfiguracaoEstudo(contextoBacktest.item)}; concursos ${periodo.concurso_inicial} a ${periodo.concurso_final}; ${periodo.quantidade_concursos.toLocaleString("pt-BR")} concursos.`;
  },
  iniciar: async () => respostaJson(await fetch(
    "/api/selecao-dezenas/backtests",
    {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(solicitacaoBacktest),
    },
  )),
  consultar: async (id) => respostaJson(await fetch(
    `/api/selecao-dezenas/backtests/${id}`,
  )),
  cancelar: async (id) => respostaJson(await fetch(
    `/api/selecao-dezenas/backtests/${id}/cancelamento`,
    { method: "POST" },
  )),
  apresentarResultado: (resultado) => ({
    aprovado: true,
        mensagem: `${resultado.resumo.testes_efetuados.toLocaleString("pt-BR")} concursos calculados. Relatório pronto.`,
  }),
});

window.addEventListener("pagehide", () => {
  if (!idBacktest) return;
  fetch(`/api/selecao-dezenas/backtests/${idBacktest}`, {
    method: "DELETE", keepalive: true,
  }).catch(() => {});
});

proteger(carregarConfiguracoes);
