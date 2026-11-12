const ESTADOS = Object.freeze({
  CARREGANDO_LISTA: "CARREGANDO_LISTA",
  CONSULTA: "CONSULTA",
  NOVO: "NOVO",
  EDICAO: "EDICAO",
  CONFERENCIA: "CONFERENCIA",
  SALVANDO: "SALVANDO",
  ERRO: "ERRO",
});

const copiar = (valor) => valor == null ? valor : structuredClone(valor);

function validarContrato({ campos, api }) {
  if (!Array.isArray(campos) || campos.length === 0) {
    throw new TypeError("O CRUD exige ao menos um campo configurado.");
  }
  const nomes = new Set();
  for (const campo of campos) {
    if (!campo || typeof campo.nome !== "string" || typeof campo.rotulo !== "string") {
      throw new TypeError("Cada campo exige nome e rótulo.");
    }
    if (nomes.has(campo.nome)) throw new TypeError(`Campo repetido: ${campo.nome}.`);
    nomes.add(campo.nome);
  }
  for (const operacao of ["listar", "criar", "atualizar", "arquivar", "desarquivar"]) {
    if (typeof api?.[operacao] !== "function") {
      throw new TypeError(`O adaptador de API exige a operação ${operacao}.`);
    }
  }
}

function dadosIniciais(campos) {
  return Object.fromEntries(campos.map((campo) => [campo.nome, copiar(campo.valorInicial ?? "")]));
}

function validarDados(campos, dados) {
  const erros = {};
  for (const campo of campos) {
    const valor = dados[campo.nome];
    if (campo.obrigatorio && (valor == null || String(valor).trim() === "")) {
      erros[campo.nome] = `${campo.rotulo} deve ser preenchido.`;
      continue;
    }
    if (campo.validar) {
      const mensagem = campo.validar(valor, dados);
      if (mensagem) erros[campo.nome] = mensagem;
    }
  }
  return erros;
}

async function chavePadrao() {
  const bytes = new TextEncoder().encode(crypto.randomUUID());
  const resumo = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(resumo)].map((item) => item.toString(16).padStart(2, "0")).join("");
}

