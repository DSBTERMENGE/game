import assert from "node:assert/strict";
import test from "node:test";

import { criarApiPadroes, listarGruposParaFiltro } from "../js/padroes-api.js";

function resposta(corpo, status = 200) {
  return { ok: status < 400, status, async json() { return corpo; } };
}

test("lista Grupos e filtra Padrões pelo relacionamento", async () => {
  const chamadas = [];
  const fetchImpl = async (url) => {
    chamadas.push(url);
    if (url === "/api/grupos-padroes") return resposta({ grupos: [{ grupo_cod: "PG_001", grupo_nome: "Sequenciais" }] });
    return resposta({ padroes: [{ padrao_cod: "PD_001", padrao_nome: "Duas sequenciais", padrao_descr: "Texto", grupo_cod: "PG_001" }] });
  };
  assert.equal((await listarGruposParaFiltro(fetchImpl))[0].grupo_cod, "PG_001");
  const resultado = await criarApiPadroes(fetchImpl).listar({ grupo_cod: "PG_001", busca: "duas" });
  assert.equal(resultado.registros[0].titulo, "Duas sequenciais");
  assert.ok(chamadas.includes("/api/padroes?grupo_cod=PG_001"));
});

test("criação e alteração preservam o Grupo escolhido", async () => {
  const chamadas = [];
  const fetchImpl = async (url, opcoes = {}) => {
    chamadas.push([url, opcoes]);
    if (!opcoes.method) return resposta({ padroes: [] });
    return resposta({ padrao: { padrao_cod: "PD_010", padrao_nome: "Nome", padrao_descr: "Descrição", grupo_cod: "PG_002" } });
  };
  const api = criarApiPadroes(fetchImpl);
  await api.listar({ grupo_cod: "PG_002", busca: "" });
  await api.criar({ titulo: "Nome", descricao: "Descrição" });
  await api.atualizar("PD_010", { titulo: "Nome", descricao: "Descrição" });
  for (const [, opcoes] of chamadas.filter(([, opcoes]) => opcoes.method)) {
    assert.equal(JSON.parse(opcoes.body).grupo_cod, "PG_002");
  }
});
