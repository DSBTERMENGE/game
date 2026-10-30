import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test, { before } from "node:test";


const geometria = { tamanhoCelula: 40 };
const eventosJanela = {};
const relogio = { proximoId: 1, tarefas: new Map() };

class ElementoFalso {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.listeners = {};
    this.textContent = "";
    this.value = "";
    this.disabled = false;
    this.files = [];
    this.checked = false;
    this.open = false;
    this.style = { valores: {}, setProperty: (nome, valor) => { this.style.valores[nome] = valor; } };
    this.clientWidth = tag === "mapa" ? 400 : 40;
    this.clientHeight = tag === "mapa" ? 240 : 40;
  }

  append(...filhos) {
    filhos.forEach((filho) => {
      if (filho?.fragmento) this.children.push(...filho.children);
      else this.children.push(filho);
    });
  }

  replaceChildren(...filhos) {
    this.children = [];
    this.append(...filhos);
  }

  setAttribute(nome, valor) {
    this.attributes[nome] = String(valor);
  }

  addEventListener(tipo, funcao) {
    this.listeners[tipo] = funcao;
  }

  disparar(tipo) {
    if (!this.disabled) this.listeners[tipo]?.({ target: this, preventDefault() {} });
  }

  click() {
    this.disparar("click");
  }

  showModal() { this.open = true; }

  close() { this.open = false; }

  getBoundingClientRect() {
    if (this.id?.startsWith("dezena-")) {
      const numero = Number(this.id.slice(-2));
      const tamanho = geometria.tamanhoCelula;
      return {
        left: ((numero - 1) % 10) * tamanho,
        top: Math.floor((numero - 1) / 10) * tamanho,
        width: tamanho,
        height: tamanho,
      };
    }
    return { left: 0, top: 0, width: this.clientWidth, height: this.clientHeight };
  }
}


function localizar(raizes, seletor) {
  const todos = [];
  const visitar = (elemento) => {
    todos.push(elemento);
    elemento.children?.forEach(visitar);
  };
  raizes.forEach(visitar);
  if (seletor.startsWith("#")) return todos.find((item) => item.id === seletor.slice(1)) ?? null;
  if (seletor.startsWith(".")) {
    return todos.find((item) => item.className?.split(" ").includes(seletor.slice(1))) ?? null;
  }
  return null;
}


const ids = [
  "grade-dezenas", "mapa-dezenas", "camada-marcas", "jogo-numero",
  "coordenada-media", "resumo-geometrico", "mensagem-sistema", "arquivo-excel", "nome-arquivo",
  "botao-selecionar-excel", "botao-importar-excel", "seletor-resultado",
  "botao-anterior", "botao-proximo", "tempo-voo", "botao-voo",
  "botao-mancha", "botao-aparencia", "botao-limpar", "dialogo-aparencia",
  "form-aparencia", "botao-fechar-aparencia", "botao-restaurar-aparencia",
  "cor-linha", "cor-fechamento", "cor-vertices", "cor-resultado", "cor-media",
  "cor-centro-gravidade", "cor-regioes", "espessura-linhas", "diametro-vertices",
  "opacidade-regioes", "mostrar-linha", "mostrar-fechamento", "mostrar-vertices",
  "mostrar-resultado", "mostrar-media", "mostrar-centro-gravidade", "mostrar-regioes",
];
const elementos = Object.fromEntries(ids.map((id) => {
  const tag = id === "mapa-dezenas" ? "mapa" : "div";
  const elemento = new ElementoFalso(tag);
  elemento.id = id;
  return [id, elemento];
}));
elementos["tempo-voo"].value = "0.5";

