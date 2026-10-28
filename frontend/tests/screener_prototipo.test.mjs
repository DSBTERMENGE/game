import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { PROTOTIPO_SCREENER, validarFechamentoPrototipo } from "../js/screener-prototipo-dados.js";


test("protótipo fecha contabilmente nos três níveis", () => {
  assert.equal(PROTOTIPO_SCREENER.niveis.length, 3);
  assert.equal(validarFechamentoPrototipo(), true);
  const excluidas = PROTOTIPO_SCREENER.niveis.reduce(
    (total, nivel) => total + nivel.exclusoes,
    0,
  );
  assert.equal(
    PROTOTIPO_SCREENER.total_inicial,
    excluidas + PROTOTIPO_SCREENER.total_aprovado,
  );
});

test("exclusões de cada nível são líquidas e fecham com seus filtros", () => {
  for (const nivel of PROTOTIPO_SCREENER.niveis) {
    assert.equal(
      nivel.exclusoes,
      nivel.filtros.reduce((total, filtro) => total + filtro.exclusoes, 0),
    );
    assert.equal(nivel.entrada - nivel.exclusoes, nivel.saldo);
  }
});

test("padrões exibem limite, frequências e lista selecionada", () => {
  const padroes = PROTOTIPO_SCREENER.niveis.find((nivel) => nivel.codigo === "padroes");
  assert.equal(padroes.limite_raridade, "10%");
  assert.deepEqual(padroes.selecionados, ["PD_003", "PD_006", "PD_009", "PD_012"]);
  assert.ok(padroes.filtros.every((filtro) => filtro.regra.includes("Frequência histórica")));
});

test("página declara dados fictícios e não chama API", async () => {
  const html = await readFile(new URL("../screener-prototipo.html", import.meta.url), "utf8");
  const javascript = await readFile(new URL("../js/screener-prototipo.js", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/screener.css", import.meta.url), "utf8");

  assert.match(html, /ESBOÇO VISUAL — dados inteiramente fictícios/);
  assert.match(html, /Não chama API, não grava banco e não executa exclusões/);
  assert.doesNotMatch(javascript, /fetch\s*\(/);
  assert.match(html, /id="botao-abrir-todos"/);
  assert.match(html, /id="botao-fechar-todos"/);
  assert.match(css, /\.prototipo-pagina\s*\{[^}]*overflow:\s*hidden/s);
  assert.match(css, /\.prototipo-niveis\s*\{[^}]*overflow:\s*auto/s);
});
