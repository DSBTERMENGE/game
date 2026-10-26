import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test, { before } from "node:test";


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
    if (!this.disabled) this.listeners[tipo]?.({ target: this });
  }

  click() {
    this.disparar("click");
  }

  getBoundingClientRect() {
    if (this.id?.startsWith("dezena-")) {
      const numero = Number(this.id.slice(-2));
      return {
        left: ((numero - 1) % 10) * 40,
        top: Math.floor((numero - 1) / 10) * 40,
        width: 40,
        height: 40,
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
  "coordenada-media", "mensagem-sistema", "arquivo-excel", "nome-arquivo",
  "botao-selecionar-excel", "botao-importar-excel", "seletor-resultado",
  "botao-anterior", "botao-proximo", "tempo-voo", "botao-voo",
  "botao-mancha", "botao-limpar",
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
  addEventListener() {},
  clearTimeout,
  setTimeout,
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

before(async () => {
  await import("../js/main.js");
  await new Promise((resolver) => setImmediate(resolver));
});

test("HTML possui controles necessários e aceita somente XLSX", async () => {
  const html = await readFile(new URL("../index.html", import.meta.url), "utf8");
  for (const id of ids) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /id="arquivo-excel"[^>]+accept="\.xlsx"/);
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