globalThis.document = {
  querySelector: (seletor) => localizar(Object.values(elementos), seletor),
  createElement: (tag) => new ElementoFalso(tag),
  createElementNS: (_ns, tag) => new ElementoFalso(tag),
  createDocumentFragment: () => Object.assign(new ElementoFalso("fragment"), { fragmento: true }),
};
globalThis.Option = class extends ElementoFalso {
  constructor(texto, valor) {
    super("option");
    this.textContent = texto;
    this.value = valor;
  }
};
globalThis.window = {
  addEventListener(tipo, funcao) {
    eventosJanela[tipo] = funcao;
  },
  clearTimeout(id) {
    relogio.tarefas.delete(id);
  },
  setTimeout(funcao, atraso) {
    const id = relogio.proximoId;
    relogio.proximoId += 1;
    relogio.tarefas.set(id, { funcao, atraso });
    return id;
  },
};
const armazenamento = new Map();
globalThis.localStorage = {
  getItem: (chave) => armazenamento.get(chave) ?? null,
  setItem: (chave, valor) => armazenamento.set(chave, valor),
  clear: () => armazenamento.clear(),
};
globalThis.fetch = async () => ({
  ok: true,
  json: async () => ({ resultados: [] }),
});

const resultado = (numero) => ({
  numero_ap: numero,
  data_resultado: `2026-10-${String(numero).padStart(2, "0")}`,
  dezenas: [1, 10, 20, 30, 40, 60],
});

const circulos = (classe) => elementos["camada-marcas"].children.filter(
  (elemento) => elemento.attributes.class === classe,
);
const marcas = (classe) => elementos["camada-marcas"].children.filter(
  (elemento) => elemento.attributes.class === classe,
);
const coordenadas = (elemento) => ({
  x: Number(elemento.attributes.cx),
  y: Number(elemento.attributes.cy),
});

function redimensionarCelulas(tamanho) {
  geometria.tamanhoCelula = tamanho;
  elementos["mapa-dezenas"].clientWidth = tamanho * 10;
  elementos["mapa-dezenas"].clientHeight = tamanho * 6;
  elementos["grade-dezenas"].children.forEach((celula) => {
    celula.clientWidth = tamanho;
    celula.clientHeight = tamanho;
  });
}

function limparRelogio() {
  relogio.tarefas.clear();
}

function unicaTarefa() {
  assert.equal(relogio.tarefas.size, 1);
  return [...relogio.tarefas.entries()][0];
}

function executarProximaTarefa() {
  const [id, tarefa] = unicaTarefa();
  relogio.tarefas.delete(id);
  tarefa.funcao();
  return tarefa.atraso;
}

before(async () => {
  await import("../js/main.js");
  await new Promise((resolver) => setImmediate(resolver));
});

test("HTML possui controles necessários e aceita somente XLSX", async () => {
  const html = await readFile(new URL("../index.html", import.meta.url), "utf8");
  for (const id of ids) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /id="arquivo-excel"[^>]+accept="\.xlsx"/);
});

test("navegação separa Painel e Cadastros em uma barra compacta", async () => {
  const paginas = await Promise.all([
    "index.html", "cadastros.html", "grupos-padroes.html", "padroes.html",
    "distribuicoes.html", "screener.html", "auditoria.html", "frequencias.html",
  ].map((arquivo) => readFile(new URL(`../${arquivo}`, import.meta.url), "utf8")));
  const css = await readFile(new URL("../css/navegacao.css", import.meta.url), "utf8");
  const javascript = await readFile(new URL("../js/navegacao.js", import.meta.url), "utf8");

  for (const html of paginas) {
    assert.match(html, /class="barra-navegacao"/);
    assert.match(html, /id="botao-voltar"/);
    assert.match(html, /href="\/"[^>]*>Painel</);
    assert.match(html, /<summary>Cadastros<\/summary>/);
    assert.match(html, /href="\/grupos-padroes\.html"/);
    assert.match(html, /href="\/padroes\.html"/);
    assert.match(html, /href="\/auditoria\.html"[^>]*>Validação e auditoria</);
    assert.match(html, /href="\/frequencias\.html"[^>]*>Frequência das dezenas</);
    assert.match(html, /js\/navegacao\.js/);
  }
  assert.doesNotMatch(paginas[0], /painel-padroes|botao-cadastro-padroes/);
  assert.match(css, /\.barra-navegacao\s*\{[^}]*min-height:\s*2\.8rem/s);
  assert.match(css, /\.navegacao-menu nav\s*\{[^}]*position:\s*absolute/s);
  assert.match(css, /\.pagina-conteudo\s*\{[^}]*height:\s*calc\(100vh - 2\.8rem\)/s);
  assert.match(javascript, /window\.history\.back/);
});

