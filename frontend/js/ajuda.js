import { secoesAjuda, topicosAjuda } from "./ajuda-conteudo.js";

const CHAVE_ULTIMO_TOPICO = "game.ajuda.ultimoTopico.v1";

const ORIGENS_AJUDA = new Map([
  ["/", "o Painel"], ["/index.html", "o Painel"],
  ["/cadastros.html", "Cadastros"], ["/grupos-padroes.html", "Grupos de padrões"],
  ["/padroes.html", "Padrões"], ["/distribuicoes.html", "Distribuições"],
  ["/screener.html", "o Screener"], ["/auditoria.html", "Validação e auditoria"],
  ["/frequencias.html", "Frequência das dezenas"],
  ["/graficos-frequencias.html", "Gráficos de frequência"],
  ["/selecao-dezenas.html", "Seleção de dezenas"],
  ["/gestao-desenvolvimento.html", "Gestão do desenvolvimento"],
]);

export function validarOrigemAjuda(valor, origemBase = "http://localhost") {
  if (!valor) return null;
  try {
    const url = new URL(valor, origemBase);
    const base = new URL(origemBase);
    if (url.origin !== base.origin || !ORIGENS_AJUDA.has(url.pathname)) return null;
    return { href: `${url.pathname}${url.search}${url.hash}`, rotulo: ORIGENS_AJUDA.get(url.pathname) };
  } catch {
    return null;
  }
}

