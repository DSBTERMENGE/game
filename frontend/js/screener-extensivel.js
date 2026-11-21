import { validarQuadroExtensivel } from "./screener-extensivel-contrato.js";
import { criarModalAndamento } from "./modal-andamento.js";


const formato = new Intl.NumberFormat("pt-BR");
const percentual = (valor) => `${String(valor).replace(".", ",")}%`;
const percentualCurto = (valor) => `(${Number(valor).toLocaleString("pt-BR", {
  minimumFractionDigits: 2, maximumFractionDigits: 2,
})}%)`;
function texto(seletor, valor, raiz = document) {
  raiz.querySelector(seletor).textContent = valor;
}

function celula(linha, valor, classe = "") {
  const td = document.createElement("td");
  td.textContent = valor;
  td.className = classe;
  linha.append(td);
}

function classeFamilia(codigo) {
  return {
    ESTATISTICA: "estatistica",
    GEOMETRIA: "geometria",
    PADROES: "padroes",
  }[codigo];
}

function valorOuTraco(valor) {
  return valor === null || valor === undefined ? "—" : formato.format(valor);
}

function descricaoFiltro(filtro, familia, detalhesPadroes) {
  if (familia.codigo !== "PADROES") return `${filtro.codigo} · ${filtro.nome}`;
  const codigoPadrao = filtro.codigo.replace(/^PAD_/, "");
  for (const grupo of detalhesPadroes.grupos) {
    const padrao = grupo.padroes.find((item) => item.padrao_cod === codigoPadrao);
    if (padrao) {
      return `${padrao.padrao_cod} · ${padrao.padrao_nome} | ${grupo.grupo_cod} · ${grupo.grupo_nome}`;
    }
  }
  return `${filtro.codigo} · ${filtro.nome}`;
}

function renderizarDetalhesPadroes(detalhes) {
  const painel = document.createElement("section");
  painel.className = "padroes-detalhados";
  detalhes.grupos.forEach((grupo) => {
    const bloco = document.createElement("details");
    bloco.className = "padrao-grupo";
    const resumo = document.createElement("summary");
    resumo.innerHTML = `<strong>${grupo.grupo_cod} · ${grupo.grupo_nome}</strong><span>Entrada <b>${formato.format(grupo.entrada)}</b></span><span>Exclusões <b>${formato.format(grupo.exclusoes)}</b></span><span>Saldo <b>${formato.format(grupo.saldo)}</b></span>`;
    bloco.append(resumo);
    const rolagem = document.createElement("div");
    rolagem.className = "padrao-grupo-tabela";
    const tabela = document.createElement("table");
    tabela.innerHTML = "<thead><tr><th>Padrão</th><th>Avaliações</th><th>Exclusões</th><th>Saldo</th></tr></thead>";
    const corpo = document.createElement("tbody");
    grupo.padroes.forEach((padrao) => {
      const linha = document.createElement("tr");
      linha.className = "padrao-aplicado";
      celula(linha, `${padrao.padrao_cod} · ${padrao.padrao_nome}`);
      celula(linha, formato.format(padrao.avaliacoes), "numero");
      celula(linha, formato.format(padrao.exclusoes), "numero");
      celula(linha, valorOuTraco(padrao.saldo), "numero");
      corpo.append(linha);
    });
    tabela.append(corpo);
    rolagem.append(tabela);
    bloco.append(rolagem);
    painel.append(bloco);
  });
  return painel;
}

