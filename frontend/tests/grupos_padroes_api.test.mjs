import assert from "node:assert/strict";
import test from "node:test";

import { criarApiGrupos } from "../js/grupos-padroes-api.js";

function resposta(corpo, status = 200) {
  return { ok: status < 400, status, async json() { return corpo; } };
}

test("adaptador localiza grupos e entrega todas as opções sem alterar a API existente", async () => {
  const fetchImpl = async () => resposta({ grupos: [
    { grupo_cod: "PG_001", grupo_nome: "Linhas", grupo_descr: "A" },
    { grupo_cod: "PG_002", grupo_nome: "Colunas", grupo_descr: "B" },
  ] });
  const resultado = await criarApiGrupos(fetchImpl).listar({ busca: "una", pagina: 1, por_pagina: 20 });
  assert.equal(resultado.total, 1);
  assert.equal(resultado.registros[0].id, "PG_002");
  assert.equal(resultado.registros[0].grupo_cod, "PG_002");
  assert.equal(resultado.registros[0].titulo, "Colunas");
  assert.equal(resultado.registros[0].descricao, "B");
});

test("adaptador traduz criação, edição e exclusão para o contrato de Grupo", async () => {
  const chamadas = [];
  const fetchImpl = async (url, opcoes = {}) => {
    chamadas.push([url, opcoes]);
    if (opcoes.method === "POST") return resposta({ grupo: { grupo_cod: "PG_003", grupo_nome: "Novo", grupo_descr: "Texto" } }, 201);
    if (opcoes.method === "PUT") return resposta({ grupo: { grupo_cod: "PG_003", grupo_nome: "Revisto", grupo_descr: "Outro" } });
    return resposta({ mensagem: "Grupo excluído." });
  };
  const api = criarApiGrupos(fetchImpl);
  await api.criar({ titulo: "Novo", descricao: "Texto" });
  await api.atualizar("PG_003", { titulo: "Revisto", descricao: "Outro" });
  await api.excluir("PG_003");
  assert.deepEqual(chamadas.map(([url, opcoes]) => [url, opcoes.method, opcoes.body]), [
    ["/api/grupos-padroes", "POST", JSON.stringify({ grupo_nome: "Novo", grupo_descr: "Texto" })],
    ["/api/grupos-padroes/PG_003", "PUT", JSON.stringify({ grupo_nome: "Revisto", grupo_descr: "Outro" })],
    ["/api/grupos-padroes/PG_003", "DELETE", undefined],
  ]);
});

test("adaptador preserva a mensagem operacional devolvida pela API", async () => {
  const api = criarApiGrupos(async () => resposta({ erro: { mensagem: "O grupo possui Subgrupos e não pode ser excluído." } }, 409));
  await assert.rejects(() => api.excluir("PG_001"), /possui Subgrupos/);
});
