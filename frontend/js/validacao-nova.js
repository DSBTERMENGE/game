export const PAGINA_VALIDACAO_NOVA = "Validação e auditoria";

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
  const circulos = (desenho.circulos || []).map((item) => ({
    tipo: String(item.tipo || ""),
    centro_x: Number(item.centro_x), centro_y: Number(item.centro_y),
    raio: Number(item.raio),
  }));
  const elipses = (desenho.elipses || []).map((item) => ({
    tipo: String(item.tipo || ""),
    centro_x: Number(item.centro_x), centro_y: Number(item.centro_y),
    raio_x: Number(item.raio_x), raio_y: Number(item.raio_y),
    angulo_graus: Number(item.angulo_graus),
  }));
  if (marcadas.size !== 6 || segmentos.some((item) =>
    ![item.x1, item.y1, item.x2, item.y2].every(Number.isFinite)
  ) || circulos.some((item) =>
    ![item.centro_x, item.centro_y, item.raio].every(Number.isFinite) || item.raio <= 0
  ) || elipses.some((item) =>
    ![item.centro_x, item.centro_y, item.raio_x, item.raio_y, item.angulo_graus]
      .every(Number.isFinite) || item.raio_x <= 0 || item.raio_y <= 0
  )) throw new Error("Desenho da ocorrência inválido.");
  return { marcadas, segmentos, circulos, elipses };
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
} = {}) {
  const livre = atividade === null;
  return {
    selecaoGeral: livre,
    iniciarGeral: livre && !catalogoVazio,
    selecaoDirigida: livre,
    testarDirigido: livre && selecaoDirigida,
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
  const inspecaoEstado = document.querySelector("#validacao-nova-relatorio-inspecao-estado");
  const inspecaoTotal = document.querySelector("#validacao-nova-inspecao-total");
  const inspecaoOcorrencias = document.querySelector("#validacao-nova-inspecao-ocorrencias");
  const inspecaoPercentual = document.querySelector("#validacao-nova-inspecao-percentual");
  const blocoPainel = document.querySelector("#validacao-nova-painel");
  const painelGrupo = document.querySelector("#validacao-nova-painel-grupo");
  const painelFiltro = document.querySelector("#validacao-nova-painel-filtro");
  const painelContexto = document.querySelector("#validacao-nova-painel-contexto");
  const painelIndice = document.querySelector("#validacao-nova-painel-indice");
  const painelCombinacao = document.querySelector("#validacao-nova-painel-combinacao");
  const painelDezenas = document.querySelector("#validacao-nova-dezenas");
  const painelDesenho = document.querySelector("#validacao-nova-desenho");
  const painelCancelar = document.querySelector("#validacao-nova-painel-cancelar");
  const continuar = document.querySelector("#validacao-nova-continuar");
  const finalizar = document.querySelector("#validacao-nova-final");
  const dirigidoRaiz = document.querySelector("#validacao-nova-dirigido");
  const dirigidoGrupo = document.querySelector("#validacao-nova-dirigido-grupo");
  const dirigidoFiltro = document.querySelector("#validacao-nova-dirigido-filtro");
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
    });
    grupo.disabled = !controles.selecaoGeral;
    filtro.disabled = !controles.selecaoGeral;
    iniciar.disabled = !controles.iniciarGeral;
    dirigidoGrupo.disabled = !controles.selecaoDirigida;
    dirigidoFiltro.disabled = !controles.selecaoDirigida;
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
  const abrirProgresso = () => {
    if (!blocoProgresso.open) blocoProgresso.showModal();
  };
  const fecharProgresso = () => {
    if (blocoProgresso.open) blocoProgresso.close();
  };
  for (let dezena = 1; dezena <= 60; dezena += 1) {
    const celula = document.createElement("span");
    celula.className = "validacao-nova-dezena";
    celula.textContent = String(dezena).padStart(2, "0");
    painelDezenas.append(celula);
    celulas.set(dezena, celula);
  }
  const limparPainel = (
    mensagem = "Aguardando o início de um teste com um filtro específico.",
    processando = false,
  ) => {
    for (const celula of celulas.values()) {
      celula.classList.remove("validacao-nova-dezena--marcada");
    }
    painelDesenho.replaceChildren();
    painelGrupo.textContent = "—";
    painelFiltro.textContent = "—";
    painelContexto.hidden = true;
    painelIndice.textContent = "Relatório";
    painelCombinacao.textContent = mensagem;
    painelCombinacao.classList.toggle("validacao-nova-processando", processando);
    painelCancelar.disabled = true;
    continuar.disabled = true;
    finalizar.disabled = true;
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
    for (const item of desenho.circulos) {
      const circulo = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circulo.setAttribute("cx", String(item.centro_x));
      circulo.setAttribute("cy", String(item.centro_y));
      circulo.setAttribute("r", String(item.raio));
      circulo.dataset.tipo = item.tipo;
      painelDesenho.append(circulo);
    }
    for (const item of desenho.elipses) {
      const elipse = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
      elipse.setAttribute("cx", String(item.centro_x));
      elipse.setAttribute("cy", String(item.centro_y));
      elipse.setAttribute("rx", String(item.raio_x));
      elipse.setAttribute("ry", String(item.raio_y));
      elipse.setAttribute(
        "transform",
        `rotate(${item.angulo_graus} ${item.centro_x} ${item.centro_y})`,
      );
      elipse.dataset.tipo = item.tipo;
      painelDesenho.append(elipse);
    }
    painelGrupo.textContent = ocorrencia.nome_grupo;
    painelFiltro.textContent = ocorrencia.nome_filtro;
    painelContexto.hidden = false;
    inspecaoEstado.textContent = `${ocorrencia.nome_filtro}: combinação ${ocorrencia.indice_combinacao} em inspeção.`;
    painelIndice.textContent = `Combinação ${ocorrencia.indice_combinacao} de ${ocorrencia.total_combinacoes || 1000}`;
    painelCombinacao.textContent = formatarCombinacao(ocorrencia.combinacao);
    painelCombinacao.classList.remove("validacao-nova-processando");
    painelCancelar.disabled = false;
    finalizar.disabled = false;
    blocoPainel.hidden = false;
  };
  const exibirRelatorio = (resultado) => {
    if (Number(resultado?.total_filtros) === 1 && resultado?.resultados?.length === 1) {
      const item = resultado.resultados[0];
      inspecaoEstado.textContent = item.nome_filtro;
      inspecaoTotal.textContent = Number(item.total_testado).toLocaleString("pt-BR");
      inspecaoOcorrencias.textContent = Number(item.ocorrencias).toLocaleString("pt-BR");
      inspecaoPercentual.textContent = formatarIncidencia(item.incidencia_percentual);
      blocoRelatorio.hidden = true;
      return;
    }
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
  const exibirRelatorioDirigido = (registro) => {
    const total = Number(registro.resultado?.total_testado || 0);
    const ocorrencias = Number(registro.resultado?.ocorrencias_detectadas || 0);
    exibirRelatorio({
      total_filtros: 1,
      total_avaliacoes: total,
      resultados: [{
        nome_grupo: registro.nome_grupo,
        nome_filtro: registro.nome_filtro,
        total_testado: total,
        ocorrencias,
        incidencia_percentual: total ? (ocorrencias / total) * 100 : 0,
      }],
    });
  };
  const liberarSelecao = () => {
    cancelar.disabled = true;
    painelCancelar.disabled = true;
    continuar.disabled = true;
    finalizar.disabled = true;
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
      fecharProgresso();
      exibirOcorrencia(execucao.ocorrencia_atual);
      continuar.disabled = false;
      finalizar.disabled = false;
    } else if (["CANCELADA", "FALHOU"].includes(execucao?.estado)) {
      fecharProgresso();
      limparPainel("Nenhuma ocorrência em inspeção.");
    }
    if (execucao?.estado === "CONCLUIDA") {
      fecharProgresso();
      painelCombinacao.textContent = "";
      painelCombinacao.classList.remove("validacao-nova-processando");
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
        ? "Seleção pronta para iniciar o teste dirigido."
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
    dirigidoTestar.addEventListener("click", async () => {
      if (!iniciarAtividade("dirigido")) {
        dirigidoEstado.textContent = "Há outro teste em andamento. Conclua-o ou cancele-o primeiro.";
        dirigidoEstado.dataset.tipo = "erro";
        return;
      }
      dirigidoEstado.textContent = "Gerando e iniciando o teste das 10 combinações…";
      inspecaoEstado.textContent = "Teste dirigido em andamento.";
      inspecaoTotal.textContent = "—";
      inspecaoOcorrencias.textContent = "—";
      inspecaoPercentual.textContent = "—";
      blocoRelatorio.hidden = true;
      try {
        const respostaGeracao = await fetch("/api/validacao-nova/testes-dirigidos", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(corpoTesteDirigido(dirigidoGrupo.value, dirigidoFiltro.value)),
        });
        const gerado = await respostaGeracao.json();
        if (!respostaGeracao.ok) throw new Error(
          gerado.erro?.mensagem || "Não foi possível gerar dez combinações positivas. Verifique a descrição e o detector do filtro."
        );
        dirigidoRaiz.dataset.idTeste = gerado.id;
        const respostaExecucao = await fetch(
          `/api/validacao-nova/testes-dirigidos/${gerado.id}/execucao`, { method: "POST" }
        );
        const registro = await respostaExecucao.json();
        if (!respostaExecucao.ok) throw new Error(
          registro.erro?.mensagem || "Não foi possível iniciar o teste dirigido."
        );
        dirigidoEstado.textContent = apresentarTesteDirigido(registro);
        dirigidoRaiz.registroAtual = registro;
        blocoPainel.dataset.modo = "dirigido";
        exibirOcorrencia(ocorrenciaDirigidaParaPainel(registro));
        continuar.disabled = false;
        finalizar.disabled = false;
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
        estado.textContent = "Teste iniciado. O andamento será exibido em uma janela.";
        delete estado.dataset.tipo;
        grupo.disabled = true;
        filtro.disabled = true;
        iniciar.disabled = true;
        dialogo.close();
        abrirProgresso();
        corpoRelatorio.replaceChildren();
        blocoRelatorio.hidden = true;
        inspecaoEstado.textContent = "Teste em andamento.";
        inspecaoTotal.textContent = "—";
        inspecaoOcorrencias.textContent = "—";
        inspecaoPercentual.textContent = "—";
        limparPainel("Teste iniciado. Aguardando a primeira ocorrência do filtro.");
        cancelar.disabled = false;
        exibirExecucao(execucao);
        acompanhar(execucao.id);
      } catch (erro) {
        estado.textContent = erro.message;
        estado.dataset.tipo = "erro";
        encerrarAtividade();
      } finally {
        confirmar.disabled = false;
      }
    });
    const cancelarExecucaoGeral = async () => {
      const idExecucao = raiz.dataset.idExecucao;
      if (!idExecucao) return;
      cancelar.disabled = true;
      painelCancelar.disabled = true;
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
        if (!["CANCELADA", "FALHOU", "CONCLUIDA"].includes(execucao.estado)) abrirProgresso();
        acompanhar(idExecucao);
      } catch (erro) {
        progressoEstado.textContent = erro.message;
        progressoEstado.dataset.tipo = "erro";
        cancelar.disabled = false;
        painelCancelar.disabled = false;
      }
    };
    cancelar.addEventListener("click", cancelarExecucaoGeral);
    painelCancelar.addEventListener("click", async () => {
      if (blocoPainel.dataset.modo !== "dirigido") {
        await cancelarExecucaoGeral();
        return;
      }
      const idTeste = dirigidoRaiz.dataset.idTeste;
      if (!idTeste) return;
      painelCancelar.disabled = true;
      continuar.disabled = true;
      finalizar.disabled = true;
      try {
        const respostaCancelamento = await fetch(
          `/api/validacao-nova/testes-dirigidos/${idTeste}/cancelamento`, { method: "POST" }
        );
        const registro = await respostaCancelamento.json();
        if (!respostaCancelamento.ok) throw new Error(
          registro.erro?.mensagem || "Não foi possível cancelar o teste dirigido."
        );
        dirigidoRaiz.registroAtual = registro;
        dirigidoEstado.textContent = "Teste dirigido cancelado pelo usuário.";
        delete dirigidoEstado.dataset.tipo;
        delete blocoPainel.dataset.modo;
        limparPainel("Teste dirigido cancelado pelo usuário.");
        dirigidoGrupo.disabled = false;
        dirigidoFiltro.disabled = false;
        encerrarAtividade();
      } catch (erro) {
        dirigidoEstado.textContent = erro.message;
        dirigidoEstado.dataset.tipo = "erro";
        painelCancelar.disabled = false;
        continuar.disabled = false;
        finalizar.disabled = false;
      }
    });
    continuar.addEventListener("click", async () => {
      if (blocoPainel.dataset.modo === "dirigido") {
        const idTeste = dirigidoRaiz.dataset.idTeste;
        if (!idTeste) return;
        continuar.disabled = true;
        finalizar.disabled = true;
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
            finalizar.disabled = false;
          } else {
            delete blocoPainel.dataset.modo;
            painelCancelar.disabled = true;
            exibirRelatorioDirigido(registro);
            dirigidoResultado.hidden = true;
            dirigidoGrupo.disabled = false;
            dirigidoFiltro.disabled = false;
            encerrarAtividade();
          }
        } catch (erro) {
          dirigidoEstado.textContent = erro.message;
          dirigidoEstado.dataset.tipo = "erro";
          continuar.disabled = false;
          finalizar.disabled = false;
        }
        return;
      }
      const idExecucao = raiz.dataset.idExecucao;
      if (!idExecucao) return;
      continuar.disabled = true;
      finalizar.disabled = true;
      try {
        const respostaContinuacao = await fetch(
          `/api/validacao-nova/execucoes/${idExecucao}/continuacao`, { method: "POST" }
        );
        const execucao = await respostaContinuacao.json();
        if (!respostaContinuacao.ok) throw new Error(
          execucao.erro?.mensagem || "Não foi possível continuar o teste."
        );
        exibirExecucao(execucao);
        if (execucao.estado !== "AGUARDANDO_CONFIRMACAO") abrirProgresso();
        acompanhar(idExecucao);
      } catch (erro) {
        progressoEstado.textContent = erro.message;
        progressoEstado.dataset.tipo = "erro";
        continuar.disabled = false;
        finalizar.disabled = false;
      }
    });
    finalizar.addEventListener("click", async () => {
      finalizar.disabled = true;
      continuar.disabled = true;
      painelCancelar.disabled = true;
      if (blocoPainel.dataset.modo === "dirigido") {
        const idTeste = dirigidoRaiz.dataset.idTeste;
        if (!idTeste) return;
        try {
          const resposta = await fetch(
            `/api/validacao-nova/testes-dirigidos/${idTeste}/conclusao`, { method: "POST" }
          );
          const registro = await resposta.json();
          if (!resposta.ok) throw new Error(
            registro.erro?.mensagem || "Não foi possível concluir o teste dirigido."
          );
          dirigidoRaiz.registroAtual = registro;
          dirigidoEstado.textContent = apresentarTesteDirigido(registro);
          delete blocoPainel.dataset.modo;
          exibirRelatorioDirigido(registro);
          limparPainel("Teste dirigido concluído.");
          encerrarAtividade();
        } catch (erro) {
          dirigidoEstado.textContent = erro.message;
          dirigidoEstado.dataset.tipo = "erro";
          continuar.disabled = false;
          finalizar.disabled = false;
          painelCancelar.disabled = false;
        }
        return;
      }
      const idExecucao = raiz.dataset.idExecucao;
      if (!idExecucao) return;
      try {
        const resposta = await fetch(
          `/api/validacao-nova/execucoes/${idExecucao}/conclusao`, { method: "POST" }
        );
        const execucao = await resposta.json();
        if (!resposta.ok) throw new Error(
          execucao.erro?.mensagem || "Não foi possível concluir o teste."
        );
        limparPainel("Processando todas as ocorrências restantes…", true);
        abrirProgresso();
        exibirExecucao(execucao);
        acompanhar(idExecucao);
      } catch (erro) {
        progressoEstado.textContent = erro.message;
        progressoEstado.dataset.tipo = "erro";
        continuar.disabled = false;
        finalizar.disabled = false;
        painelCancelar.disabled = false;
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