test("página de auditoria mantém estrutura compacta e expõe validação", async () => {
  const html = await readFile(new URL("../auditoria.html", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/auditoria.css", import.meta.url), "utf8");
  assert.match(html, /<h1>Validação e auditoria<\/h1>/);
  assert.match(html, /id="estado-algoritmo"/);
  assert.match(html, /id="botao-atualizar-validacao"/);
  assert.match(html, /id="filtros-auditoria"/);
  assert.match(html, /id="corpo-avaliacoes"/);
  assert.match(html, /data-destino-voltar="\/screener\.html"/);
  assert.doesNotMatch(html, /<input/i);
  assert.match(css, /grid-template-rows:\s*auto auto auto auto minmax\(0,\s*1fr\)/);
});

test("cadastro de grupos usa grade compacta e arquivos separados", async () => {
  const html = await readFile(new URL("../grupos-padroes.html", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/grupos-padroes.css", import.meta.url), "utf8");
  const javascript = await readFile(new URL("../js/grupos-padroes.js", import.meta.url), "utf8");

  for (const id of [
    "form-novo-grupo", "novo-grupo-nome", "novo-grupo-descr",
    "mensagem-grupos", "tabela-grupos", "corpo-tabela-grupos",
  ]) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /css\/grupos-padroes\.css/);
  assert.match(html, /js\/grupos-padroes\.js/);
  assert.match(css, /\.pagina-grupos\s*\{[^}]*grid-template-rows:\s*auto auto minmax\(0, 1fr\)/s);
  assert.match(css, /\.grupos-grade\s*\{[^}]*overflow:\s*auto/s);
  assert.match(css, /#tabela-grupos th\s*\{[^}]*position:\s*sticky/s);
  assert.match(javascript, /method:\s*"POST"/);
  assert.match(javascript, /method:\s*"PUT"/);
  assert.match(javascript, /method:\s*"DELETE"/);
  assert.match(javascript, /window\.confirm/);
});

test("cadastro de padrões usa grupo obrigatório e grade compacta", async () => {
  const html = await readFile(new URL("../padroes.html", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/padroes.css", import.meta.url), "utf8");
  const javascript = await readFile(new URL("../js/padroes.js", import.meta.url), "utf8");
  for (const id of [
    "form-novo-padrao", "novo-padrao-grupo", "novo-padrao-nome",
    "novo-padrao-descr", "filtro-grupo", "mensagem-padroes",
    "tabela-padroes", "corpo-tabela-padroes", "perfil-padroes",
    "form-perfil", "perfil-limite", "perfil-tipo-corte",
    "perfil-indicadores", "tabela-perfil", "corpo-tabela-perfil",
  ]) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(css, /\.pagina-padroes\s*\{[^}]*grid-template-rows:\s*auto auto minmax\(0, 1fr\)/s);
  assert.match(css, /\.padroes-grade\s*\{[^}]*overflow:\s*auto/s);
  assert.match(css, /#tabela-padroes th\s*\{[^}]*position:\s*sticky/s);
  assert.match(css, /#tabela-padroes th:nth-child\(5\)\s*\{\s*width:\s*5\.5rem/);
  assert.match(css, /#tabela-padroes input,[^{]+\{[^}]*height:\s*4\.75rem/s);
  assert.match(css, /#tabela-padroes th:nth-child\(2\)\s*\{\s*width:\s*20rem/);
  assert.match(css, /#tabela-padroes th:nth-child\(3\)\s*\{\s*width:\s*22rem/);
  assert.match(css, /\.perfil-padroes__painel\s*\{[^}]*position:\s*absolute/s);
  assert.match(css, /\.perfil-padroes__grade\s*\{[^}]*overflow:\s*auto/s);
  assert.match(javascript, /criarCampo\("textarea", padrao\.padrao_nome/);
  assert.match(javascript, /grupo_cod:\s*grupoNovo\.value/);
  assert.match(javascript, /grupo_cod:\s*grupo\.value/);
  assert.match(javascript, /encodeURIComponent\(filtroGrupo\.value\)/);
  assert.match(javascript, /api\/grupos-padroes\/PG_001\/perfil/i);
  assert.match(javascript, /ativa_no_screener|screener inativo/i);
});

test("nenhum resultado mantém navegação desabilitada e informa o estado", () => {
  window.gameAnalysis.definirResultados([]);

  assert.equal(elementos["seletor-resultado"].disabled, true);
  assert.equal(elementos["botao-anterior"].disabled, true);
  assert.equal(elementos["botao-proximo"].disabled, true);
  assert.equal(elementos["botao-voo"].disabled, true);
  assert.equal(elementos["botao-mancha"].disabled, true);
  assert.equal(elementos["seletor-resultado"].children.length, 1);
  assert.equal(elementos["mensagem-sistema"].textContent, "Nenhum resultado foi carregado.");
});

test("um resultado é selecionado e não oferece avanço sem efeito", () => {
  window.gameAnalysis.definirResultados([resultado(1)]);

  assert.equal(elementos["jogo-numero"].textContent, 1);
  assert.equal(elementos["seletor-resultado"].value, "0");
  assert.equal(elementos["seletor-resultado"].disabled, false);
  assert.equal(elementos["botao-anterior"].disabled, true);
  assert.equal(elementos["botao-proximo"].disabled, true);
  assert.equal(elementos["botao-voo"].disabled, true);
  assert.equal(elementos["botao-mancha"].disabled, false);
  assert.equal(elementos["mensagem-sistema"].textContent, "1 resultado carregado.");
});

test("seleção direta exibe o resultado escolhido", () => {
  window.gameAnalysis.definirResultados([resultado(1), resultado(2), resultado(3)]);
  elementos["seletor-resultado"].value = "1";
  elementos["seletor-resultado"].disparar("change");

  assert.equal(elementos["jogo-numero"].textContent, 2);
  assert.equal(elementos["seletor-resultado"].value, "1");
});

test("anterior no primeiro vai ao último e próximo no último volta ao primeiro", () => {
  window.gameAnalysis.definirResultados([resultado(1), resultado(2), resultado(3)]);
  assert.equal(elementos["botao-anterior"].disabled, false);
  assert.equal(elementos["botao-proximo"].disabled, false);

  elementos["botao-anterior"].click();
  assert.equal(elementos["jogo-numero"].textContent, 3);
  assert.equal(elementos["seletor-resultado"].value, "2");

  elementos["botao-proximo"].click();
  assert.equal(elementos["jogo-numero"].textContent, 1);
  assert.equal(elementos["seletor-resultado"].value, "0");
});

test("desenha seis marcas nos centros, incluindo 01, 10, 51 e 60", () => {
  redimensionarCelulas(40);
  window.gameAnalysis.desenharResultado({
    numero_ap: 100,
    dezenas: [1, 10, 51, 60, 22, 39],
  });

  const marcas = circulos("marca-resultado");
  assert.equal(marcas.length, 6);
  assert.deepEqual(coordenadas(marcas[0]), { x: 20, y: 20 });
  assert.deepEqual(coordenadas(marcas[1]), { x: 380, y: 20 });
  assert.deepEqual(coordenadas(marcas[2]), { x: 20, y: 220 });
  assert.deepEqual(coordenadas(marcas[3]), { x: 380, y: 220 });
});

test("posiciona uma média inteira exatamente no centro correspondente", () => {
  redimensionarCelulas(40);
  const media = window.gameAnalysis.desenharResultado({
    numero_ap: 101,
    dezenas: [1, 3, 11, 13, 21, 23],
  });

  assert.deepEqual(media, { x: 1, y: 1 });
  assert.equal(circulos("marca-media").length, 1);
  assert.deepEqual(coordenadas(circulos("marca-media")[0]), { x: 60, y: 60 });
  assert.equal(elementos["coordenada-media"].textContent, "Média espacial: (1.00; 1.00)");
});

test("desenha percurso, fechamento, regiões e centro de gravidade", () => {
  window.gameAnalysis.desenharResultado({
    numero_ap: 1,
    dezenas: [1, 2, 3, 10, 11, 20],
    analise_geometrica: {
      vertices: [
        { x: "0", y: "0" }, { x: "1", y: "0" }, { x: "2", y: "0" },
        { x: "9", y: "0" }, { x: "0", y: "1" }, { x: "9", y: "1" },
      ],
      regioes: [
        [{ x: "0", y: "0" }, { x: "9", y: "0" }, { x: "4.5", y: "0.5" }],
        [{ x: "0", y: "1" }, { x: "4.5", y: "0.5" }, { x: "9", y: "1" }],
      ],
      quantidade_regioes: 2,
      extensao_aberta: "27.055385",
      perimetro_fechado: "36.110770",
      area_total: "4.5",
      centro_gravidade: { x: "4.5", y: "0.5" },
    },
  });

  assert.equal(marcas("linha-geometrica").length, 1);
  assert.equal(marcas("fechamento-geometrico").length, 1);
  assert.equal(marcas("regiao-geometrica").length, 2);
  assert.equal(marcas("vertice-geometrico").length, 6);
  assert.deepEqual(coordenadas(marcas("centro-gravidade")[0]), { x: 200, y: 40 });
  assert.match(elementos["resumo-geometrico"].textContent, /Área: 4,500 \| Regiões: 2/);
});

test("salva configuração visual, reaplica e restaura os padrões", () => {
  elementos["botao-aparencia"].click();
  assert.equal(elementos["dialogo-aparencia"].open, true);
  elementos["cor-linha"].value = "#123456";
  elementos["espessura-linhas"].value = "1.5";
  elementos["mostrar-linha"].checked = false;
  elementos["form-aparencia"].disparar("submit");

  assert.equal(elementos["dialogo-aparencia"].open, false);
  assert.equal(elementos["mapa-dezenas"].style.valores["--cor-linha-geometrica"], "#123456");
  assert.equal(elementos["mapa-dezenas"].style.valores["--espessura-linhas"], "1.5mm");
  assert.match(localStorage.getItem("msen.configuracaoVisual.v1"), /"mostrarLinha":false/);
  window.gameAnalysis.desenharResultado(resultado(1));
  assert.equal(marcas("linha-geometrica").length, 0);

  elementos["botao-aparencia"].click();
  elementos["botao-restaurar-aparencia"].click();
  elementos["form-aparencia"].disparar("submit");
  assert.equal(elementos["mapa-dezenas"].style.valores["--cor-linha-geometrica"], "#25834f");
});

test("preserva a posição decimal conhecida 2 por 4,33", () => {
  redimensionarCelulas(40);
  const media = window.gameAnalysis.desenharResultado({
    numero_ap: 102,
    dezenas: [41, 42, 43, 44, 53, 55],
  });
  const marca = coordenadas(circulos("marca-media")[0]);

  assert.equal(media.x, 2);
  assert.ok(Math.abs(media.y - 4.333333333333333) < 1e-12);
  assert.equal(marca.x, 100);
  assert.ok(Math.abs(marca.y - 193.33333333333331) < 1e-10);
  assert.equal(elementos["coordenada-media"].textContent, "Média espacial: (2.00; 4.33)");
});

test("mantém dezenas legíveis sob marcas sem capturar eventos", async () => {
  window.gameAnalysis.desenharResultado({
    numero_ap: 103,
    dezenas: [1, 10, 20, 30, 40, 60],
  });
  const css = await readFile(new URL("../css/style.css", import.meta.url), "utf8");

  assert.equal(elementos["grade-dezenas"].children[0].textContent, "01");
  assert.equal(elementos["grade-dezenas"].children[59].textContent, "60");
  assert.match(css, /\.mapa__marcas\s*\{[^}]*pointer-events:\s*none/s);
  assert.match(css, /\.marca-resultado\s*\{[^}]*fill-opacity:\s*0\.5/s);
});

test("redimensionamento recalcula as marcas e a viewBox", () => {
  redimensionarCelulas(40);
  window.gameAnalysis.definirResultados([{
    numero_ap: 104,
    dezenas: [41, 42, 43, 44, 53, 55],
  }]);
  assert.deepEqual(coordenadas(circulos("marca-media")[0]), {
    x: 100,
    y: 193.33333333333331,
  });

  redimensionarCelulas(50);
  eventosJanela.resize();
  const reposicionada = coordenadas(circulos("marca-media")[0]);

  assert.equal(reposicionada.x, 125);
  assert.ok(Math.abs(reposicionada.y - 241.66666666666666) < 1e-10);
  assert.equal(elementos["camada-marcas"].attributes.viewBox, "0 0 500 300");
});

test("voo usa intervalo padrão de 0,5 segundo e avança em ordem", () => {
  limparRelogio();
  elementos["tempo-voo"].value = "0.5";
  window.gameAnalysis.definirResultados([resultado(1), resultado(2), resultado(3)]);

  elementos["botao-voo"].click();
  const [, tarefaInicial] = unicaTarefa();
  assert.equal(tarefaInicial.atraso, 500);
  assert.equal(elementos["jogo-numero"].textContent, 1);
  assert.equal(elementos["botao-voo"].textContent, "Pausar voo dos pássaros");
  assert.equal(elementos["mensagem-sistema"].textContent, "Voo dos pássaros iniciado.");

  assert.equal(executarProximaTarefa(), 500);
  assert.equal(elementos["jogo-numero"].textContent, 2);
  assert.equal(executarProximaTarefa(), 500);
  assert.equal(elementos["jogo-numero"].textContent, 3);
});

test("pausa cancela o temporizador sem deixar tarefa órfã", () => {
  elementos["botao-voo"].click();

  assert.equal(relogio.tarefas.size, 0);
  assert.equal(elementos["botao-voo"].textContent, "Iniciar voo dos pássaros");
  assert.equal(elementos["mensagem-sistema"].textContent, "Voo interrompido.");
});

test("alteração do tempo passa a valer no passo seguinte", () => {
  limparRelogio();
  elementos["tempo-voo"].value = "0.5";
  window.gameAnalysis.definirResultados([resultado(1), resultado(2)]);
  elementos["botao-voo"].click();
  assert.equal(unicaTarefa()[1].atraso, 500);

  elementos["tempo-voo"].value = "1.2";
  executarProximaTarefa();
  assert.equal(unicaTarefa()[1].atraso, 1200);

  elementos["botao-voo"].click();
  assert.equal(relogio.tarefas.size, 0);
});

test("tempo fora de 0,1 a 30 segundos não inicia o voo", () => {
  for (const valor of ["0", "30.1", "texto"]) {
    limparRelogio();
    elementos["tempo-voo"].value = valor;
    window.gameAnalysis.definirResultados([resultado(1), resultado(2)]);
    elementos["botao-voo"].click();

    assert.equal(relogio.tarefas.size, 0);
    assert.equal(elementos["botao-voo"].textContent, "Iniciar voo dos pássaros");
    assert.equal(elementos["mensagem-sistema"].dataset.tipo, "erro");
  }
});

test("redimensionamento durante o voo redesenha sem perder o temporizador", () => {
  limparRelogio();
  elementos["tempo-voo"].value = "0.5";
  redimensionarCelulas(40);
  window.gameAnalysis.definirResultados([{
    numero_ap: 201,
    dezenas: [41, 42, 43, 44, 53, 55],
  }, resultado(2)]);
  elementos["botao-voo"].click();
  const [idAntes] = unicaTarefa();

  redimensionarCelulas(50);
  eventosJanela.resize();
  const reposicionada = coordenadas(circulos("marca-media")[0]);

  assert.equal(reposicionada.x, 125);
  assert.ok(Math.abs(reposicionada.y - 241.66666666666666) < 1e-10);
  assert.equal(unicaTarefa()[0], idAntes);

  elementos["botao-voo"].click();
  assert.equal(relogio.tarefas.size, 0);
});

test("mancha pequena distribui ocorrências lado a lado e inclui as médias", () => {
  redimensionarCelulas(40);
  const resultados = [
    { numero_ap: 301, dezenas: [1, 10, 20, 30, 40, 60] },
    { numero_ap: 302, dezenas: [1, 11, 21, 31, 41, 51] },
  ];
  window.gameAnalysis.desenharMancha(resultados);

  const marcas = circulos("marca-mancha-resultado");
  const medias = circulos("marca-mancha-media");
  const diametro = (3 / 25.4) * 96;
  const primeira = coordenadas(marcas[0]);
  const segundaOcorrenciaDaDezena01 = coordenadas(marcas[6]);

  assert.equal(marcas.length, 12);
  assert.equal(medias.length, 2);
  assert.ok(Math.abs(segundaOcorrenciaDaDezena01.x - primeira.x - diametro) < 1e-10);
  assert.equal(segundaOcorrenciaDaDezena01.y, primeira.y);
  assert.equal(elementos["jogo-numero"].textContent, "Todos");
  assert.equal(elementos["mensagem-sistema"].textContent, "Mancha desenhada com 2 resultados.");
});

test("ao exceder a capacidade da célula, recomeça no primeiro ponto", () => {
  redimensionarCelulas(40);
  const resultados = Array.from({ length: 10 }, (_, indice) => ({
    numero_ap: 400 + indice,
    dezenas: [1, 10, 20, 30, 40, 60],
  }));
  window.gameAnalysis.desenharMancha(resultados);

  const ocorrencias01 = circulos("marca-mancha-resultado").filter(
    (_marca, indice) => indice % 6 === 0,
  );
  assert.equal(ocorrencias01.length, 10);
  assert.deepEqual(coordenadas(ocorrencias01[9]), coordenadas(ocorrencias01[0]));
});

test("desenha aproximadamente 3.000 resultados dentro dos limites locais", () => {
  redimensionarCelulas(40);
  const resultados = Array.from({ length: 3000 }, (_, indice) => ({
    numero_ap: 1000 + indice,
    dezenas: [1, 10, 20, 30, 40, 60],
  }));
  const memoriaAntes = process.memoryUsage().heapUsed;
  const inicio = performance.now();

  window.gameAnalysis.desenharMancha(resultados);

  const duracao = performance.now() - inicio;
  const memoriaAdicional = process.memoryUsage().heapUsed - memoriaAntes;
  assert.equal(circulos("marca-mancha-resultado").length, 18000);
  assert.equal(circulos("marca-mancha-media").length, 3000);
  assert.ok(duracao < 2000, `desenho levou ${duracao.toFixed(1)} ms`);
  assert.ok(memoriaAdicional < 128 * 1024 * 1024, `consumo adicional: ${memoriaAdicional}`);
});

test("limpar remove completamente a mancha e restaura o cabeçalho", () => {
  elementos["botao-limpar"].click();

  assert.equal(elementos["camada-marcas"].children.length, 0);
  assert.equal(elementos["jogo-numero"].textContent, "—");
  assert.equal(elementos["coordenada-media"].textContent, "Média espacial: —");
  assert.equal(elementos["mensagem-sistema"].textContent, "Gráfico limpo.");
});
