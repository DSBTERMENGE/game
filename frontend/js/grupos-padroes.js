const API_GRUPOS = "/api/grupos-padroes";

const formulario = document.querySelector("#form-novo-grupo");
const nomeNovo = document.querySelector("#novo-grupo-nome");
const descricaoNova = document.querySelector("#novo-grupo-descr");
const corpoTabela = document.querySelector("#corpo-tabela-grupos");
const mensagem = document.querySelector("#mensagem-grupos");
const botaoAdicionar = document.querySelector("#botao-adicionar-grupo");
const estado = { grupos: [], ocupado: false };

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
  if (!resposta.ok) {
    throw new Error(corpo.erro?.mensagem ?? `A API respondeu com status ${resposta.status}.`);
  }
  return corpo;
}

function criarCampo(tag, valor, rotulo) {
  const campo = document.createElement(tag);
  campo.value = valor;
  campo.setAttribute("aria-label", rotulo);
  campo.maxLength = tag === "input" ? 200 : 4000;
  if (tag === "textarea") campo.rows = 2;
  return campo;
}

function criarBotao(texto, acao, codigo) {
  const botao = document.createElement("button");
  botao.type = "button";
  botao.textContent = texto;
  botao.dataset.acao = acao;
  botao.dataset.codigo = codigo;
  return botao;
}

function criarLinha(grupo) {
  const linha = document.createElement("tr");
  linha.dataset.codigo = grupo.grupo_cod;

  const codigo = document.createElement("td");
  codigo.textContent = grupo.grupo_cod;
  linha.append(codigo);

  const nome = document.createElement("td");
  nome.append(criarCampo("input", grupo.grupo_nome, `Nome de ${grupo.grupo_cod}`));
  linha.append(nome);

  const descricao = document.createElement("td");
  descricao.append(
    criarCampo("textarea", grupo.grupo_descr, `Descrição de ${grupo.grupo_cod}`),
  );
  linha.append(descricao);

  const acoes = document.createElement("td");
  acoes.className = "grupo-acoes";
  acoes.append(
    criarBotao("Salvar", "salvar", grupo.grupo_cod),
    criarBotao("Excluir", "excluir", grupo.grupo_cod),
  );
  linha.append(acoes);
  return linha;
}

function renderizar() {
  corpoTabela.replaceChildren(...estado.grupos.map(criarLinha));
}

function definirOcupado(ocupado) {
  estado.ocupado = ocupado;
  botaoAdicionar.disabled = ocupado;
}

async function carregar() {
  definirOcupado(true);
  informar("Carregando grupos...");
  try {
    const corpo = await requisitar(API_GRUPOS);
    estado.grupos = corpo.grupos ?? [];
    renderizar();
    informar(`${estado.grupos.length} grupo(s) carregado(s).`, "sucesso");
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
    const corpo = await requisitar(API_GRUPOS, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        grupo_nome: nomeNovo.value,
        grupo_descr: descricaoNova.value,
      }),
    });
    estado.grupos.push(corpo.grupo);
    renderizar();
    formulario.reset();
    informar(`${corpo.grupo.grupo_cod} cadastrado.`, "sucesso");
  } catch (erro) {
    informar(`Não foi possível cadastrar: ${erro.message}`, "erro");
  } finally {
    definirOcupado(false);
  }
}

function localizarLinha(codigo) {
  return [...corpoTabela.querySelectorAll("tr")].find(
    (linha) => linha.dataset.codigo === codigo,
  );
}

async function salvar(codigo) {
  const linha = localizarLinha(codigo);
  const [nome, descricao] = linha.querySelectorAll("input, textarea");
  const corpo = await requisitar(`${API_GRUPOS}/${codigo}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grupo_nome: nome.value, grupo_descr: descricao.value }),
  });
  const indice = estado.grupos.findIndex((item) => item.grupo_cod === codigo);
  estado.grupos[indice] = corpo.grupo;
  renderizar();
  informar(`${codigo} atualizado.`, "sucesso");
}

async function excluir(codigo) {
  if (!window.confirm(`Excluir definitivamente o grupo ${codigo}?`)) return;
  await requisitar(`${API_GRUPOS}/${codigo}`, { method: "DELETE" });
  estado.grupos = estado.grupos.filter((item) => item.grupo_cod !== codigo);
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
carregar();
