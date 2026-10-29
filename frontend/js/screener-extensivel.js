import { validarQuadroExtensivel } from "./screener-extensivel-contrato.js";


const formato = new Intl.NumberFormat("pt-BR");
const percentual = (valor) => `${String(valor).replace(".", ",")}%`;
const CHAVE_LIMITE_RARIDADE = "msen.screener.limiteRaridade";

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
  const politica = document.createElement("p");
  politica.className = "prototipo-politica";
  politica.textContent = `Aplicados somente quando a incidência histórica é ${detalhes.operador} ${detalhes.limite_percentual}%.`;
  painel.append(politica);
  detalhes.grupos.forEach((grupo) => {
    const bloco = document.createElement("details");
    bloco.className = "padrao-grupo";
    const resumo = document.createElement("summary");
    resumo.innerHTML = `<strong>${grupo.grupo_cod} · ${grupo.grupo_nome}</strong><span>Entrada <b>${formato.format(grupo.entrada)}</b></span><span>Exclusões <b>${formato.format(grupo.exclusoes)}</b></span><span>Saldo <b>${formato.format(grupo.saldo)}</b></span>`;
    bloco.append(resumo);
    const rolagem = document.createElement("div");
    rolagem.className = "padrao-grupo-tabela";
    const tabela = document.createElement("table");
    tabela.innerHTML = "<thead><tr><th>Padrão</th><th>Incidência histórica</th><th>Limite</th><th>Estado</th><th>Avaliações</th><th>Correspondências</th><th>Exclusões</th><th>Saldo</th></tr></thead>";
    const corpo = document.createElement("tbody");
    grupo.padroes.forEach((padrao) => {
      const linha = document.createElement("tr");
      linha.className = "padrao-aplicado";
      celula(linha, `${padrao.padrao_cod} · ${padrao.padrao_nome}`);
      celula(linha, `${percentual(padrao.percentual_ocorrencia)} (${formato.format(padrao.num_ocorrencias)}/${formato.format(padrao.total_sorteios)})`, "numero");
      celula(linha, `${padrao.operador} ${percentual(padrao.limite_percentual)}`, "numero");
      celula(linha, "Aplicado: raro", "estado-padrao");
      celula(linha, formato.format(padrao.avaliacoes), "numero");
      celula(linha, formato.format(padrao.correspondencias), "numero");
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
    celula(linha, descricaoFiltro(filtro, familia, detalhesPadroes));
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
  if (familia.codigo === "PADROES") corpo.append(renderizarDetalhesPadroes(detalhesPadroes));
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
  const selecionados = dados.configuracao_raridade.padroes_selecionados;
  texto(
    "#extensivel-raridade-usada",
    `Limite usado: ${dados.configuracao_raridade.operador} ${percentual(dados.configuracao_raridade.limite_percentual)}. Padrões selecionados: ${selecionados.length ? selecionados.join(", ") : "nenhum"}.`,
  );
  document.querySelector("#limite-raridade-extensivel").value = dados.configuracao_raridade.limite_percentual;
  localStorage.setItem(CHAVE_LIMITE_RARIDADE, dados.configuracao_raridade.limite_percentual);
  document.querySelector("#extensivel-niveis").replaceChildren(
    ...dados.familias.map((familia) => renderizarFamilia(familia, dados.detalhes_padroes)),
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
const botaoAbrirTodos = document.querySelector("#botao-abrir-todos");
const botaoFecharTodos = document.querySelector("#botao-fechar-todos");
const limiteRaridade = document.querySelector("#limite-raridade-extensivel");
let detalhesDisponiveis = false;

function atualizarControles(processando = false) {
  botaoExecutar.disabled = processando;
  limiteRaridade.disabled = processando;
  botaoAbrirTodos.disabled = processando || !detalhesDisponiveis;
  botaoFecharTodos.disabled = processando || !detalhesDisponiveis;
}

const limiteMemorizado = localStorage.getItem(CHAVE_LIMITE_RARIDADE);
if (limiteMemorizado !== null) {
  limiteRaridade.value = limiteMemorizado;
  if (!limiteRaridade.checkValidity()) limiteRaridade.value = "10";
}

async function executarAmostra() {
  if (!limiteRaridade.checkValidity()) {
    limiteRaridade.reportValidity();
    texto("#mensagem-extensivel", "Informe um limite de raridade entre 0% e 100%.");
    return;
  }
  atualizarControles(true);
  texto("#mensagem-extensivel", "Executando 5.000 combinações e comparando os funis...");
  try {
    const resposta = await fetch("/api/screener/quadro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ limite_raridade: limiteRaridade.value }),
    });
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro?.mensagem || "Falha no novo screener.");
    renderizarQuadroExtensivel(dados);
    detalhesDisponiveis = true;
  } catch (erro) {
    texto("#mensagem-extensivel", `Não foi possível concluir a execução: ${erro.message}`);
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
botaoExecutar.addEventListener("click", executarAmostra);
atualizarControles(false);
