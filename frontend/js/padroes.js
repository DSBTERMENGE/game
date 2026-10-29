const API_PADROES = "/api/padroes";
const API_GRUPOS = "/api/grupos-padroes";
const API_PERFIL = "/api/grupos-padroes/PG_001/perfil";

const formulario = document.querySelector("#form-novo-padrao");
const grupoNovo = document.querySelector("#novo-padrao-grupo");
const nomeNovo = document.querySelector("#novo-padrao-nome");
const descricaoNova = document.querySelector("#novo-padrao-descr");
const filtroGrupo = document.querySelector("#filtro-grupo");
const corpoTabela = document.querySelector("#corpo-tabela-padroes");
const mensagem = document.querySelector("#mensagem-padroes");
const botaoAdicionar = document.querySelector("#botao-adicionar-padrao");
const detalhesPerfil = document.querySelector("#perfil-padroes");
const formularioPerfil = document.querySelector("#form-perfil");
const limitePerfil = document.querySelector("#perfil-limite");
const tipoCortePerfil = document.querySelector("#perfil-tipo-corte");
const campoNumeroPerfil = document.querySelector("#perfil-campo-numero");
const numeroPerfil = document.querySelector("#perfil-numero");
const campoDataPerfil = document.querySelector("#perfil-campo-data");
const dataPerfil = document.querySelector("#perfil-data");
const resumoPerfil = document.querySelector("#resumo-perfil");
const mensagemPerfil = document.querySelector("#mensagem-perfil");
const indicadoresPerfil = document.querySelector("#perfil-indicadores");
const corpoPerfil = document.querySelector("#corpo-tabela-perfil");
const estado = { grupos: [], padroes: [], ocupado: false, perfilCarregado: false };

function informar(texto, tipo = "informacao") {
  mensagem.textContent = texto;
  mensagem.dataset.tipo = tipo;
}

