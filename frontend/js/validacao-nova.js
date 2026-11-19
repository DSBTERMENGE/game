export const PAGINA_VALIDACAO_NOVA = "Validação e auditoria NOVA";

export function validarCatalogo(dados) {
  if (!dados || !Array.isArray(dados.grupos)) throw new Error("Catálogo de filtros inválido.");
  return dados.grupos.map((grupo) => ({
    id_grupo: Number(grupo.id_grupo),
    nome_grupo: String(grupo.nome_grupo || ""),
    filtros: Array.isArray(grupo.filtros) ? grupo.filtros.map((filtro) => ({
      id_filtro: Number(filtro.id_filtro),
      nome_filtro: String(filtro.nome_filtro || ""),
      descricao: String(filtro.descricao || ""),
    })) : [],
  }));
}

export function filtrosDoGrupo(catalogo, idGrupo) {
  if (idGrupo === "") return [];
  return catalogo.find((grupo) => grupo.id_grupo === Number(idGrupo))?.filtros ?? [];
}

export function idsFiltrosSelecionados(catalogo, idGrupo, idFiltro) {
  if (idFiltro !== "") return [Number(idFiltro)];
  if (idGrupo !== "") return filtrosDoGrupo(catalogo, idGrupo).map((item) => item.id_filtro);
  return catalogo.flatMap((grupo) => grupo.filtros.map((item) => item.id_filtro));
}

export function resumirSelecao(catalogo, idGrupo, idFiltro) {
  const ids = idsFiltrosSelecionados(catalogo, idGrupo, idFiltro);
  if (idFiltro !== "") {
    const filtro = catalogo.flatMap((grupo) => grupo.filtros)
      .find((item) => item.id_filtro === Number(idFiltro));
    return { ids, texto: `1 filtro: ${filtro?.nome_filtro || "selecionado"}.` };
  }
  if (idGrupo !== "") {
    const grupo = catalogo.find((item) => item.id_grupo === Number(idGrupo));
    return { ids, texto: `${ids.length} filtro(s) do grupo ${grupo?.nome_grupo || "selecionado"}.` };
  }
  return { ids, texto: `Todos os ${ids.length} filtros disponíveis.` };
}

export function corpoInicioTeste(catalogo, idGrupo, idFiltro) {
  const selecao = resumirSelecao(catalogo, idGrupo, idFiltro);
  return { ids_filtros: selecao.ids };
}

export function apresentarEstadoExecucao(execucao) {
  const percentual = Math.max(0, Math.min(100, Number(execucao?.percentual || 0)));
  const mensagens = {
    AGUARDANDO: "Aguardando início do processamento.",
    EXECUTANDO: "Teste em execução.",
    CANCELANDO: "Cancelamento solicitado; aguardando ponto seguro.",
    CANCELADA: "Teste cancelado.",
    CONCLUIDA: "Teste concluído.",
    FALHOU: "O teste foi interrompido por uma falha.",
    AGUARDANDO_CONFIRMACAO: "Ocorrência encontrada; aguardando análise no painel.",
  };
  return {
    percentual,
    grupo: execucao?.grupo_atual || "—",
    filtro: execucao?.filtro_atual || "—",
    mensagem: mensagens[execucao?.estado] || "Consultando andamento.",
    terminou: ["CANCELADA", "CONCLUIDA", "FALHOU"].includes(execucao?.estado),
    erro: execucao?.estado === "FALHOU",
  };
}

export function organizarRelatorio(resultados) {
  const linhas = [];
  let grupoAnterior = null;
  for (const item of resultados || []) {
    if (item.nome_grupo !== grupoAnterior) {
      grupoAnterior = item.nome_grupo;
      linhas.push({ tipo: "grupo", nome_grupo: grupoAnterior });
    }
    linhas.push({
      tipo: "filtro",
      nome_filtro: item.nome_filtro,
      total_testado: Number(item.total_testado),
      ocorrencias: Number(item.ocorrencias),
      incidencia_percentual: Number(item.incidencia_percentual),
    });
  }
  return linhas;
}

