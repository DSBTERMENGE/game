const ESTADOS_TERMINAIS = new Set(["CONCLUIDA", "FALHOU", "CANCELADA"]);
let proximoIdentificadorModal = 1;

function segundos(valor) {
  return `${Number(valor || 0).toFixed(1)} s`;
}

export function criarModalAndamento({
  titulo, iniciar, consultar, cancelar = null, intervaloMs = 500,
  apresentarResultado = null, descricao = null, confirmarCancelamento = false,
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
  if (descricao !== null && typeof descricao !== "string" && typeof descricao !== "function") {
    throw new TypeError("descricao deve ser texto, função ou nulo.");
  }
  const dialogo = document.createElement("dialog");
  const identificadorTitulo = `modal-andamento-titulo-${proximoIdentificadorModal++}`;
  dialogo.className = "modal-andamento";
  dialogo.setAttribute("aria-labelledby", identificadorTitulo);
  dialogo.innerHTML = `
    <section class="modal-andamento__conteudo">
      <h2 id="${identificadorTitulo}"></h2>
      <p class="modal-andamento__contexto" hidden></p>
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
  const dialogoConfirmarCancelamento = document.createElement("dialog");
  const identificadorTituloCancelamento = `${identificadorTitulo}-cancelamento`;
  dialogoConfirmarCancelamento.className = "modal-andamento modal-andamento--confirmacao";
  dialogoConfirmarCancelamento.setAttribute("aria-labelledby", identificadorTituloCancelamento);
  dialogoConfirmarCancelamento.innerHTML = `
    <section class="modal-andamento__conteudo">
      <h2 id="${identificadorTituloCancelamento}">Cancelar processamento?</h2>
      <p>O trabalho será interrompido no próximo ponto seguro e os resultados parciais serão descartados.</p>
      <div class="modal-andamento__acoes">
        <button type="button" data-acao="continuar">Continuar processamento</button>
        <button type="button" data-acao="confirmar">Confirmar cancelamento</button>
      </div>
    </section>`;
  if (confirmarCancelamento) document.body.append(dialogoConfirmarCancelamento);
  const etapa = dialogo.querySelector(".modal-andamento__etapa");
  const contexto = dialogo.querySelector(".modal-andamento__contexto");
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
    const textoContexto = typeof descricao === "function" ? descricao() : descricao;
    contexto.hidden = !textoContexto;
    contexto.textContent = textoContexto || "";
    renderizar({ estado: "AGUARDANDO", etapa: "Iniciando…", concluido: 0, total: 4, percentual: 0 });
    dialogo.showModal();
    try {
      const dados = await iniciar();
      identificadorAtual = dados.id;
      renderizar(dados);
      return await aguardar(dados.id);
    } catch (falha) {
      const dadosFalha = {
        estado: "FALHOU", etapa: "Não foi possível iniciar", concluido: 0,
        total: 4, percentual: 0, erro: { mensagem: falha.message },
      };
      renderizar(dadosFalha);
      return dadosFalha;
    }
  }

  dialogo.addEventListener("cancel", (evento) => {
    if (executando) evento.preventDefault();
  });
  fechar.addEventListener("click", () => {
    if (!executando) dialogo.close();
  });
  async function solicitarCancelamento() {
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
  }
  botaoCancelar.addEventListener("click", () => {
    if (confirmarCancelamento) dialogoConfirmarCancelamento.showModal();
    else solicitarCancelamento();
  });
  if (confirmarCancelamento) {
    dialogoConfirmarCancelamento.querySelector('[data-acao="continuar"]').addEventListener("click", () => dialogoConfirmarCancelamento.close());
    dialogoConfirmarCancelamento.querySelector('[data-acao="confirmar"]').addEventListener("click", () => {
      dialogoConfirmarCancelamento.close();
      solicitarCancelamento();
    });
  }
  return { abrir, elemento: dialogo, estaExecutando: () => executando };
}