async function requisitar(url, opcoes = {}) {
  const resposta = await fetch(url, {
    headers: { Accept: "application/json", ...(opcoes.headers ?? {}) },
    ...opcoes,
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) throw new Error(corpo.erro?.mensagem ?? `A API respondeu com status ${resposta.status}.`);
  return corpo;
}

function definirOcupado(ocupado) {
  estado.ocupado = ocupado;
  botaoAdicionar.disabled = ocupado || estado.grupos.length === 0;
}

function preencherSelecao(selecao, incluirTodos = false) {
  const valorAtual = selecao.value;
  const opcoes = estado.grupos.map(
    (grupo) => new Option(`${grupo.grupo_cod} — ${grupo.grupo_nome}`, grupo.grupo_cod),
  );
  if (incluirTodos) opcoes.unshift(new Option("Todos", ""));
  selecao.replaceChildren(...opcoes);
  if ([...selecao.options].some((opcao) => opcao.value === valorAtual)) selecao.value = valorAtual;
}

function criarCampo(tag, valor, rotulo, limite = 4000) {
  const campo = document.createElement(tag);
  campo.value = valor;
  campo.setAttribute("aria-label", rotulo);
  campo.maxLength = limite;
  if (tag === "textarea") campo.rows = 3;
  return campo;
}

function criarSelecaoGrupo(valor, rotulo) {
  const selecao = document.createElement("select");
  selecao.setAttribute("aria-label", rotulo);
  selecao.append(...estado.grupos.map(
    (grupo) => new Option(`${grupo.grupo_cod} — ${grupo.grupo_nome}`, grupo.grupo_cod),
  ));
  selecao.value = valor;
  const atualizarTitulo = () => {
    selecao.title = selecao.options[selecao.selectedIndex]?.text ?? "";
  };
  selecao.addEventListener("change", atualizarTitulo);
  atualizarTitulo();
  return selecao;
}

function criarCelula(texto, classe = "") {
  const celula = document.createElement("td");
  celula.textContent = texto;
  celula.className = classe;
  return celula;
}

function criarBotao(texto, acao, codigo) {
  const botao = document.createElement("button");
  botao.type = "button";
  botao.textContent = texto;
  botao.dataset.acao = acao;
  botao.dataset.codigo = codigo;
  return botao;
}

function formatarCalculado(valor) {
  return valor === null || valor === undefined ? "—" : String(valor).replace(".", ",");
}

function formatarNumero(valor) {
  return Number(valor).toLocaleString("pt-BR");
}

function informarPerfil(texto, tipo = "informacao") {
  mensagemPerfil.textContent = texto;
  mensagemPerfil.dataset.tipo = tipo;
}

function criarCelulaPerfil(texto) {
  const celula = document.createElement("td");
  celula.textContent = texto;
  return celula;
}

function renderizarPerfil(perfil) {
  const raros = perfil.raridade.padroes_indicados;
  resumoPerfil.textContent = `${formatarNumero(perfil.amostra.total_resultados)} resultados`;
  indicadoresPerfil.replaceChildren();
  const textos = [
    ["Amostra", formatarNumero(perfil.amostra.total_resultados)],
    ["Classificados", formatarNumero(perfil.amostra.total_classificados)],
    ["Limite", `${formatarCalculado(perfil.raridade.limite_percentual)}%`],
    ["Indicados", raros.length ? raros.join(", ") : "nenhum"],
  ];
  for (const [rotulo, valor] of textos) {
    const item = document.createElement("span");
    const titulo = document.createElement("strong");
    titulo.textContent = `${rotulo}: `;
    item.append(titulo, document.createTextNode(valor));
    indicadoresPerfil.append(item);
  }
  corpoPerfil.replaceChildren(...perfil.classes.map((classe) => {
    const linha = document.createElement("tr");
    linha.dataset.raro = String(classe.raro);
    linha.append(
      criarCelulaPerfil(classe.padrao_cod),
      criarCelulaPerfil(formatarNumero(classe.quantidade)),
      criarCelulaPerfil(`${formatarCalculado(classe.percentual_total)}%`),
      criarCelulaPerfil(classe.percentual_classificados === null ? "—" : `${formatarCalculado(classe.percentual_classificados)}%`),
      criarCelulaPerfil(formatarCalculado(classe.intervalo_medio)),
      criarCelulaPerfil(formatarCalculado(classe.desvio_padrao)),
      criarCelulaPerfil(classe.raro ? "Abaixo do limite" : "Preservado"),
    );
    return linha;
  }));
}

function atualizarCamposCorte() {
  campoNumeroPerfil.hidden = tipoCortePerfil.value !== "numero";
  campoDataPerfil.hidden = tipoCortePerfil.value !== "data";
  numeroPerfil.required = tipoCortePerfil.value === "numero";
  dataPerfil.required = tipoCortePerfil.value === "data";
}

async function carregarPerfil(evento) {
  evento?.preventDefault();
  const parametros = new URLSearchParams({ limite_raridade: limitePerfil.value });
  if (tipoCortePerfil.value === "numero") parametros.set("numero_ap_ate", numeroPerfil.value);
  if (tipoCortePerfil.value === "data") parametros.set("data_ate", dataPerfil.value);
  informarPerfil("Consultando perfil...");
  try {
    const corpo = await requisitar(`${API_PERFIL}?${parametros}`);
    renderizarPerfil(corpo.perfil);
    estado.perfilCarregado = true;
    informarPerfil("Diagnóstico informativo; screener inativo.", "sucesso");
  } catch (erro) {
    informarPerfil(`Não foi possível consultar: ${erro.message}`, "erro");
  }
}

function criarLinha(padrao) {
  const linha = document.createElement("tr");
  linha.dataset.codigo = padrao.padrao_cod;
  linha.append(criarCelula(padrao.padrao_cod));
  const grupo = document.createElement("td");
  grupo.append(criarSelecaoGrupo(padrao.grupo_cod, `Grupo de ${padrao.padrao_cod}`));
  linha.append(grupo);
  const nome = document.createElement("td");
  nome.append(criarCampo("textarea", padrao.padrao_nome, `Nome de ${padrao.padrao_cod}`, 200));
  linha.append(nome);
  const descricao = document.createElement("td");
  descricao.append(criarCampo("textarea", padrao.padrao_descr, `Descrição de ${padrao.padrao_cod}`));
  linha.append(descricao);
  linha.append(criarCelula(formatarCalculado(padrao.num_oco), "padrao-calculado"));
  linha.append(criarCelula(formatarCalculado(padrao.intervalo_medio), "padrao-calculado"));
  linha.append(criarCelula(formatarCalculado(padrao.desv_padrao), "padrao-calculado"));
  linha.append(criarCelula(padrao.detector_implementado ? "Implementada" : "Pendente"));
  const acoes = document.createElement("td");
  acoes.className = "padrao-acoes";
  acoes.append(criarBotao("Salvar", "salvar", padrao.padrao_cod), criarBotao("Excluir", "excluir", padrao.padrao_cod));
  linha.append(acoes);
  return linha;
}

function renderizar() {
  corpoTabela.replaceChildren(...estado.padroes.map(criarLinha));
}

async function carregarGrupos() {
  const corpo = await requisitar(API_GRUPOS);
  estado.grupos = corpo.grupos ?? [];
  preencherSelecao(grupoNovo);
  preencherSelecao(filtroGrupo, true);
}

async function carregarPadroes() {
  const parametro = filtroGrupo.value ? `?grupo_cod=${encodeURIComponent(filtroGrupo.value)}` : "";
  const corpo = await requisitar(`${API_PADROES}${parametro}`);
  estado.padroes = corpo.padroes ?? [];
  renderizar();
  informar(`${estado.padroes.length} padrão(ões) carregado(s).`, "sucesso");
}

async function carregar() {
  definirOcupado(true);
  informar("Carregando padrões...");
  try {
    await carregarGrupos();
    await carregarPadroes();
    if (estado.grupos.length === 0) informar("Cadastre um grupo antes de criar padrões.", "erro");
  } catch (erro) {
    informar(`Não foi possível carregar: ${erro.message}`, "erro");
  } finally {
    definirOcupado(false);
  }
}

async function criar(evento) {
  evento.preventDefault();
  if (estado.ocupado) return;
  definirOcupado(true);
  try {
    const corpo = await requisitar(API_PADROES, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grupo_cod: grupoNovo.value, padrao_nome: nomeNovo.value, padrao_descr: descricaoNova.value }),
    });
    if (!filtroGrupo.value || filtroGrupo.value === corpo.padrao.grupo_cod) estado.padroes.push(corpo.padrao);
    renderizar();
    formulario.reset();
    informar(`${corpo.padrao.padrao_cod} cadastrado.`, "sucesso");
  } catch (erro) {
    informar(`Não foi possível cadastrar: ${erro.message}`, "erro");
  } finally {
    definirOcupado(false);
  }
}

