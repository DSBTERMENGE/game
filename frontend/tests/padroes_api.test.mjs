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

test("ordena alfabeticamente os grupos oferecidos em Padrões", async () => {
  const fetchImpl = async () => resposta({ grupos: [
    { grupo_cod: "PG_003", grupo_nome: "Linhas" },
    { grupo_cod: "PG_001", grupo_nome: "Áreas" },
    { grupo_cod: "PG_002", grupo_nome: "Colunas" },
  ] });

  const grupos = await listarGruposParaFiltro(fetchImpl);

  assert.deepEqual(
    grupos.map((grupo) => grupo.grupo_nome),
    ["Áreas", "Colunas", "Linhas"],
  );
});

test("criação e alteração preservam o Grupo escolhido", async () => {
  const chamadas = [];
  const fetchImpl = async (url, opcoes = {}) => {
    chamadas.push([url, opcoes]);
    if (!opcoes.method) return resposta({ padroes: [] });
    return resposta({ padrao: {
      id_padrao: 10, padrao_cod: "PD_010", padrao_nome: "Nome",
      padrao_descr: "Descrição", grupo_cod: "PG_002",
      funcao_detectora: url.includes("funcao-detectora")
        ? "msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais" : null,
    } });
  };
  const api = criarApiPadroes(fetchImpl);
  await api.listar({ grupo_cod: "PG_002", busca: "" });
  await api.criar({ titulo: "Nome", descricao: "Descrição" });
  const atualizado = await api.atualizar("PD_010", {
    titulo: "Nome", descricao: "Descrição",
    funcaoDetectora: "msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais",
  });
  assert.equal(JSON.parse(chamadas[1][1].body).grupo_cod, "PG_002");
  assert.equal(chamadas[2][0], "/api/padroes/PD_010");
  assert.equal(chamadas[3][0], "/api/padroes/id/10/funcao-detectora");
  assert.equal(
    JSON.parse(chamadas[3][1].body).funcao_detectora,
    "msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais",
  );
  assert.equal(
    atualizado.registro.funcaoDetectora,
    "msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais",
  );
});