export function formatarIncidencia(valor) {
  return `${Number(valor).toLocaleString("pt-BR", {
    minimumFractionDigits: 6, maximumFractionDigits: 6,
  })}%`;
}

export function prepararDesenhoPainel(ocorrencia) {
  const desenho = ocorrencia?.desenho || {};
  const marcadas = new Set((desenho.dezenas_marcadas || []).map(Number));
  const segmentos = (desenho.segmentos || []).map((item) => ({
    tipo: String(item.tipo || ""),
    x1: Number(item.x1), y1: Number(item.y1),
    x2: Number(item.x2), y2: Number(item.y2),
  }));
  if (marcadas.size !== 6 || segmentos.some((item) =>
    ![item.x1, item.y1, item.x2, item.y2].every(Number.isFinite)
  )) throw new Error("Desenho da ocorrência inválido.");
  return { marcadas, segmentos };
}

export function formatarCombinacao(dezenas) {
  return (dezenas || []).map((item) => String(item).padStart(2, "0")).join(" · ");
}

export function podeContinuarExecucao(execucao) {
  return Boolean(
    execucao?.estado === "AGUARDANDO_CONFIRMACAO" && execucao?.ocorrencia_atual
  );
}

export function selecaoDirigidaValida(idGrupo, idFiltro) {
  return Number.isInteger(Number(idGrupo)) && Number(idGrupo) > 0
    && Number.isInteger(Number(idFiltro)) && Number(idFiltro) > 0;
}

export function corpoTesteDirigido(idGrupo, idFiltro) {
  if (!selecaoDirigidaValida(idGrupo, idFiltro)) {
    throw new Error("Selecione um grupo e um filtro específicos.");
  }
  return { id_grupo: Number(idGrupo), id_filtro: Number(idFiltro) };
}

export function apresentarTesteDirigido(registro) {
  const mensagens = {
    GERADO: `${Number(registro?.total_combinacoes || 0)} combinações geradas e mantidas em memória.`,
    AGUARDANDO_CONFIRMACAO: "Teste iniciado; aguardando inspeção das combinações.",
    TESTADO: "Teste dirigido concluído.",
  };
  return mensagens[registro?.estado] || "Estado do teste dirigido atualizado.";
}

export function ocorrenciaDirigidaParaPainel(registro) {
  const ocorrencia = registro?.ocorrencia_atual;
  if (!ocorrencia) throw new Error("O teste dirigido não possui combinação para inspeção.");
  return {
    ...ocorrencia,
    nome_grupo: String(registro.nome_grupo || ""),
    nome_filtro: String(registro.nome_filtro || ""),
    indice_combinacao: Number(ocorrencia.numero),
    total_combinacoes: Number(registro.total_combinacoes || 10),
  };
}

export function resumirResultadoDirigido(resultado) {
  const total = Number(resultado?.total_testado || 0);
  const detectadas = Number(resultado?.ocorrencias_detectadas || 0);
  return `${total} combinações testadas · ${detectadas} ocorrência(s) detectada(s).`;
}

export function controlesPorAtividade({
  atividade = null, catalogoVazio = false, selecaoDirigida = false,
  testeDirigidoGerado = false,
} = {}) {
  const livre = atividade === null;
  return {
    selecaoGeral: livre,
    iniciarGeral: livre && !catalogoVazio,
    selecaoDirigida: livre,
    gerarDirigido: livre && selecaoDirigida,
    testarDirigido: livre && testeDirigidoGerado,
  };
}

function preencherSelecao(selecao, itens, valor, rotulo) {
  selecao.replaceChildren(new Option("Todos", ""));
  for (const item of itens) selecao.add(new Option(item[rotulo], String(item[valor])));
  selecao.disabled = false;
}

