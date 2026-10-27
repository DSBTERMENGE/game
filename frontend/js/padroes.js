const API_PADROES = "/api/padroes";

const botaoAbrir = document.querySelector("#botao-cadastro-padroes");
const botaoFechar = document.querySelector("#botao-fechar-padroes");
const painel = document.querySelector("#painel-padroes");
const formulario = document.querySelector("#form-novo-padrao");
const nomeNovo = document.querySelector("#novo-padrao-nome");
const descricaoNova = document.querySelector("#novo-padrao-descr");
const corpoTabela = document.querySelector("#corpo-tabela-padroes");
const mensagem = document.querySelector("#mensagem-padroes");

const estadoPadroes = { padroes: [], ocupado: false };

function informarPadroes(texto, tipo = "informacao") {
  mensagem.textContent = texto;
  mensagem.dataset.tipo = tipo;
}

function formatarCalculado(valor) {
  if (valor === null || valor === undefined) return "—";
  return String(valor).replace(".", ",");
}

function criarCelula(texto, classe = "") {
  const celula = document.createElement("td");
  celula.textContent = texto;
  celula.className = classe;
  return celula;
}

function criarCampo(tag, valor, rotulo) {
  const campo = document.createElement(tag);
  campo.value = valor;
  campo.setAttribute("aria-label", rotulo);
  if (tag === "input") campo.maxLength = 200;
  else {
    campo.maxLength = 4000;
    campo.rows = 3;
  }
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

function criarLinha(padrao) {
  const linha = document.createElement("tr");
  linha.dataset.codigo = padrao.padrao_cod;
  linha.append(criarCelula(padrao.padrao_cod));

  const celulaNome = document.createElement("td");
  celulaNome.append(criarCampo("input", padrao.padrao_nome, `Nome de ${padrao.padrao_cod}`));
  linha.append(celulaNome);

  const celulaDescricao = document.createElement("td");
  celulaDescricao.append(
    criarCampo("textarea", padrao.padrao_descr, `Descrição de ${padrao.padrao_cod}`),
  );
  linha.append(celulaDescricao);

  linha.append(criarCelula(formatarCalculado(padrao.num_oco), "padrao-calculado"));
  linha.append(criarCelula(formatarCalculado(padrao.intervalo_medio), "padrao-calculado"));
  linha.append(criarCelula(formatarCalculado(padrao.desv_padrao), "padrao-calculado"));
  linha.append(criarCelula(padrao.detector_implementado ? "Implementada" : "Pendente"));

  const acoes = document.createElement("td");
  acoes.className = "padrao-acoes";
  acoes.append(
    criarBotao("Salvar", "salvar", padrao.padrao_cod),
    criarBotao("Excluir", "excluir", padrao.padrao_cod),
  );
  linha.append(acoes);
  return linha;
}

function renderizarPadroes(padroes = estadoPadroes.padroes) {
  corpoTabela.replaceChildren(...padroes.map(criarLinha));
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

async function carregarPadroes() {
  estadoPadroes.ocupado = true;
  informarPadroes("Carregando padrões...");
  try {
    const corpo = await requisitar(API_PADROES);
    estadoPadroes.padroes = corpo.padroes ?? [];
    renderizarPadroes();
    informarPadroes(
      `${estadoPadroes.padroes.length} padrão(ões) carregado(s).`,
      "sucesso",
    );
  } catch (erro) {
    informarPadroes(`Não foi possível carregar: ${erro.message}`, "erro");
  } finally {
    estadoPadroes.ocupado = false;
  }
}

async function criarPadrao(evento) {
  evento.preventDefault();
  if (estadoPadroes.ocupado) return;
  estadoPadroes.ocupado = true;
  try {
    const corpo = await requisitar(API_PADROES, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        padrao_nome: nomeNovo.value,
        padrao_descr: descricaoNova.value,
      }),
    });
    estadoPadroes.padroes.push(corpo.padrao);
    renderizarPadroes();
    formulario.reset();
    informarPadroes(`${corpo.padrao.padrao_cod} cadastrado.`, "sucesso");
  } catch (erro) {
    informarPadroes(`Não foi possível cadastrar: ${erro.message}`, "erro");
  } finally {
    estadoPadroes.ocupado = false;
  }
}

function localizarLinha(codigo) {
  return [...corpoTabela.querySelectorAll("tr")].find(
    (linha) => linha.dataset.codigo === codigo,
  );
}

async function salvarPadrao(codigo) {
  const linha = localizarLinha(codigo);
  const [nome, descricao] = linha.querySelectorAll("input, textarea");
  try {
    const corpo = await requisitar(`${API_PADROES}/${codigo}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ padrao_nome: nome.value, padrao_descr: descricao.value }),
    });
    const indice = estadoPadroes.padroes.findIndex((item) => item.padrao_cod === codigo);
    estadoPadroes.padroes[indice] = corpo.padrao;
    renderizarPadroes();
    informarPadroes(`${codigo} atualizado.`, "sucesso");
  } catch (erro) {
    informarPadroes(`Não foi possível salvar: ${erro.message}`, "erro");
  }
}

async function excluirPadrao(codigo) {
  if (!window.confirm(`Excluir definitivamente o padrão ${codigo}?`)) return;
  try {
    await requisitar(`${API_PADROES}/${codigo}`, { method: "DELETE" });
    estadoPadroes.padroes = estadoPadroes.padroes.filter(
      (item) => item.padrao_cod !== codigo,
    );
    renderizarPadroes();
    informarPadroes(`${codigo} excluído.`, "sucesso");
  } catch (erro) {
    informarPadroes(`Não foi possível excluir: ${erro.message}`, "erro");
  }
}

async function tratarAcao(evento) {
  const botao = evento.target.closest("button[data-acao]");
  if (!botao || estadoPadroes.ocupado) return;
  estadoPadroes.ocupado = true;
  try {
    if (botao.dataset.acao === "salvar") await salvarPadrao(botao.dataset.codigo);
    else if (botao.dataset.acao === "excluir") await excluirPadrao(botao.dataset.codigo);
  } finally {
    estadoPadroes.ocupado = false;
  }
}

async function abrirCadastroPadroes() {
  painel.hidden = false;
  botaoFechar.focus();
  await carregarPadroes();
}

function fecharCadastroPadroes() {
  painel.hidden = true;
  botaoAbrir.focus();
}

botaoAbrir.addEventListener("click", abrirCadastroPadroes);
botaoFechar.addEventListener("click", fecharCadastroPadroes);
formulario.addEventListener("submit", criarPadrao);
corpoTabela.addEventListener("click", tratarAcao);

window.gamePadroes = {
  abrirCadastroPadroes,
  carregarPadroes,
  fecharCadastroPadroes,
  formatarCalculado,
  renderizarPadroes,
};