function renderizarFamilia(familia, detalhesPadroes) {
  const details = document.createElement("details");
  details.className = `prototipo-nivel prototipo-nivel--${classeFamilia(familia.codigo)}`;
  const summary = document.createElement("summary");
  summary.innerHTML = `
    <strong>${familia.ordem} — ${familia.nome}</strong>
    <span>Entrada <b>${formato.format(familia.entrada)}</b></span>
    <span>Excluídas <b>${formato.format(familia.exclusoes)}</b></span>
    <span>% excluído <b>${percentual(familia.percentual_saldo_recebido)}</b></span>
    <span>Saldo <b>${formato.format(familia.saldo)}</b></span>`;
  details.append(summary);

  const corpo = document.createElement("div");
  corpo.className = "prototipo-detalhes";
  const tabela = document.createElement("table");
  tabela.innerHTML = "<thead><tr><th>Filtro</th><th>Integração</th><th>Entrada</th><th>Avaliações</th><th>Exclusões</th><th>% excluído</th><th>Saldo</th></tr></thead>";
  const tbody = document.createElement("tbody");
  familia.filtros.forEach((filtro) => {
    const linha = document.createElement("tr");
    celula(linha, descricaoFiltro(filtro, familia, detalhesPadroes));
    celula(linha, "Função Python validada", "integracao-validada");
    celula(linha, formato.format(filtro.entrada), "numero");
    celula(linha, formato.format(filtro.avaliacoes), "numero");
    celula(linha, formato.format(filtro.exclusoes), "numero");
    celula(linha, percentual(filtro.percentual_saldo_recebido), "numero");
    celula(linha, formato.format(filtro.saldo), "numero");
    tbody.append(linha);
  });
  tabela.append(tbody);
  corpo.append(tabela);
  if (familia.codigo === "PADROES") corpo.append(renderizarDetalhesPadroes(detalhesPadroes));
  details.append(corpo);
  return details;
}

export function renderizarQuadroExtensivel(dados) {
  if (!validarQuadroExtensivel(dados)) throw new Error("Quadro extensível não reconciliado.");
  texto("#extensivel-total-analisado", formato.format(dados.resumo.total_analisado));
  texto("#extensivel-total-excluido", formato.format(dados.resumo.total_excluido));
  texto("#extensivel-percentual-excluido", percentualCurto(dados.resumo.percentual_excluido));
  texto("#extensivel-total-aprovado", formato.format(dados.resumo.total_aprovado));
  texto("#extensivel-percentual-aprovado", percentualCurto(dados.resumo.percentual_aprovado));
  document.querySelector("#extensivel-niveis").replaceChildren(
    ...dados.familias.map((familia) => renderizarFamilia(familia, dados.detalhes_padroes)),
  );
  texto("#extensivel-reconciliacao", "Fechamento correto: total analisado = exclusões líquidas + aprovadas.");
  texto(
    "#mensagem-extensivel",
    dados.escopo.processamento_integral
      ? "Aplicação do Screener concluída e conferida."
      : "Teste do Screener concluído com 5.000 combinações; este resultado não representa a aplicação integral.",
  );
  if (dados.comparacao) {
    const anterior = dados.comparacao.anterior.total_aprovado;
    const novo = dados.comparacao.novo.total_aprovado;
    const diferenca = dados.comparacao.diferenca_aprovadas;
    texto(
      "#extensivel-comparacao",
      `Mesmo conjunto de teste — resultado anterior: ${formato.format(anterior)} aprovadas; resultado atual: ${formato.format(novo)}; diferença: ${formato.format(diferenca)}. As regras e a ordem são diferentes.`,
    );
  }
}

const botaoExecutar = document.querySelector("#botao-executar-extensivel");
const botaoAplicacao = document.querySelector("#botao-aplicacao-screener");
const dialogoConfirmarTeste = document.querySelector("#dialogo-confirmar-teste-screener");
const botaoConfirmarTeste = document.querySelector("#botao-confirmar-teste-screener");
const dialogoConfirmarAplicacao = document.querySelector("#dialogo-confirmar-aplicacao-screener");
const botaoConfirmarAplicacao = document.querySelector("#botao-confirmar-aplicacao-screener");
const botaoAbrirTodos = document.querySelector("#botao-abrir-todos");
const botaoFecharTodos = document.querySelector("#botao-fechar-todos");
let detalhesDisponiveis = false;

async function respostaJson(resposta) {
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro?.mensagem || `Falha HTTP ${resposta.status}.`);
  return dados;
}