export function criarControladorCrud({
  campos, api, porPagina = 20, gerarChaveIdempotencia = chavePadrao,
  usarOrdenacao = true,
}) {
  validarContrato({ campos, api });
  if (!Number.isInteger(porPagina) || porPagina < 1 || porPagina > 100) {
    throw new TypeError("porPagina deve ficar entre 1 e 100.");
  }
  const ouvintes = new Set();
  let estado = {
    modo: ESTADOS.CONSULTA, itens: [], total: 0, pagina: 1, porPagina,
    busca: "", filtros: {}, ordenacao: usarOrdenacao ? "ATUALIZACAO" : null, arquivados: false,
    selecionado: null, rascunho: null, origemRascunho: null,
    erros: {}, mensagem: "", falha: null, ocupada: false,
  };

  const publicar = () => {
    const fotografia = copiar(estado);
    for (const ouvinte of ouvintes) ouvinte(fotografia);
    return fotografia;
  };
  const alterarEstado = (mudancas) => {
    estado = { ...estado, ...mudancas };
    return publicar();
  };
  const consultaAtual = () => ({
    busca: estado.busca, ...estado.filtros,
    ...(usarOrdenacao ? { ordenacao: estado.ordenacao } : {}),
    arquivados: estado.arquivados, pagina: estado.pagina, por_pagina: estado.porPagina,
  });

  async function carregar(mudancas = {}) {
    estado = { ...estado, ...mudancas, modo: ESTADOS.CARREGANDO_LISTA, ocupada: true, falha: null };
    publicar();
    try {
      const resposta = await api.listar(consultaAtual());
      const registros = resposta.registros ?? [];
      const idAtual = estado.selecionado?.id_manutencao ?? estado.selecionado?.id;
      const tituloExato = estado.busca.trim().toLocaleLowerCase("pt-BR");
      const selecionado = registros.find((item) =>
        tituloExato && item.titulo?.toLocaleLowerCase("pt-BR") === tituloExato
      ) ?? registros.find((item) =>
        (item.id_manutencao ?? item.id) === idAtual
      ) ?? registros[0] ?? null;
      return alterarEstado({
        modo: ESTADOS.CONSULTA, ocupada: false, itens: registros,
        total: resposta.total ?? 0, selecionado,
        mensagem: resposta.mensagem ?? "",
      });
    } catch (falha) {
      return alterarEstado({ modo: ESTADOS.ERRO, ocupada: false, falha, mensagem: falha.message });
    }
  }

  async function listarTitulos() {
    const consulta = { ...consultaAtual(), busca: "", pagina: 1, por_pagina: 100 };
    if (usarOrdenacao) consulta.ordenacao = "TITULO";
    const titulos = [];
    let total = 0;
    do {
      const resposta = await api.listar(consulta);
      const registros = resposta.registros ?? [];
      titulos.push(...registros.map((item) => item.titulo).filter(Boolean));
      total = resposta.total ?? titulos.length;
      consulta.pagina += 1;
      if (registros.length === 0) break;
    } while (titulos.length < total);
    return [...new Set(titulos)].sort((a, b) => a.localeCompare(b, "pt-BR"));
  }

  function novo() {
    return alterarEstado({
      modo: ESTADOS.NOVO, selecionado: null, rascunho: dadosIniciais(campos),
      origemRascunho: dadosIniciais(campos), erros: {}, mensagem: "", falha: null,
    });
  }

  function consultar(registro) {
    return alterarEstado({
      modo: ESTADOS.CONSULTA, selecionado: copiar(registro), rascunho: null,
      origemRascunho: null, erros: {}, mensagem: "",
    });
  }

  function editar() {
    if (!estado.selecionado) throw new Error("Selecione um registro antes de editar.");
    const rascunho = Object.fromEntries(campos.map(({ nome }) => [nome, copiar(estado.selecionado[nome] ?? "")]));
    return alterarEstado({
      modo: ESTADOS.EDICAO, rascunho, origemRascunho: copiar(rascunho),
      erros: {}, mensagem: "",
    });
  }

  function alterarCampo(nome, valor) {
    if (![ESTADOS.NOVO, ESTADOS.EDICAO].includes(estado.modo)) return publicar();
    if (!campos.some((campo) => campo.nome === nome)) throw new Error(`Campo desconhecido: ${nome}.`);
    const erros = { ...estado.erros };
    delete erros[nome];
    return alterarEstado({ rascunho: { ...estado.rascunho, [nome]: valor }, erros });
  }

  function possuiAlteracoes() {
    return JSON.stringify(estado.rascunho) !== JSON.stringify(estado.origemRascunho);
  }

  function conferir() {
    if (![ESTADOS.NOVO, ESTADOS.EDICAO].includes(estado.modo)) return publicar();
    return alterarEstado({
      modo: ESTADOS.CONFERENCIA, erros: {},
      mensagem: "Confirme se deseja salvar o registro.",
    });
  }

  function voltarDaConferencia() {
    if (estado.modo !== ESTADOS.CONFERENCIA) return publicar();
    return alterarEstado({ modo: estado.selecionado ? ESTADOS.EDICAO : ESTADOS.NOVO, mensagem: "" });
  }

  async function salvar() {
    if (estado.modo !== ESTADOS.CONFERENCIA || estado.ocupada) return publicar();
    const erros = validarDados(campos, estado.rascunho);
    if (Object.keys(erros).length) {
      return alterarEstado({
        modo: estado.selecionado ? ESTADOS.EDICAO : ESTADOS.NOVO,
        erros, mensagem: "Preencha ou corrija os campos indicados.",
      });
    }
    const criando = estado.selecionado === null;
    alterarEstado({ modo: ESTADOS.SALVANDO, ocupada: true, mensagem: "Salvando…", falha: null });
    try {
      const registro = criando
        ? (await api.criar(copiar(estado.rascunho), await gerarChaveIdempotencia())).registro
        : (await api.atualizar(
            estado.selecionado.id_manutencao ?? estado.selecionado.id,
            copiar(estado.rascunho), estado.selecionado.versao_registro,
          )).registro;
      alterarEstado({
        modo: ESTADOS.CONSULTA, ocupada: false, selecionado: registro,
        rascunho: null, origemRascunho: null, mensagem: criando ? "Registro criado." : "Registro atualizado.",
      });
      await carregar();
      return alterarEstado({ selecionado: registro, mensagem: criando ? "Registro criado." : "Registro atualizado." });
    } catch (falha) {
      return alterarEstado({
        modo: criando ? ESTADOS.NOVO : ESTADOS.EDICAO, ocupada: false,
        falha, mensagem: falha.message || "Não foi possível salvar.",
      });
    }
  }

  function cancelarEdicao({ descartar = false } = {}) {
    if (![ESTADOS.NOVO, ESTADOS.EDICAO].includes(estado.modo)) return true;
    if (possuiAlteracoes() && !descartar) return false;
    alterarEstado({ modo: ESTADOS.CONSULTA, rascunho: null, origemRascunho: null, erros: {}, mensagem: "" });
    return true;
  }

  async function definirArquivamento(arquivar) {
    if (!estado.selecionado || estado.ocupada) return publicar();
    alterarEstado({ ocupada: true, mensagem: arquivar ? "Arquivando…" : "Desarquivando…" });
    try {
      const id = estado.selecionado.id_manutencao ?? estado.selecionado.id;
      const resposta = arquivar
        ? await api.arquivar(id, estado.selecionado.versao_registro)
        : await api.desarquivar(id, estado.selecionado.versao_registro);
      alterarEstado({ ocupada: false, selecionado: resposta.registro, mensagem: arquivar ? "Registro arquivado." : "Registro desarquivado." });
      await carregar();
      return alterarEstado({ selecionado: resposta.registro });
    } catch (falha) {
      return alterarEstado({ ocupada: false, falha, mensagem: falha.message });
    }
  }

  return {
    carregar, novo, consultar, editar, alterarCampo, conferir, voltarDaConferencia,
    salvar, cancelarEdicao, definirArquivamento, possuiAlteracoes, listarTitulos,
    observar(ouvinte) { ouvintes.add(ouvinte); ouvinte(copiar(estado)); return () => ouvintes.delete(ouvinte); },
    obterEstado: () => copiar(estado),
    pesquisar(busca) { return carregar({ busca, pagina: 1 }); },
    filtrar(filtros) { return carregar({ filtros: { ...filtros }, pagina: 1 }); },
    ordenar(ordenacao) { return carregar({ ordenacao, pagina: 1 }); },
    paginar(pagina) { return carregar({ pagina }); },
    mostrarArquivados(arquivados) { return carregar({ arquivados, pagina: 1 }); },
  };
}

