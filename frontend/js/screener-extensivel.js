import { validarQuadroExtensivel } from "./screener-extensivel-contrato.js";


const formato = new Intl.NumberFormat("pt-BR");
const percentual = (valor) => `${String(valor).replace(".", ",")}%`;

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

function renderizarFamilia(familia) {
  const details = document.createElement("details");
  details.className = `prototipo-nivel prototipo-nivel--${classeFamilia(familia.codigo)}`;
  const summary = document.createElement("summary");
  summary.innerHTML = `
    <strong>${familia.ordem} — ${familia.nome}</strong>
    <span>Entrada <b>${formato.format(familia.entrada)}</b></span>
    <span>Excluídas <b>${formato.format(familia.exclusoes)}</b></span>
    <span>% inicial <b>${percentual(familia.percentual_total_inicial)}</b></span>
    <span>% recebido <b>${percentual(familia.percentual_saldo_recebido)}</b></span>
    <span>Saldo <b>${formato.format(familia.saldo)}</b></span>`;
  details.append(summary);

  const corpo = document.createElement("div");
  corpo.className = "prototipo-detalhes";
  const tabela = document.createElement("table");
  tabela.innerHTML = "<thead><tr><th>Filtro</th><th>Integração</th><th>Entrada</th><th>Avaliações</th><th>Exclusões</th><th>% inicial</th><th>% recebido</th><th>Saldo</th></tr></thead>";
  const tbody = document.createElement("tbody");
  familia.filtros.forEach((filtro) => {
    const linha = document.createElement("tr");
    celula(linha, `${filtro.codigo} · ${filtro.nome}`);
    celula(linha, "Função Python validada", "integracao-validada");
    celula(linha, formato.format(filtro.entrada), "numero");
    celula(linha, formato.format(filtro.avaliacoes), "numero");
    celula(linha, formato.format(filtro.exclusoes), "numero");
    celula(linha, percentual(filtro.percentual_total_inicial), "numero");
    celula(linha, percentual(filtro.percentual_saldo_recebido), "numero");
    celula(linha, formato.format(filtro.saldo), "numero");
    tbody.append(linha);
  });
  tabela.append(tbody);
  corpo.append(tabela);
  details.append(corpo);
  return details;
}

export function renderizarQuadroExtensivel(dados) {
  if (!validarQuadroExtensivel(dados)) throw new Error("Quadro extensível não reconciliado.");
  texto("#extensivel-total-universo", formato.format(dados.escopo.total_universo));
  texto("#extensivel-total-analisado", formato.format(dados.resumo.total_analisado));
  texto("#extensivel-total-excluido", formato.format(dados.resumo.total_excluido));
  texto("#extensivel-percentual-excluido", percentual(dados.resumo.percentual_excluido));
  texto("#extensivel-total-aprovado", formato.format(dados.resumo.total_aprovado));
  texto("#extensivel-percentual-aprovado", percentual(dados.resumo.percentual_aprovado));
  document.querySelector("#extensivel-niveis").replaceChildren(
    ...dados.familias.map(renderizarFamilia),
  );
  texto("#extensivel-reconciliacao", "Fechamento correto: total analisado = exclusões líquidas + aprovadas.");
  texto(
    "#mensagem-extensivel",
    dados.escopo.processamento_integral
      ? "Processamento integral reconciliado."
      : "Amostra protegida reconciliada; não representa processamento integral.",
  );
  if (dados.comparacao) {
    const anterior = dados.comparacao.anterior.total_aprovado;
    const novo = dados.comparacao.novo.total_aprovado;
    const diferenca = dados.comparacao.diferenca_aprovadas;
    texto(
      "#extensivel-comparacao",
      `Mesma amostra — anterior: ${formato.format(anterior)} aprovadas; novo: ${formato.format(novo)}; diferença: ${formato.format(diferenca)}. As regras e a ordem são diferentes.`,
    );
  }
}

const botaoExecutar = document.querySelector("#botao-executar-extensivel");

async function executarAmostra() {
  botaoExecutar.disabled = true;
  texto("#mensagem-extensivel", "Executando 5.000 combinações e comparando os funis...");
  try {
    const resposta = await fetch("/api/screener/quadro-extensivel", { method: "POST" });
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro?.mensagem || "Falha no novo screener.");
    renderizarQuadroExtensivel(dados);
  } catch (erro) {
    texto("#mensagem-extensivel", erro.message);
  } finally {
    botaoExecutar.disabled = false;
  }
}

document.querySelector("#botao-abrir-todos").addEventListener("click", () => {
  document.querySelectorAll(".prototipo-nivel").forEach((item) => { item.open = true; });
});
document.querySelector("#botao-fechar-todos").addEventListener("click", () => {
  document.querySelectorAll(".prototipo-nivel").forEach((item) => { item.open = false; });
});
botaoExecutar.addEventListener("click", executarAmostra);