function localizarLinha(codigo) {
  return [...corpoTabela.querySelectorAll("tr")].find((linha) => linha.dataset.codigo === codigo);
}

async function salvar(codigo) {
  const linha = localizarLinha(codigo);
  const grupo = linha.querySelector("select");
  const [nome, descricao] = linha.querySelectorAll("input, textarea");
  const corpo = await requisitar(`${API_PADROES}/${codigo}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grupo_cod: grupo.value, padrao_nome: nome.value, padrao_descr: descricao.value }),
  });
  const indice = estado.padroes.findIndex((item) => item.padrao_cod === codigo);
  if (filtroGrupo.value && filtroGrupo.value !== corpo.padrao.grupo_cod) estado.padroes.splice(indice, 1);
  else estado.padroes[indice] = corpo.padrao;
  renderizar();
  informar(`${codigo} atualizado.`, "sucesso");
}

async function excluir(codigo) {
  if (!window.confirm(`Excluir definitivamente o padrão ${codigo}?`)) return;
  await requisitar(`${API_PADROES}/${codigo}`, { method: "DELETE" });
  estado.padroes = estado.padroes.filter((item) => item.padrao_cod !== codigo);
  renderizar();
  informar(`${codigo} excluído.`, "sucesso");
}

async function tratarAcao(evento) {
  const botao = evento.target.closest("button[data-acao]");
  if (!botao || estado.ocupado) return;
  definirOcupado(true);
  try {
    if (botao.dataset.acao === "salvar") await salvar(botao.dataset.codigo);
    else if (botao.dataset.acao === "excluir") await excluir(botao.dataset.codigo);
  } catch (erro) {
    informar(`Não foi possível concluir: ${erro.message}`, "erro");
  } finally {
    definirOcupado(false);
  }
}

formulario.addEventListener("submit", criar);
corpoTabela.addEventListener("click", tratarAcao);
filtroGrupo.addEventListener("change", carregarPadroes);
tipoCortePerfil.addEventListener("change", atualizarCamposCorte);
formularioPerfil.addEventListener("submit", carregarPerfil);
detalhesPerfil.addEventListener("toggle", () => {
  if (detalhesPerfil.open && !estado.perfilCarregado) carregarPerfil();
});
atualizarCamposCorte();
carregar();