function escapar(valor) {
  return String(valor ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

function controleCampo(campo, valor, erro, protegido, prefixo) {
  const id = `${prefixo}-${campo.nome}`;
  const largura = ["curta", "media", "larga", "total"].includes(campo.largura)
    ? campo.largura : "total";
  const comum = `id="${id}" name="${campo.nome}" ${protegido ? "disabled" : ""} ${campo.obrigatorio ? "required" : ""} ${erro ? 'aria-invalid="true"' : ""}`;
  let controle;
  if (campo.tipo === "select") {
    controle = `<select ${comum}>${(campo.opcoes ?? []).map((opcao) => {
      const item = typeof opcao === "string" ? { valor: opcao, rotulo: opcao } : opcao;
      return `<option value="${escapar(item.valor)}" ${item.valor === valor ? "selected" : ""}>${escapar(item.rotulo)}</option>`;
    }).join("")}</select>`;
  } else if (campo.tipo === "texto-longo") {
    controle = `<textarea ${comum} rows="${campo.linhas ?? 5}">${escapar(valor)}</textarea>`;
  } else {
    const tipo = campo.tipo === "numero" ? "number" : campo.tipo === "data" ? "date" : "text";
    controle = `<input ${comum} type="${tipo}" value="${escapar(valor)}">`;
  }
  return `<label class="crud-navegavel__campo crud-navegavel__campo--${largura}" data-campo="${escapar(campo.nome)}" for="${id}"><span>${escapar(campo.rotulo)}</span>${controle}<small role="alert">${escapar(erro)}</small></label>`;
}

export function criarCrudNavegavel(configuracao) {
  const {
    raiz, titulo, descricao = "", campos, colunas = [], api, filtros = [],
    usarOrdenacao = true,
    ordenacoes = [
      { valor: "ATUALIZACAO", rotulo: "Atualização mais recente" },
      { valor: "PRIORIDADE", rotulo: "Prioridade" },
      { valor: "TITULO", rotulo: "Título" },
      { valor: "CRIACAO", rotulo: "Criação mais recente" },
    ],
  } = configuracao;
  if (!(raiz instanceof Element)) throw new TypeError("raiz deve ser um elemento da página.");
  const controlador = criarControladorCrud(configuracao);
  const prefixoCampos = `crud-${crypto.randomUUID()}`;
  const idTituloConfirmacao = `${prefixoCampos}-confirmacao-titulo`;
  const idTitulos = `${prefixoCampos}-titulos`;
  raiz.classList.add("crud-navegavel");
  raiz.innerHTML = `
    <header class="crud-navegavel__cabecalho"><div><h1>${escapar(titulo)}</h1><p>${escapar(descricao)}</p></div><button data-acao="novo" type="button">Novo registro</button></header>
    <section class="crud-navegavel__consulta" aria-label="Localização e filtros"><label class="crud-navegavel__localizar">Localizar<input data-pesquisa type="search" list="${idTitulos}" autocomplete="off" placeholder="Selecione ou digite parte do título"><datalist id="${idTitulos}" data-titulos></datalist></label><div data-filtros>${filtros.map((filtro) => `<label>${escapar(filtro.rotulo)}<select data-filtro="${escapar(filtro.nome)}"><option value="">Todos</option>${filtro.opcoes.map((opcao) => { const item = typeof opcao === "string" ? { valor: opcao, rotulo: opcao } : opcao; return `<option value="${escapar(item.valor)}">${escapar(item.rotulo)}</option>`; }).join("")}</select></label>`).join("")}${usarOrdenacao ? `<label>Ordenar por<select data-ordenacao>${ordenacoes.map((item) => `<option value="${escapar(item.valor)}">${escapar(item.rotulo)}</option>`).join("")}</select></label>` : ""}<label class="crud-navegavel__arquivados"><input data-arquivados type="checkbox"> Consultar arquivados</label></div></section>
    <p class="crud-navegavel__mensagem" aria-live="polite"></p>
    <div class="crud-navegavel__corpo"><section><table><thead><tr>${colunas.map((item) => `<th>${escapar(item.rotulo)}</th>`).join("")}</tr></thead><tbody data-lista></tbody></table><nav data-paginacao aria-label="Paginação"></nav></section><section data-formulario></section></div>
    <dialog data-confirmar-arquivamento><h2>Confirmar arquivamento</h2><p>O registro continuará preservado e poderá ser desarquivado.</p><div class="crud-navegavel__acoes"><button data-acao="cancelar-arquivamento" type="button">Cancelar</button><button data-acao="confirmar-arquivamento" type="button">Confirmar arquivamento</button></div></dialog>
    <dialog data-confirmacao aria-labelledby="${idTituloConfirmacao}"><h2 id="${idTituloConfirmacao}">Confirmar gravação</h2><p>Deseja salvar este registro?</p><div data-resumo></div><p>Nenhum dado será gravado antes da confirmação.</p><div><button data-acao="voltar" type="button">Cancelar</button><button data-acao="confirmar" type="button">Sim, salvar registro</button></div></dialog>
    <dialog data-descarte><h2>Descartar alterações?</h2><p>As alterações não salvas serão perdidas.</p><button data-acao="continuar" type="button">Continuar editando</button><button data-acao="descartar" type="button">Descartar alterações</button></dialog>`;

  const lista = raiz.querySelector("[data-lista]");
  const formulario = raiz.querySelector("[data-formulario]");
  const mensagem = raiz.querySelector("[aria-live]");
  const paginacao = raiz.querySelector("[data-paginacao]");
  const confirmacao = raiz.querySelector("[data-confirmacao]");
  const descarte = raiz.querySelector("[data-descarte]");
  const confirmarArquivamento = raiz.querySelector("[data-confirmar-arquivamento]");
  const pesquisa = raiz.querySelector("[data-pesquisa]");
  const listaTitulos = raiz.querySelector("[data-titulos]");
  let atrasoPesquisa = null;
  let identidadeFormularioAnterior = null;

  async function atualizarTitulos() {
    try {
      const titulos = await controlador.listarTitulos();
      listaTitulos.replaceChildren(...titulos.map((titulo) => {
        const opcao = document.createElement("option");
        opcao.value = titulo;
        return opcao;
      }));
    } catch (_erro) {
      listaTitulos.replaceChildren();
    }
  }

  function renderizar(estado) {
    mensagem.textContent = estado.mensagem;
    lista.innerHTML = estado.itens.length ? estado.itens.map((item, indice) => `<tr>${colunas.map((coluna, colunaIndice) => `<td>${colunaIndice === 0 ? `<button type="button" data-item="${indice}">${escapar(item[coluna.campo])}</button>` : escapar(item[coluna.campo])}</td>`).join("")}</tr>`).join("") : `<tr><td colspan="${Math.max(1, colunas.length)}">Nenhum registro encontrado.</td></tr>`;
    const paginas = Math.max(1, Math.ceil(estado.total / estado.porPagina));
    paginacao.innerHTML = `<button type="button" data-pagina="${estado.pagina - 1}" ${estado.pagina <= 1 ? "disabled" : ""}>Anterior</button><span>Página ${estado.pagina} de ${paginas} · ${estado.total} registro(s)</span><button type="button" data-pagina="${estado.pagina + 1}" ${estado.pagina >= paginas ? "disabled" : ""}>Próxima</button>`;
    const editando = [ESTADOS.NOVO, ESTADOS.EDICAO].includes(estado.modo);
    const dados = editando ? estado.rascunho : estado.selecionado;
    const identidadeFormulario = [
      estado.modo,
      estado.selecionado?.id_manutencao ?? estado.selecionado?.id ?? "novo",
      estado.selecionado?.versao_registro ?? "",
    ].join(":");
    if (identidadeFormulario !== identidadeFormularioAnterior) {
      identidadeFormularioAnterior = identidadeFormulario;
      if (!dados) {
        formulario.innerHTML = "<p>Selecione um registro ou escolha Novo registro.</p>";
      } else {
        const acaoArquivo = dados.arquivado_em ? '<button data-acao="desarquivar" type="button">Desarquivar</button>' : '<button data-acao="arquivar" type="button">Arquivar</button>';
        formulario.innerHTML = `<form><fieldset ${editando ? "" : "disabled"}>${campos.map((campo) => controleCampo(campo, dados[campo.nome], estado.erros[campo.nome], !editando, prefixoCampos)).join("")}</fieldset><div class="crud-navegavel__acoes">${editando ? '<button data-acao="cancelar" type="button">Cancelar</button><button data-acao="conferir" type="button">Salvar registro</button>' : `<button data-acao="editar" type="button">Editar</button>${acaoArquivo}`}</div></form>`;
      }
    }
    if (estado.modo === ESTADOS.CONFERENCIA && !confirmacao.open) {
      confirmacao.querySelector("[data-resumo]").innerHTML = campos.map((campo) => `<p><strong>${escapar(campo.rotulo)}:</strong> ${escapar(estado.rascunho[campo.nome])}</p>`).join("");
      confirmacao.showModal();
    }
    raiz.querySelector("[data-acao='novo']").disabled = estado.ocupada;
    formulario.querySelectorAll("button").forEach((botao) => { botao.disabled = estado.ocupada; });
    confirmacao.querySelectorAll("button").forEach((botao) => { botao.disabled = estado.ocupada; });
    confirmarArquivamento.querySelectorAll("button").forEach((botao) => { botao.disabled = estado.ocupada; });
  }

  raiz.addEventListener("input", (evento) => {
    if (evento.target.matches("[data-pesquisa]")) {
      clearTimeout(atrasoPesquisa);
      atrasoPesquisa = setTimeout(() => controlador.pesquisar(evento.target.value), 250);
      return;
    }
    if (evento.target.name) {
      evento.target.removeAttribute("aria-invalid");
      evento.target.closest("[data-campo]")?.querySelector("small")?.replaceChildren();
      controlador.alterarCampo(evento.target.name, evento.target.value);
    }
  });
  raiz.addEventListener("change", (evento) => {
    if (evento.target.matches("[data-filtro]")) {
      const valores = Object.fromEntries([...raiz.querySelectorAll("[data-filtro]")].map((item) => [item.dataset.filtro, item.value || null]));
      controlador.carregar({ filtros: valores, pagina: 1 });
      atualizarTitulos();
    } else if (usarOrdenacao && evento.target.matches("[data-ordenacao]")) {
      controlador.carregar({ ordenacao: evento.target.value, pagina: 1 });
    } else if (evento.target.matches("[data-arquivados]")) {
      controlador.mostrarArquivados(evento.target.checked);
      atualizarTitulos();
    } else if (evento.target.name) controlador.alterarCampo(evento.target.name, evento.target.value);
  });
  confirmacao.addEventListener("cancel", (evento) => {
    evento.preventDefault();
    confirmacao.close();
    controlador.voltarDaConferencia();
  });
  raiz.addEventListener("click", async (evento) => {
    const botao = evento.target.closest("button");
    if (!botao) return;
    if (botao.dataset.item != null) controlador.consultar(controlador.obterEstado().itens[Number(botao.dataset.item)]);
    if (botao.dataset.pagina) await controlador.paginar(Number(botao.dataset.pagina));
    const acao = botao.dataset.acao;
    if (acao === "novo") controlador.novo();
    if (acao === "editar") controlador.editar();
    if (acao === "conferir") controlador.conferir();
    if (acao === "voltar") { confirmacao.close(); controlador.voltarDaConferencia(); }
    if (acao === "confirmar") {
      confirmacao.close();
      const resultado = await controlador.salvar();
      if (Object.keys(resultado.erros ?? {}).length) {
        requestAnimationFrame(() => formulario.querySelector('[aria-invalid="true"]')?.focus());
      }
    }
    if (acao === "cancelar" && !controlador.cancelarEdicao()) descarte.showModal();
    if (acao === "continuar") descarte.close();
    if (acao === "descartar") { descarte.close(); controlador.cancelarEdicao({ descartar: true }); }
    if (acao === "arquivar") confirmarArquivamento.showModal();
    if (acao === "desarquivar") await controlador.definirArquivamento(false);
    if (acao === "cancelar-arquivamento") confirmarArquivamento.close();
    if (acao === "confirmar-arquivamento") {
      confirmarArquivamento.close();
      await controlador.definirArquivamento(true);
    }
  });
  pesquisa.addEventListener("search", (evento) => controlador.pesquisar(evento.target.value));
  controlador.observar(renderizar);
  controlador.carregar();
  atualizarTitulos();
  return controlador;
}

export { ESTADOS };
