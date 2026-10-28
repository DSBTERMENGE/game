import { PROTOTIPO_SCREENER, validarFechamentoPrototipo } from "./screener-prototipo-dados.js";


const formato = new Intl.NumberFormat("pt-BR");
const percentual = (valor, base) => `${(100 * valor / base).toFixed(2).replace(".", ",")}%`;

function texto(seletor, valor) {
  document.querySelector(seletor).textContent = valor;
}

function celula(linha, valor, classe = "") {
  const td = document.createElement("td");
  td.textContent = valor;
  td.className = classe;
  linha.append(td);
}

function renderizarNivel(nivel, totalInicial) {
  const details = document.createElement("details");
  details.className = `prototipo-nivel prototipo-nivel--${nivel.codigo}`;
  const summary = document.createElement("summary");
  summary.innerHTML = `
    <strong>${nivel.titulo}</strong>
    <span>Entrada <b>${formato.format(nivel.entrada)}</b></span>
    <span>Excluídas <b>${formato.format(nivel.exclusoes)}</b></span>
    <span>% inicial <b>${percentual(nivel.exclusoes, totalInicial)}</b></span>
    <span>% recebido <b>${percentual(nivel.exclusoes, nivel.entrada)}</b></span>
    <span>Saldo <b>${formato.format(nivel.saldo)}</b></span>`;
  details.append(summary);

  const corpo = document.createElement("div");
  corpo.className = "prototipo-detalhes";
  if (nivel.limite_raridade) {
    const politica = document.createElement("p");
    politica.className = "prototipo-politica";
    politica.textContent = `Limite de raridade: frequência histórica < ${nivel.limite_raridade}. Selecionados: ${nivel.selecionados.join(", ")}.`;
    corpo.append(politica);
  }
  const tabela = document.createElement("table");
  tabela.innerHTML = "<thead><tr><th>Filtro decisivo</th><th>Regra/evidência</th><th>Exclusões líquidas</th><th>% recebido</th></tr></thead>";
  const tbody = document.createElement("tbody");
  nivel.filtros.forEach((filtro) => {
    const linha = document.createElement("tr");
    celula(linha, filtro.nome);
    celula(linha, filtro.regra);
    celula(linha, formato.format(filtro.exclusoes), "numero");
    celula(linha, percentual(filtro.exclusoes, nivel.entrada), "numero");
    tbody.append(linha);
  });
  tabela.append(tbody);
  corpo.append(tabela);
  details.append(corpo);
  return details;
}

function renderizar() {
  const dados = PROTOTIPO_SCREENER;
  const totalExcluido = dados.total_inicial - dados.total_aprovado;
  texto("#prototipo-total-inicial", formato.format(dados.total_inicial));
  texto("#prototipo-total-excluido", formato.format(totalExcluido));
  texto("#prototipo-percentual-excluido", percentual(totalExcluido, dados.total_inicial));
  texto("#prototipo-total-aprovado", formato.format(dados.total_aprovado));
  texto("#prototipo-percentual-aprovado", percentual(dados.total_aprovado, dados.total_inicial));
  const niveis = document.querySelector("#prototipo-niveis");
  niveis.replaceChildren(...dados.niveis.map((nivel) => renderizarNivel(nivel, dados.total_inicial)));
  const reconciliacao = document.querySelector("#prototipo-reconciliacao");
  reconciliacao.textContent = validarFechamentoPrototipo(dados)
    ? "Fechamento correto: total inicial = exclusões líquidas + aprovadas."
    : "Divergência no fechamento fictício.";
  reconciliacao.classList.toggle("divergente", !validarFechamentoPrototipo(dados));
}

document.querySelector("#botao-abrir-todos").addEventListener("click", () => {
  document.querySelectorAll(".prototipo-nivel").forEach((item) => { item.open = true; });
});
document.querySelector("#botao-fechar-todos").addEventListener("click", () => {
  document.querySelectorAll(".prototipo-nivel").forEach((item) => { item.open = false; });
});
renderizar();
