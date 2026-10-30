const ESTADOS_TERMINAIS = new Set(["CONCLUIDA", "FALHOU", "CANCELADA"]);

function segundos(valor) {
  return `${Number(valor || 0).toFixed(1)} s`;
}

export function criarModalAndamento({
  titulo, iniciar, consultar, cancelar = null, intervaloMs = 500,
  apresentarResultado = null,
}) {
  if (typeof iniciar !== "function" || typeof consultar !== "function") {
    throw new TypeError("O modal exige funções para iniciar e consultar a operação.");
  }
  if (apresentarResultado !== null && typeof apresentarResultado !== "function") {
    throw new TypeError("apresentarResultado deve ser função ou nulo.");
  }
  if (cancelar !== null && typeof cancelar !== "function") {
    throw new TypeError("cancelar deve ser função ou nulo.");
  }
  const dialogo = document.createElement("dialog");
  dialogo.className = "modal-andamento";
  dialogo.setAttribute("aria-labelledby", "modal-andamento-titulo");
  dialogo.innerHTML = `
    <section class="modal-andamento__conteudo">
      <h2 id="modal-andamento-titulo"></h2>
      <p class="modal-andamento__etapa" aria-live="polite">Preparando operação…</p>
      <div class="modal-andamento__barra" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
        <div class="modal-andamento__progresso"></div>
      </div>
      <div class="modal-andamento__metricas">
        <span class="modal-andamento__quantidade">0 / 0 — 0%</span>
        <span class="modal-andamento__duracao">0,0 s</span>
      </div>
      <p class="modal-andamento__resultado" role="status" hidden></p>
      <p class="modal-andamento__erro" role="alert" hidden></p>
      <div class="modal-andamento__acoes">
        <button class="modal-andamento__cancelar" type="button" hidden>Cancelar</button>
        <button class="modal-andamento__fechar" type="button" disabled>Fechar</button>
      </div>
    </section>`;
  dialogo.querySelector("h2").textContent = titulo;
  document.body.append(dialogo);
  const etapa = dialogo.querySelector(".modal-andamento__etapa");
  const barra = dialogo.querySelector("[role='progressbar']");
  const progresso = dialogo.querySelector(".modal-andamento__progresso");
  const quantidade = dialogo.querySelector(".modal-andamento__quantidade");
  const duracao = dialogo.querySelector(".modal-andamento__duracao");
  const resultado = dialogo.querySelector(".modal-andamento__resultado");
  const erro = dialogo.querySelector(".modal-andamento__erro");
  const fechar = dialogo.querySelector(".modal-andamento__fechar");
  const botaoCancelar = dialogo.querySelector(".modal-andamento__cancelar");
  let executando = false;
  let identificadorAtual = null;
  let cancelamentoEnviado = false;

  function renderizar(dados) {
    const percentual = Math.max(0, Math.min(100, Number(dados.percentual || 0)));
    etapa.textContent = dados.etapa || dados.estado;
    progresso.style.width = `${percentual}%`;
    barra.setAttribute("aria-valuenow", String(percentual));
    quantidade.textContent = `${dados.concluido} / ${dados.total} — ${percentual}%`;
    duracao.textContent = segundos(dados.duracao_segundos);
    const terminal = ESTADOS_TERMINAIS.has(dados.estado);
    fechar.disabled = !terminal;
    executando = !terminal;
    botaoCancelar.hidden = cancelar === null || terminal;
    botaoCancelar.disabled = terminal || cancelamentoEnviado;
    if (dados.estado === "CONCLUIDA" && apresentarResultado) {
      const diagnostico = apresentarResultado(dados.resultado);
      resultado.hidden = false;
      resultado.textContent = diagnostico.mensagem;
      resultado.className = `modal-andamento__resultado modal-andamento__resultado--${diagnostico.aprovado ? "aprovado" : "pendente"}`;
    }
    if (dados.erro) {
      erro.hidden = false;
      erro.textContent = dados.erro.mensagem || "A operação não pôde ser concluída.";
    }
    return terminal;
  }

  async function aguardar(identificador) {
    while (executando) {
      const dados = await consultar(identificador);
      if (renderizar(dados)) return dados;
      await new Promise((resolver) => window.setTimeout(resolver, intervaloMs));
    }
    return null;
  }

  async function abrir() {
    if (executando) return null;
    erro.hidden = true;
    erro.textContent = "";
    resultado.hidden = true;
    resultado.textContent = "";
    resultado.className = "modal-andamento__resultado";
    fechar.disabled = true;
    executando = true;
    identificadorAtual = null;
    cancelamentoEnviado = false;
    renderizar({ estado: "AGUARDANDO", etapa: "Iniciando…", concluido: 0, total: 4, percentual: 0 });
    dialogo.showModal();
    try {
      const dados = await iniciar();
      identificadorAtual = dados.id;
      renderizar(dados);
      return await aguardar(dados.id);
    } catch (falha) {
      return renderizar({
        estado: "FALHOU", etapa: "Não foi possível iniciar", concluido: 0,
        total: 4, percentual: 0, erro: { mensagem: falha.message },
      });
    }
  }

  dialogo.addEventListener("cancel", (evento) => {
    if (executando) evento.preventDefault();
  });
  fechar.addEventListener("click", () => {
    if (!executando) dialogo.close();
  });
  botaoCancelar.addEventListener("click", async () => {
    if (!executando || cancelar === null || cancelamentoEnviado) return;
    cancelamentoEnviado = true;
    botaoCancelar.disabled = true;
    etapa.textContent = "Solicitando cancelamento seguro…";
    try {
      await cancelar(identificadorAtual);
    } catch (falha) {
      cancelamentoEnviado = false;
      botaoCancelar.disabled = false;
      erro.hidden = false;
      erro.textContent = falha.message || "Não foi possível solicitar o cancelamento.";
    }
  });
  return { abrir, elemento: dialogo, estaExecutando: () => executando };
}