export function normalizarBusca(valor = "") {
  return String(valor)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

function textoPesquisavel(topico) {
  return [
    topico.titulo,
    ...(topico.aliases ?? []),
    topico.resumo,
    ...topico.blocos.flatMap((bloco) => [
      bloco.titulo,
      ...(bloco.paragrafos ?? []),
      ...(bloco.itens ?? []),
      ...(bloco.formulas ?? []),
    ]),
  ].join(" ");
}

export function buscarTopicos(termo, topicos = topicosAjuda) {
  const consulta = normalizarBusca(termo);
  if (!consulta) return [];
  const palavras = consulta.split(/\s+/).filter(Boolean);
  return topicos
    .map((topico) => {
      const titulo = normalizarBusca(topico.titulo);
      const aliases = normalizarBusca((topico.aliases ?? []).join(" "));
      const conteudo = normalizarBusca(textoPesquisavel(topico));
      if (!palavras.every((palavra) => conteudo.includes(palavra))) return null;
      const pontuacao = palavras.reduce((total, palavra) => (
        total + (titulo.includes(palavra) ? 4 : 0) + (aliases.includes(palavra) ? 2 : 0)
      ), 0);
      return { topico, pontuacao };
    })
    .filter(Boolean)
    .sort((a, b) => b.pontuacao - a.pontuacao || a.topico.titulo.localeCompare(b.topico.titulo, "pt-BR"))
    .map(({ topico }) => topico);
}

export function localizarTopico(id, topicos = topicosAjuda) {
  return topicos.find((topico) => topico.id === id) ?? null;
}

function criarElemento(tag, texto, classe) {
  const elemento = document.createElement(tag);
  if (texto) elemento.textContent = texto;
  if (classe) elemento.className = classe;
  return elemento;
}

function lerUltimoTopico() {
  try {
    return localStorage.getItem(CHAVE_ULTIMO_TOPICO);
  } catch {
    return null;
  }
}

function guardarUltimoTopico(id) {
  try {
    localStorage.setItem(CHAVE_ULTIMO_TOPICO, id);
  } catch {
    // A navegação continua funcional quando o armazenamento estiver indisponível.
  }
}

function iniciarAjuda() {
  const arvore = document.querySelector("#ajuda-arvore");
  const artigo = document.querySelector("#ajuda-artigo");
  const campoBusca = document.querySelector("#ajuda-busca");
  const limparBusca = document.querySelector("#ajuda-limpar-busca");
  const resultadosBusca = document.querySelector("#ajuda-resultados-busca");
  const estadoBusca = document.querySelector("#ajuda-estado-busca");
  const aviso = document.querySelector("#ajuda-aviso");
  const voltarOrigem = document.querySelector("#ajuda-voltar-origem");
  let focarAoAbrir = false;

  if (!arvore || !artigo || !campoBusca || !resultadosBusca) return;

  const origem = validarOrigemAjuda(new URLSearchParams(window.location.search).get("origem"), window.location.origin);
  if (origem && voltarOrigem) {
    voltarOrigem.href = origem.href;
    voltarOrigem.textContent = `Voltar para ${origem.rotulo}`;
    voltarOrigem.hidden = false;
  }

  const abrir = (id, { focar = false } = {}) => {
    const topico = localizarTopico(id) ?? topicosAjuda[0];
    if (!topico) return;
    artigo.replaceChildren();

    const cabecalho = criarElemento("header", "", "ajuda-artigo__cabecalho");
    const grupo = criarElemento("div");
    grupo.append(criarElemento("p", topico.secaoTitulo, "ajuda-artigo__secao"));
    const titulo = criarElemento("h2", topico.titulo);
    titulo.id = "ajuda-titulo-topico";
    titulo.tabIndex = -1;
    grupo.append(titulo);
    cabecalho.append(grupo);
    if (topico.estado !== "confirmado") {
      const rotulo = topico.estado === "em-desenvolvimento" ? "Em desenvolvimento" : "Limitação conhecida";
      cabecalho.append(criarElemento("span", rotulo, `ajuda-estado ajuda-estado--${topico.estado}`));
    }
    artigo.append(cabecalho, criarElemento("p", topico.resumo, "ajuda-artigo__resumo"));

    topico.blocos.forEach((bloco) => {
      const secao = criarElemento("section");
      secao.append(criarElemento("h3", bloco.titulo));
      (bloco.paragrafos ?? []).forEach((paragrafo) => secao.append(criarElemento("p", paragrafo)));
      if (bloco.itens?.length) {
        const lista = criarElemento("ul");
        bloco.itens.forEach((texto) => lista.append(criarElemento("li", texto)));
        secao.append(lista);
      }
      (bloco.formulas ?? []).forEach((formula) => secao.append(criarElemento("pre", formula, "ajuda-formula")));
      artigo.append(secao);
    });

    if (topico.relacionados?.length) {
      const relacionados = criarElemento("nav", "", "ajuda-relacionados");
      relacionados.setAttribute("aria-label", "Assuntos relacionados");
      relacionados.append(criarElemento("h3", "Assuntos relacionados"));
      const lista = criarElemento("ul");
      topico.relacionados.forEach((relacionadoId) => {
        const relacionado = localizarTopico(relacionadoId);
        if (!relacionado) return;
        const item = criarElemento("li");
        const link = criarElemento("a", relacionado.titulo);
        link.href = `#${relacionado.id}`;
        item.append(link);
        lista.append(item);
      });
      relacionados.append(lista);
      artigo.append(relacionados);
    }

    arvore.querySelectorAll("a").forEach((link) => {
      const atual = link.getAttribute("href") === `#${topico.id}`;
      if (atual) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    guardarUltimoTopico(topico.id);
    document.title = `${topico.titulo} — Ajuda do Game`;
    aviso.hidden = localizarTopico(id) !== null || !id;
    if (!aviso.hidden) aviso.textContent = "O tópico solicitado não foi encontrado. Foi aberto o início da Ajuda.";
    if (focar) titulo.focus();
  };

  secoesAjuda.forEach((secao) => {
    const grupo = criarElemento("section", "", "ajuda-arvore__grupo");
    grupo.append(criarElemento("h2", secao.titulo));
    const lista = criarElemento("ul");
    secao.topicos.forEach((topico) => {
      const item = criarElemento("li");
      const link = criarElemento("a", topico.titulo);
      link.href = `#${topico.id}`;
      link.addEventListener("click", () => { focarAoAbrir = true; });
      item.append(link);
      lista.append(item);
    });
    grupo.append(lista);
    arvore.append(grupo);
  });

  const atualizarBusca = () => {
    const termo = campoBusca.value.trim();
    resultadosBusca.replaceChildren();
    limparBusca.hidden = !termo;
    if (!termo) {
      resultadosBusca.hidden = true;
      arvore.hidden = false;
      estadoBusca.textContent = "";
      return;
    }
    const resultados = buscarTopicos(termo);
    arvore.hidden = true;
    resultadosBusca.hidden = false;
    estadoBusca.textContent = `${resultados.length} ${resultados.length === 1 ? "assunto encontrado" : "assuntos encontrados"}.`;
    if (!resultados.length) {
      resultadosBusca.append(criarElemento("p", "Nenhum assunto contém os termos informados.", "ajuda-busca-vazia"));
      return;
    }
    resultados.forEach((topico) => {
      const link = criarElemento("a", "", "ajuda-resultado");
      link.href = `#${topico.id}`;
      link.append(
        criarElemento("strong", topico.titulo),
        criarElemento("span", topico.secaoTitulo),
        criarElemento("p", topico.resumo),
      );
      link.addEventListener("click", () => { focarAoAbrir = true; });
      resultadosBusca.append(link);
    });
  };

  campoBusca.addEventListener("input", atualizarBusca);
  campoBusca.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape" && campoBusca.value) {
      campoBusca.value = "";
      atualizarBusca();
    }
  });
  limparBusca.addEventListener("click", () => {
    campoBusca.value = "";
    atualizarBusca();
    campoBusca.focus();
  });
  window.addEventListener("hashchange", () => {
    const id = decodeURIComponent(window.location.hash.slice(1));
    abrir(id, { focar: focarAoAbrir });
    focarAoAbrir = false;
  });

  const idInicial = decodeURIComponent(window.location.hash.slice(1)) || lerUltimoTopico() || topicosAjuda[0]?.id;
  abrir(idInicial);
  if (!window.location.hash && idInicial) history.replaceState(null, "", `#${idInicial}`);
}

if (typeof document !== "undefined") iniciarAjuda();