const modalTeste = criarModalAndamento({
  titulo: "Teste do Screener",
  descricao: "Aplicação dos filtros atuais e comparação com o resultado anterior sobre as mesmas 5.000 combinações.",
  confirmarCancelamento: true,
  iniciar: async () => respostaJson(await fetch("/api/screener/execucoes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  })),
  consultar: async (id) => respostaJson(await fetch(`/api/screener/execucoes/${encodeURIComponent(id)}`)),
  cancelar: async (id) => respostaJson(await fetch(
    `/api/screener/execucoes/${encodeURIComponent(id)}/cancelamento`, { method: "POST" },
  )),
  apresentarResultado: (dados) => {
    renderizarQuadroExtensivel(dados);
    detalhesDisponiveis = true;
    return { aprovado: true, mensagem: "Teste concluído. Os resultados estão disponíveis na página." };
  },
});

const modalAplicacao = criarModalAndamento({
  titulo: "Aplicação do Screener",
  descricao: "Aplicação dos filtros atuais sobre todas as 50.063.860 combinações possíveis.",
  confirmarCancelamento: true,
  iniciar: async () => respostaJson(await fetch("/api/screener/execucoes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      escopo: "integral",
      confirmacao_integral: "PROCESSAR_50063860_COMBINACOES",
    }),
  })),
  consultar: async (id) => respostaJson(await fetch(`/api/screener/execucoes/${encodeURIComponent(id)}`)),
  cancelar: async (id) => respostaJson(await fetch(
    `/api/screener/execucoes/${encodeURIComponent(id)}/cancelamento`, { method: "POST" },
  )),
  apresentarResultado: (dados) => {
    renderizarQuadroExtensivel(dados);
    texto("#extensivel-comparacao", "Aplicação integral concluída; a comparação histórica pertence somente ao Teste do Screener.");
    detalhesDisponiveis = true;
    return { aprovado: true, mensagem: "Aplicação integral concluída. Os resultados estão disponíveis na página." };
  },
});

function atualizarControles(processando = false) {
  botaoExecutar.disabled = processando;
  botaoAplicacao.disabled = processando;
  botaoAbrirTodos.disabled = processando || !detalhesDisponiveis;
  botaoFecharTodos.disabled = processando || !detalhesDisponiveis;
}

async function executarAmostra() {
  atualizarControles(true);
  texto("#mensagem-extensivel", "Teste em andamento: analisando 5.000 combinações e comparando os resultados...");
  try {
    const final = await modalTeste.abrir();
    if (final?.estado === "CANCELADA") {
      texto("#mensagem-extensivel", "Teste cancelado. Os resultados parciais foram descartados.");
    } else if (final?.estado === "FALHOU") {
      texto("#mensagem-extensivel", `Não foi possível concluir o teste: ${final.erro?.mensagem || "falha não identificada"}.`);
    }
  } finally {
    atualizarControles(false);
  }
}

async function executarAplicacaoIntegral() {
  atualizarControles(true);
  texto("#mensagem-extensivel", "Aplicação em andamento: analisando 50.063.860 combinações...");
  try {
    const final = await modalAplicacao.abrir();
    if (final?.estado === "CANCELADA") {
      texto("#mensagem-extensivel", "Aplicação cancelada. Os resultados parciais foram descartados.");
    } else if (final?.estado === "FALHOU") {
      texto("#mensagem-extensivel", `Não foi possível concluir a aplicação: ${final.erro?.mensagem || "falha não identificada"}.`);
    }
  } finally {
    atualizarControles(false);
  }
}

botaoAbrirTodos.addEventListener("click", () => {
  document.querySelectorAll(".prototipo-nivel").forEach((item) => { item.open = true; });
});
botaoFecharTodos.addEventListener("click", () => {
  document.querySelectorAll(".prototipo-nivel").forEach((item) => { item.open = false; });
});
botaoExecutar.addEventListener("click", () => {
  dialogoConfirmarTeste.showModal();
});
botaoConfirmarTeste.addEventListener("click", () => {
  queueMicrotask(executarAmostra);
});
botaoAplicacao.addEventListener("click", () => {
  dialogoConfirmarAplicacao.showModal();
});
botaoConfirmarAplicacao.addEventListener("click", () => {
  queueMicrotask(executarAplicacaoIntegral);
});
atualizarControles(false);
