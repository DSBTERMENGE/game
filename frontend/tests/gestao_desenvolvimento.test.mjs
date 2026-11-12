import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { criarApiGestao } from "../js/gestao-desenvolvimento-api.js";

const html = await readFile(new URL("../gestao-desenvolvimento.html", import.meta.url), "utf8");
const pagina = await readFile(new URL("../js/gestao-desenvolvimento.js", import.meta.url), "utf8");
const css = await readFile(new URL("../css/gestao-desenvolvimento.css", import.meta.url), "utf8");

function resposta(corpo, status = 200) {
  return { ok: status >= 200 && status < 300, status, async json() { return corpo; } };
}

test("adaptador traduz lista, criação, edição e arquivamento para a API", async () => {
  const chamadas = [];
  const fetchFalso = async (url, opcoes) => {
    chamadas.push([url, opcoes]);
    return resposta({ registro: { id_manutencao: 1 }, registros: [], total: 0 });
  };
  const api = criarApiGestao(fetchFalso);
  await api.listar({ busca: "falha", pagina: 2, por_pagina: 20, tipo: null });
  await api.criar({ titulo: "Item" }, "a".repeat(64));
  await api.atualizar(1, { titulo: "Novo" }, 3);
  await api.arquivar(1, 4);
  await api.desarquivar(1, 5);
  assert.match(chamadas[0][0], /busca=falha/);
  assert.doesNotMatch(chamadas[0][0], /tipo=/);
  assert.equal(chamadas[1][1].method, "POST");
  assert.equal(JSON.parse(chamadas[1][1].body).chave_idempotencia.length, 64);
  assert.equal(JSON.parse(chamadas[2][1].body).versao_registro, 3);
  assert.equal(chamadas[3][1].method, "POST");
  assert.equal(chamadas[4][1].method, "DELETE");
});

test("adaptador apresenta mensagem segura devolvida pela API", async () => {
  const api = criarApiGestao(async () => resposta({ erro: { codigo: "CONFLITO_VERSAO", mensagem: "Atualize a consulta." } }, 409));
  await assert.rejects(() => api.consultar(1), (erro) => erro.codigo === "CONFLITO_VERSAO" && erro.message === "Atualize a consulta.");
});

test("página aplica o CRUD reutilizável sem bloco lateral perdido", () => {
  assert.match(html, /id="gestao-desenvolvimento"/);
  assert.doesNotMatch(html, /id="historico-desenvolvimento"/);
  assert.match(html, /css\/crud-navegavel\.css/);
  assert.match(html, /js\/gestao-desenvolvimento\.js/);
  assert.match(pagina, /criarCrudNavegavel/);
  for (const coluna of ["titulo", "data_registro", "tipo", "status_trabalho"])
    assert.match(pagina, new RegExp(`campo: "${coluna}"`));
  assert.doesNotMatch(pagina, /api\.historico/);
  assert.doesNotMatch(pagina, /prioridade/);
  assert.doesNotMatch(pagina, /origem_registro/);
  assert.match(pagina, /usarOrdenacao: false/);
  assert.match(pagina, /usarOrdenacao: false/);
  for (const largura of ["curta", "media", "larga", "total"])
    assert.match(pagina, new RegExp(`largura: "${largura}"`));
  assert.doesNotMatch(pagina, /id_manutencao.*rotulo/);
});

test("ajuda contextual abre o tópico central da Gestão", () => {
  assert.match(html, /id="abrir-ajuda-gestao"/);
  assert.match(html, /ajuda\.html\?origem=%2Fgestao-desenvolvimento\.html#pagina-gestao-desenvolvimento/);
  assert.doesNotMatch(html, /id="ajuda-gestao-desenvolvimento"/);
});

test("layout inicia no topo e usa toda a largura disponível", () => {
  assert.match(css, /grid-template-columns/);
  assert.match(css, /align-content: start/);
  assert.doesNotMatch(css, /\.gestao-historico/);
  assert.match(css, /data-campo="tipo"/);
  assert.match(css, /data-campo="descricao"/);
});

test("navegação principal inclui a Gestão do desenvolvimento", async () => {
  for (const arquivo of ["index.html", "screener.html", "selecao-dezenas.html", "auditoria.html"]) {
    const conteudo = await readFile(new URL(`../${arquivo}`, import.meta.url), "utf8");
    assert.match(conteudo, /href="\/gestao-desenvolvimento\.html"/);
  }
});