async function carregarCatalogo(raiz) {
  const grupo = raiz.querySelector("#validacao-nova-grupo");
  const filtro = raiz.querySelector("#validacao-nova-filtro");
  const estado = raiz.querySelector("#validacao-nova-estado");
  const resumo = raiz.querySelector("#validacao-nova-resumo");
  const iniciar = raiz.querySelector("#validacao-nova-iniciar");
  const dialogo = document.querySelector("#validacao-nova-confirmacao");
  const textoConfirmacao = document.querySelector("#validacao-nova-confirmacao-texto");
  const confirmar = document.querySelector("#validacao-nova-confirmar");
  const blocoProgresso = document.querySelector("#validacao-nova-progresso");
  const barra = document.querySelector("#validacao-nova-barra");
  const percentual = document.querySelector("#validacao-nova-percentual");
  const grupoAtual = document.querySelector("#validacao-nova-grupo-atual");
  const filtroAtual = document.querySelector("#validacao-nova-filtro-atual");
  const progressoEstado = document.querySelector("#validacao-nova-progresso-estado");
  const cancelar = document.querySelector("#validacao-nova-cancelar");
  const blocoRelatorio = document.querySelector("#validacao-nova-relatorio");
  const resumoRelatorio = document.querySelector("#validacao-nova-relatorio-resumo");
  const corpoRelatorio = document.querySelector("#validacao-nova-relatorio-corpo");
  const blocoPainel = document.querySelector("#validacao-nova-painel");
  const painelGrupo = document.querySelector("#validacao-nova-painel-grupo");
  const painelFiltro = document.querySelector("#validacao-nova-painel-filtro");
  const painelContexto = document.querySelector("#validacao-nova-painel-contexto");
  const painelIndice = document.querySelector("#validacao-nova-painel-indice");
  const painelCombinacao = document.querySelector("#validacao-nova-painel-combinacao");
  const painelDezenas = document.querySelector("#validacao-nova-dezenas");
  const painelDesenho = document.querySelector("#validacao-nova-desenho");
  const continuar = document.querySelector("#validacao-nova-continuar");
  const dirigidoRaiz = document.querySelector("#validacao-nova-dirigido");
  const dirigidoGrupo = document.querySelector("#validacao-nova-dirigido-grupo");
  const dirigidoFiltro = document.querySelector("#validacao-nova-dirigido-filtro");
  const dirigidoGerar = document.querySelector("#validacao-nova-dirigido-gerar");
  const dirigidoTestar = document.querySelector("#validacao-nova-dirigido-testar");
  const dirigidoEstado = document.querySelector("#validacao-nova-dirigido-estado");
  const dirigidoResultado = document.querySelector("#validacao-nova-dirigido-resultado");
  let temporizador = null;
  let atividadeAtual = null;
  let catalogoVazio = true;
  const aplicarBloqueios = () => {
    const controles = controlesPorAtividade({
      atividade: atividadeAtual,
      catalogoVazio,
      selecaoDirigida: selecaoDirigidaValida(dirigidoGrupo.value, dirigidoFiltro.value),
      testeDirigidoGerado: Boolean(dirigidoRaiz.dataset.idTeste),
    });
    grupo.disabled = !controles.selecaoGeral;
    filtro.disabled = !controles.selecaoGeral;
    iniciar.disabled = !controles.iniciarGeral;
    dirigidoGrupo.disabled = !controles.selecaoDirigida;
    dirigidoFiltro.disabled = !controles.selecaoDirigida;
    dirigidoGerar.disabled = !controles.gerarDirigido;
    dirigidoTestar.disabled = !controles.testarDirigido;
  };
  const iniciarAtividade = (tipo) => {
    if (atividadeAtual !== null) return false;
    atividadeAtual = tipo;
    aplicarBloqueios();
    return true;
  };
  const encerrarAtividade = () => {
    atividadeAtual = null;
    aplicarBloqueios();
  };
  const celulas = new Map();
  for (let dezena = 1; dezena <= 60; dezena += 1) {
    const celula = document.createElement("span");
    celula.className = "validacao-nova-dezena";
    celula.textContent = String(dezena).padStart(2, "0");
    painelDezenas.append(celula);
    celulas.set(dezena, celula);
  }
  const limparPainel = (mensagem = "Aguardando o início de um teste com um filtro específico.") => {
    for (const celula of celulas.values()) {
      celula.classList.remove("validacao-nova-dezena--marcada");
    }
    painelDesenho.replaceChildren();
    painelGrupo.textContent = "—";
    painelFiltro.textContent = "—";
    painelContexto.hidden = true;
    painelIndice.textContent = "Relatório";
    painelCombinacao.textContent = mensagem;
    continuar.disabled = true;
    blocoPainel.hidden = false;
  };
  const exibirOcorrencia = (ocorrencia) => {
    const desenho = prepararDesenhoPainel(ocorrencia);
    for (const [dezena, celula] of celulas) {
      celula.classList.toggle("validacao-nova-dezena--marcada", desenho.marcadas.has(dezena));
    }
    painelDesenho.replaceChildren();
    for (const segmento of desenho.segmentos) {
      const linha = document.createElementNS("http://www.w3.org/2000/svg", "line");
      for (const atributo of ["x1", "y1", "x2", "y2"]) {
        linha.setAttribute(atributo, String(segmento[atributo]));
      }
      linha.dataset.tipo = segmento.tipo;
      painelDesenho.append(linha);
    }
    painelGrupo.textContent = ocorrencia.nome_grupo;
    painelFiltro.textContent = ocorrencia.nome_filtro;
    painelContexto.hidden = false;
    painelIndice.textContent = `Combinação ${ocorrencia.indice_combinacao} de ${ocorrencia.total_combinacoes || 1000}`;
    painelCombinacao.textContent = formatarCombinacao(ocorrencia.combinacao);
    blocoPainel.hidden = false;
  };
  const exibirRelatorio = (resultado) => {
    corpoRelatorio.replaceChildren();
    for (const linha of organizarRelatorio(resultado?.resultados)) {
      const tr = document.createElement("tr");
      if (linha.tipo === "grupo") {
        tr.className = "validacao-nova-grupo";
        const th = document.createElement("th");
        th.colSpan = 4;
        th.scope = "rowgroup";
        th.textContent = linha.nome_grupo;
        tr.append(th);
      } else {
        for (const valor of [
          linha.nome_filtro,
          linha.total_testado.toLocaleString("pt-BR"),
          linha.ocorrencias.toLocaleString("pt-BR"),
          formatarIncidencia(linha.incidencia_percentual),
        ]) {
          const td = document.createElement("td");
          td.textContent = valor;
          tr.append(td);
        }
      }
      corpoRelatorio.append(tr);
    }
    resumoRelatorio.textContent = `${resultado.total_filtros} filtro(s) · ${resultado.total_avaliacoes.toLocaleString("pt-BR")} avaliações.`;
    blocoRelatorio.hidden = false;
  };
  const liberarSelecao = () => {
    cancelar.disabled = true;
    encerrarAtividade();
  };
  const exibirExecucao = (execucao) => {
    const visual = apresentarEstadoExecucao(execucao);
    barra.value = visual.percentual;
    barra.textContent = `${visual.percentual}%`;
    percentual.textContent = `${visual.percentual.toLocaleString("pt-BR")}%`;
    grupoAtual.textContent = visual.grupo;
    filtroAtual.textContent = visual.filtro;
    progressoEstado.textContent = visual.mensagem;
    progressoEstado.dataset.tipo = visual.erro ? "erro" : "";
    if (execucao?.estado === "CONCLUIDA" && execucao.resultado) {
      exibirRelatorio(execucao.resultado);
    }
    if (execucao?.estado === "AGUARDANDO_CONFIRMACAO" && execucao.ocorrencia_atual) {
      exibirOcorrencia(execucao.ocorrencia_atual);
      continuar.disabled = false;
    } else if (["CONCLUIDA", "CANCELADA", "FALHOU"].includes(execucao?.estado)) {
      limparPainel(execucao.estado === "CONCLUIDA"
        ? "Teste concluído. Selecione um filtro para realizar uma nova inspeção."
        : "Nenhuma ocorrência em inspeção.");
    }
    if (visual.terminou) liberarSelecao();
    return visual;
  };
  const acompanhar = async (idExecucao) => {
    try {
      const respostaEstado = await fetch(`/api/validacao-nova/execucoes/${idExecucao}`);
      const execucao = await respostaEstado.json();
      if (!respostaEstado.ok) throw new Error(execucao.erro?.mensagem || "Não foi possível consultar o teste.");
      const visual = exibirExecucao(execucao);
      if (!visual.terminou && execucao.estado !== "AGUARDANDO_CONFIRMACAO") {
        temporizador = setTimeout(() => acompanhar(idExecucao), 300);
      }
    } catch (erro) {
      progressoEstado.textContent = erro.message;
      progressoEstado.dataset.tipo = "erro";
      liberarSelecao();
    }
  };
  try {
    const resposta = await fetch("/api/validacao-nova/filtros");
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro?.mensagem || "Não foi possível consultar os filtros.");
    const catalogo = validarCatalogo(dados);
    preencherSelecao(grupo, catalogo, "id_grupo", "nome_grupo");
    preencherSelecao(filtro, [], "id_filtro", "nome_filtro");
    const preencherDirigido = (selecao, itens, valor, rotulo, textoInicial) => {
      selecao.replaceChildren(new Option(textoInicial, ""));
      for (const item of itens) selecao.add(new Option(item[rotulo], String(item[valor])));
      selecao.disabled = false;
    };
    preencherDirigido(dirigidoGrupo, catalogo, "id_grupo", "nome_grupo", "Selecione um grupo");
    preencherDirigido(dirigidoFiltro, [], "id_filtro", "nome_filtro", "Selecione um filtro");
    const atualizarDirigido = () => {
      const valido = selecaoDirigidaValida(dirigidoGrupo.value, dirigidoFiltro.value);
      delete dirigidoRaiz.dataset.idTeste;
      dirigidoResultado.hidden = true;
      dirigidoEstado.textContent = valido
        ? "Seleção pronta para gerar as 10 combinações."
        : "";
      delete dirigidoEstado.dataset.tipo;
      aplicarBloqueios();
    };
    dirigidoGrupo.addEventListener("change", () => {
      preencherDirigido(
        dirigidoFiltro, filtrosDoGrupo(catalogo, dirigidoGrupo.value),
        "id_filtro", "nome_filtro", "Selecione um filtro"
      );
      atualizarDirigido();
    });
    dirigidoFiltro.addEventListener("change", atualizarDirigido);
    dirigidoGerar.addEventListener("click", async () => {
      if (!iniciarAtividade("dirigido")) {
        dirigidoEstado.textContent = "Conclua ou cancele o teste em andamento antes de gerar outra coleção.";
        dirigidoEstado.dataset.tipo = "erro";
        return;
      }
      dirigidoEstado.textContent = "Gerando 10 combinações conhecidas…";
      try {
        const respostaDirigida = await fetch("/api/validacao-nova/testes-dirigidos", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(corpoTesteDirigido(dirigidoGrupo.value, dirigidoFiltro.value)),
        });
        const registro = await respostaDirigida.json();
        if (!respostaDirigida.ok) throw new Error(
          registro.erro?.mensagem || "Não foi possível gerar as combinações dirigidas."
        );
        dirigidoRaiz.dataset.idTeste = registro.id;
        dirigidoRaiz.registroAtual = registro;
        dirigidoEstado.textContent = apresentarTesteDirigido(registro);
        dirigidoGrupo.disabled = true;
        dirigidoFiltro.disabled = true;
        encerrarAtividade();
      } catch (erro) {
        dirigidoEstado.textContent = erro.message;
        dirigidoEstado.dataset.tipo = "erro";
        encerrarAtividade();
      }
    });
    dirigidoTestar.addEventListener("click", async () => {
      const idTeste = dirigidoRaiz.dataset.idTeste;
      if (!idTeste) {
        dirigidoEstado.textContent = "Gere primeiro as 10 combinações do teste dirigido.";
        dirigidoEstado.dataset.tipo = "erro";
        return;
      }
      if (!iniciarAtividade("dirigido")) {
        dirigidoEstado.textContent = "Há outro teste em andamento. Conclua-o ou cancele-o primeiro.";
        dirigidoEstado.dataset.tipo = "erro";
        return;
      }
      dirigidoEstado.textContent = "Iniciando o teste das 10 combinações…";
      try {
        const respostaDirigida = await fetch(
          `/api/validacao-nova/testes-dirigidos/${idTeste}/execucao`, { method: "POST" }
        );
        const registro = await respostaDirigida.json();
        if (!respostaDirigida.ok) throw new Error(
          registro.erro?.mensagem || "Não foi possível iniciar o teste dirigido."
        );
        dirigidoEstado.textContent = apresentarTesteDirigido(registro);
        dirigidoRaiz.registroAtual = registro;
        blocoPainel.dataset.modo = "dirigido";
        exibirOcorrencia(ocorrenciaDirigidaParaPainel(registro));
        continuar.disabled = false;
      } catch (erro) {
        dirigidoEstado.textContent = erro.message;
        dirigidoEstado.dataset.tipo = "erro";
        encerrarAtividade();
      }
    });
    const atualizarResumo = () => {
      resumo.textContent = resumirSelecao(catalogo, grupo.value, filtro.value).texto;
    };
    grupo.addEventListener("change", () => {
      preencherSelecao(
        filtro, filtrosDoGrupo(catalogo, grupo.value), "id_filtro", "nome_filtro"
      );
      atualizarResumo();
    });
    filtro.addEventListener("change", atualizarResumo);
    iniciar.addEventListener("click", () => {
      if (atividadeAtual !== null) {
        estado.textContent = "Conclua ou cancele o teste em andamento antes de iniciar outro.";
        estado.dataset.tipo = "erro";
        return;
      }
      textoConfirmacao.textContent = resumirSelecao(
        catalogo, grupo.value, filtro.value
      ).texto;
      dialogo.showModal();
    });
    confirmar.addEventListener("click", async (evento) => {
      evento.preventDefault();
      if (!iniciarAtividade("geral")) {
        estado.textContent = "Já existe um teste em andamento.";
        estado.dataset.tipo = "erro";
        dialogo.close();
        return;
      }
      confirmar.disabled = true;
      try {
        const respostaInicio = await fetch("/api/validacao-nova/execucoes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(corpoInicioTeste(catalogo, grupo.value, filtro.value)),
        });
        const execucao = await respostaInicio.json();
        if (!respostaInicio.ok) throw new Error(execucao.erro?.mensagem || "Não foi possível iniciar o teste.");
        raiz.dataset.idExecucao = execucao.id;
        estado.textContent = "Teste iniciado. O acompanhamento será exibido abaixo.";
        delete estado.dataset.tipo;
        grupo.disabled = true;
        filtro.disabled = true;
        iniciar.disabled = true;
        blocoProgresso.hidden = false;
        corpoRelatorio.innerHTML = '<tr><td colspan="4">Teste em andamento.</td></tr>';
        resumoRelatorio.textContent = "Aguardando a conclusão do teste.";
        blocoRelatorio.hidden = false;
        limparPainel("Teste iniciado. Aguardando a primeira ocorrência do filtro.");
        cancelar.disabled = false;
        exibirExecucao(execucao);
        dialogo.close();
        acompanhar(execucao.id);
      } catch (erro) {
        estado.textContent = erro.message;
        estado.dataset.tipo = "erro";
        encerrarAtividade();
      } finally {
        confirmar.disabled = false;
      }
    });
    cancelar.addEventListener("click", async () => {
      const idExecucao = raiz.dataset.idExecucao;
      if (!idExecucao) return;
      cancelar.disabled = true;
      if (temporizador) clearTimeout(temporizador);
      try {
        const respostaCancelamento = await fetch(
          `/api/validacao-nova/execucoes/${idExecucao}/cancelamento`, { method: "POST" }
        );
        const execucao = await respostaCancelamento.json();
        if (!respostaCancelamento.ok) throw new Error(
          execucao.erro?.mensagem || "Não foi possível cancelar o teste."
        );
        exibirExecucao(execucao);
        acompanhar(idExecucao);
      } catch (erro) {
        progressoEstado.textContent = erro.message;
        progressoEstado.dataset.tipo = "erro";
        cancelar.disabled = false;
      }
    });
    continuar.addEventListener("click", async () => {
      if (blocoPainel.dataset.modo === "dirigido") {
        const idTeste = dirigidoRaiz.dataset.idTeste;
        if (!idTeste) return;
        continuar.disabled = true;
        try {
          const respostaContinuacao = await fetch(
            `/api/validacao-nova/testes-dirigidos/${idTeste}/continuacao`, { method: "POST" }
          );
          const registro = await respostaContinuacao.json();
          if (!respostaContinuacao.ok) throw new Error(
            registro.erro?.mensagem || "Não foi possível continuar o teste dirigido."
          );
          dirigidoRaiz.registroAtual = registro;
          dirigidoEstado.textContent = apresentarTesteDirigido(registro);
          if (registro.estado === "AGUARDANDO_CONFIRMACAO") {
            exibirOcorrencia(ocorrenciaDirigidaParaPainel(registro));
            continuar.disabled = false;
          } else {
            limparPainel("Teste dirigido concluído. As 10 combinações foram inspecionadas.");
            delete blocoPainel.dataset.modo;
            dirigidoResultado.textContent = resumirResultadoDirigido(registro.resultado);
            dirigidoResultado.hidden = false;
            dirigidoGrupo.disabled = false;
            dirigidoFiltro.disabled = false;
            encerrarAtividade();
          }
        } catch (erro) {
          dirigidoEstado.textContent = erro.message;
          dirigidoEstado.dataset.tipo = "erro";
          continuar.disabled = false;
        }
        return;
      }
      const idExecucao = raiz.dataset.idExecucao;
      if (!idExecucao) return;
      continuar.disabled = true;
      try {
        const respostaContinuacao = await fetch(
          `/api/validacao-nova/execucoes/${idExecucao}/continuacao`, { method: "POST" }
        );
        const execucao = await respostaContinuacao.json();
        if (!respostaContinuacao.ok) throw new Error(
          execucao.erro?.mensagem || "Não foi possível continuar o teste."
        );
        limparPainel("Teste retomado. Aguardando a próxima ocorrência do filtro.");
        exibirExecucao(execucao);
        acompanhar(idExecucao);
      } catch (erro) {
        progressoEstado.textContent = erro.message;
        progressoEstado.dataset.tipo = "erro";
        continuar.disabled = false;
      }
    });
    raiz.catalogoFiltros = catalogo;
    atualizarResumo();
    atualizarDirigido();
    catalogoVazio = catalogo.every((item) => item.filtros.length === 0);
    aplicarBloqueios();
    estado.textContent = "";
    delete estado.dataset.tipo;
  } catch (erro) {
    estado.textContent = erro.message;
    estado.dataset.tipo = "erro";
  }
}

const raiz = typeof document === "undefined" ? null : document.querySelector("#validacao-nova-aplicacao");
if (raiz) carregarCatalogo(raiz);
