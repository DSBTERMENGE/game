const botao = document.querySelector("#botao-executar-screener");
const mensagem = document.querySelector("#mensagem-screener");
const corpoQuadro = document.querySelector("#corpo-quadro-screener");
const corpoValidacoes = document.querySelector("#corpo-validacoes-screener");

function celula(linha, texto) {
  const td = document.createElement("td");
  td.textContent = texto;
  linha.append(td);
  return td;
}

function preencherResumo(dados) {
  document.querySelector("#total-recebido").textContent = dados.total_recebido.toLocaleString("pt-BR");
  document.querySelector("#total-aprovado").textContent = dados.total_aprovado.toLocaleString("pt-BR");
  document.querySelector("#total-excluido").textContent = (dados.total_recebido - dados.total_aprovado).toLocaleString("pt-BR");
  document.querySelector("#duracao-screener").textContent = `${dados.duracao_segundos.toFixed(3)} s`;
}

function preencherQuadro(dados) {
  corpoQuadro.replaceChildren();
  dados.linhas.forEach((item) => {
    const linha = document.createElement("tr");
    celula(linha, item.ordem);
    celula(linha, item.codigo_criterio);
    celula(linha, item.avaliacoes.toLocaleString("pt-BR"));
    celula(linha, item.exclusoes.toLocaleString("pt-BR"));
    celula(linha, `${(100 * item.exclusoes / dados.total_recebido).toFixed(2)}%`);
    celula(linha, item.saldo.toLocaleString("pt-BR"));
    corpoQuadro.append(linha);
  });
}

function preencherValidacoes(casos) {
  corpoValidacoes.replaceChildren();
  casos.forEach((caso) => {
    const linha = document.createElement("tr");
    celula(linha, caso.combinacao.map((n) => String(n).padStart(2, "0")).join(", "));
    const tdEsperado = document.createElement("td");
    const seletor = document.createElement("select");
    [["", "Selecione"], ["aprovar", "Aprovar"], ["excluir", "Excluir"]].forEach(([valor, rotulo]) => {
      const opcao = document.createElement("option");
      opcao.value = valor;
      opcao.textContent = rotulo;
      seletor.append(opcao);
    });
    tdEsperado.append(seletor);
    linha.append(tdEsperado);
    celula(linha, caso.resultado_obtido);
    celula(linha, caso.criterio_decisivo || "Passou pelos oito filtros");
    const tdConformidade = celula(linha, "Pendente");
    seletor.addEventListener("change", () => {
      tdConformidade.className = "";
      if (!seletor.value) {
        tdConformidade.textContent = "Pendente";
      } else if (seletor.value === caso.resultado_obtido) {
        tdConformidade.textContent = "Conforme";
        tdConformidade.className = "conforme";
      } else {
        tdConformidade.textContent = "Divergente";
        tdConformidade.className = "divergente";
      }
    });
    corpoValidacoes.append(linha);
  });
}

async function executar() {
  botao.disabled = true;
  mensagem.textContent = "Executando amostra protegida...";
  try {
    const resposta = await fetch("/api/screener/quadro?limite_validacoes=30");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro?.mensagem || "Falha ao executar o screener.");
    preencherResumo(dados);
    preencherQuadro(dados);
    preencherValidacoes(dados.validacoes);
    mensagem.textContent = dados.aviso;
  } catch (erro) {
    mensagem.textContent = erro.message;
  } finally {
    botao.disabled = false;
  }
}

botao.addEventListener("click", executar);
