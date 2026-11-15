import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  criarControladorCrud, ESTADOS,
} from "../js/crud-navegavel.js";


const campos = [
  { nome: "titulo", rotulo: "Título", tipo: "texto", obrigatorio: true },
  { nome: "descricao", rotulo: "Descrição", tipo: "texto-longo", obrigatorio: true },
];

function prepararApi() {
  const chamadas = [];
  const api = {
    async listar(consulta) {
      chamadas.push(["listar", consulta]);
      return { registros: [{ id_manutencao: 1, titulo: "Um", descricao: "Texto", versao_registro: 1 }], total: 1 };
    },
    async criar(dados, chave) {
      chamadas.push(["criar", dados, chave]);
      return { registro: { id_manutencao: 2, ...dados, versao_registro: 1 } };
    },
    async atualizar(id, dados, versao) {
      chamadas.push(["atualizar", id, dados, versao]);
      return { registro: { id_manutencao: id, ...dados, versao_registro: versao + 1 } };
    },
    async arquivar(id, versao) {
      chamadas.push(["arquivar", id, versao]);
      return { registro: { id_manutencao: id, titulo: "Um", descricao: "Texto", versao_registro: versao + 1, arquivado_em: "agora" } };
    },
    async desarquivar(id, versao) {
      chamadas.push(["desarquivar", id, versao]);
      return { registro: { id_manutencao: id, titulo: "Um", descricao: "Texto", versao_registro: versao + 1, arquivado_em: null } };
    },
  };
  return { api, chamadas };
}

const controlador = (api, extras = {}) => criarControladorCrud({
  campos, api, gerarChaveIdempotencia: async () => "a".repeat(64), ...extras,
});

test("carrega lista paginada sem compartilhar estado", async () => {
  const primeira = prepararApi();
  const segunda = prepararApi();
  const a = controlador(primeira.api);
  const b = controlador(segunda.api);
  await a.pesquisar("falha");
  await b.carregar();
  assert.equal(a.obterEstado().busca, "falha");
  assert.equal(b.obterEstado().busca, "");
  assert.equal(primeira.chamadas[0][1].pagina, 1);
  assert.equal(primeira.chamadas[0][1].por_pagina, 20);
  assert.equal(a.obterEstado().selecionado.titulo, "Um");
});

test("localização reúne todos os títulos e usa consulta sem trecho", async () => {
  const { api, chamadas } = prepararApi();
  const crud = controlador(api);
  const titulos = await crud.listarTitulos();
  assert.deepEqual(titulos, ["Um"]);
  const consulta = chamadas.find(([nome, dados]) => nome === "listar" && dados.por_pagina === 100)[1];
  assert.equal(consulta.busca, "");
  assert.equal(consulta.ordenacao, "TITULO");
});

test("abrir, preencher ou solicitar gravação não cria antes da confirmação", async () => {
  const { api, chamadas } = prepararApi();
  const crud = controlador(api);
  crud.novo();
  crud.alterarCampo("titulo", "Novo item");
  crud.alterarCampo("descricao", "Detalhes");
  crud.conferir();
  assert.equal(crud.obterEstado().modo, ESTADOS.CONFERENCIA);
  assert.equal(chamadas.some(([nome]) => nome === "criar"), false);
  await crud.salvar();
  assert.equal(chamadas.filter(([nome]) => nome === "criar").length, 1);
  assert.equal(chamadas.find(([nome]) => nome === "criar")[2].length, 64);
});

test("campos obrigatórios são validados depois da confirmação", async () => {
  const { api } = prepararApi();
  const crud = controlador(api);
  crud.novo();
  crud.conferir();
  assert.equal(crud.obterEstado().modo, ESTADOS.CONFERENCIA);
  await crud.salvar();
  assert.equal(crud.obterEstado().modo, ESTADOS.NOVO);
  assert.deepEqual(Object.keys(crud.obterEstado().erros).sort(), ["descricao", "titulo"]);
});

test("cancelamento exige decisão quando há alterações", () => {
  const { api } = prepararApi();
  const crud = controlador(api);
  crud.novo();
  crud.alterarCampo("titulo", "Rascunho");
  assert.equal(crud.cancelarEdicao(), false);
  assert.equal(crud.obterEstado().modo, ESTADOS.NOVO);
  assert.equal(crud.cancelarEdicao({ descartar: true }), true);
  assert.equal(crud.obterEstado().modo, ESTADOS.CONSULTA);
});

test("edição envia identificador e versão lida", async () => {
  const { api, chamadas } = prepararApi();
  const crud = controlador(api);
  crud.consultar({ id_manutencao: 8, titulo: "Antes", descricao: "Texto", versao_registro: 4 });
  crud.editar();
  crud.alterarCampo("titulo", "Depois");
  crud.conferir();
  await crud.salvar();
  const chamada = chamadas.find(([nome]) => nome === "atualizar");
  assert.deepEqual(chamada.slice(1), [8, { titulo: "Depois", descricao: "Texto" }, 4]);
  assert.equal(crud.obterEstado().selecionado.versao_registro, 5);
});

test("arquivamento usa versão e não chama exclusão", async () => {
  const { api, chamadas } = prepararApi();
  const crud = controlador(api);
  crud.consultar({ id_manutencao: 3, titulo: "Item", descricao: "Texto", versao_registro: 2 });
  await crud.definirArquivamento(true);
  assert.deepEqual(chamadas.find(([nome]) => nome === "arquivar"), ["arquivar", 3, 2]);
  assert.equal("excluir" in api, false);
});

test("exclusão definitiva é opcional e usa o identificador configurado", async () => {
  const { api, chamadas } = prepararApi();
  delete api.arquivar;
  delete api.desarquivar;
  api.excluir = async (codigo, versao) => {
    chamadas.push(["excluir", codigo, versao]);
    return { mensagem: "Excluído." };
  };
  const crud = controlador(api, {
    obterIdentificador: (registro) => registro.grupo_cod,
  });
  crud.consultar({ grupo_cod: "PG_007", titulo: "Grupo", descricao: "Texto" });
  await crud.excluir();
  assert.deepEqual(chamadas.find(([nome]) => nome === "excluir"), ["excluir", "PG_007", undefined]);
  assert.equal(crud.obterEstado().mensagem, "Registro excluído.");
});

test("cadastro pode operar sem arquivamento nem exclusão", async () => {
  const { api } = prepararApi();
  delete api.arquivar;
  delete api.desarquivar;
  const crud = controlador(api);
  await crud.carregar();
  assert.equal(crud.obterEstado().selecionado.titulo, "Um");
  await assert.rejects(() => crud.definirArquivamento(true), /não utiliza arquivamento/);
  await assert.rejects(() => crud.excluir(), /não utiliza exclusão definitiva/);
});

test("identificador próprio não é chamado antes da primeira seleção", async () => {
  const { api } = prepararApi();
  const crud = controlador(api, {
    obterIdentificador(registro) {
      assert.ok(registro);
      return registro.id_manutencao;
    },
  });
  await crud.carregar();
  assert.equal(crud.obterEstado().selecionado.id_manutencao, 1);
});

test("filtro obrigatório impede consulta até a escolha do registro relacionado", async () => {
  const { api, chamadas } = prepararApi();
  const crud = controlador(api, {
    filtros: [{
      nome: "grupo_cod", rotulo: "Grupo", obrigatorio: true,
      opcoes: [{ valor: "PG_001", rotulo: "Sequenciais" }],
    }],
  });
  await crud.carregar();
  assert.equal(chamadas.some(([nome]) => nome === "listar"), false);
  assert.equal(crud.obterEstado().total, 0);
  assert.match(crud.obterEstado().mensagem, /Selecione grupo/);

  await crud.filtrar({ grupo_cod: "PG_001" });
  assert.equal(chamadas.some(([nome]) => nome === "listar"), true);
  assert.equal(crud.obterEstado().filtros.grupo_cod, "PG_001");
});

test("falha preserva rascunho para correção", async () => {
  const { api } = prepararApi();
  api.criar = async () => { throw new Error("Título já utilizado."); };
  const crud = controlador(api);
  crud.novo();
  crud.alterarCampo("titulo", "Repetido");
  crud.alterarCampo("descricao", "Texto");
  crud.conferir();
  await crud.salvar();
  assert.equal(crud.obterEstado().modo, ESTADOS.NOVO);
  assert.equal(crud.obterEstado().rascunho.titulo, "Repetido");
  assert.match(crud.obterEstado().mensagem, /utilizado/);
});

test("falha técnica de carregamento recebe mensagem operacional", async () => {
  const { api } = prepararApi();
  api.listar = async () => { throw new TypeError("Cannot read properties of null"); };
  const crud = controlador(api);
  await crud.carregar();
  assert.equal(crud.obterEstado().mensagem, "Não foi possível carregar os registros.");
});

test("contrato rejeita campos repetidos e adaptador incompleto", () => {
  const { api } = prepararApi();
  assert.throws(() => criarControladorCrud({ campos: [campos[0], campos[0]], api }), /repetido/);
  assert.throws(() => criarControladorCrud({ campos, api: {} }), /operação listar/);
  assert.throws(() => criarControladorCrud({ campos, api, usarExclusao: true }), /arquivamento ou exclusão/);
});

test("camada visual possui lista, formulário, confirmação e acessibilidade", async () => {
  const javascript = await readFile(new URL("../js/crud-navegavel.js", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/crud-navegavel.css", import.meta.url), "utf8");
  assert.match(javascript, /aria-live="polite"/);
  assert.match(javascript, /Nenhum dado será gravado antes da confirmação/);
  assert.match(javascript, /Descartar alterações\?/);
  assert.match(javascript, /data-paginacao/);
  assert.match(javascript, /Nenhum registro encontrado/);
  assert.match(javascript, /Salvar registro/);
  assert.match(javascript, /Deseja salvar este registro\?/);
  assert.match(javascript, /Sim, salvar registro/);
  assert.match(javascript, /Confirmar arquivamento/);
  assert.match(javascript, /Confirmar exclusão/);
  assert.match(javascript, /data-filtro/);
  assert.match(javascript, /filtro\.obrigatorio/);
  assert.match(javascript, /data-ordenacao/);
  assert.match(javascript, />Localizar</);
  assert.match(javascript, /Consultar arquivados/);
  assert.match(javascript, /data-titulos/);
  assert.doesNotMatch(javascript, /window\.confirm/);
  assert.match(css, /grid-template-columns/);
  assert.match(css, /crud-navegavel__campo--curta/);
  assert.match(css, /crud-navegavel__campo--media/);
  assert.match(css, /crud-navegavel__campo--larga/);
  assert.match(css, /crud-navegavel__campo--total/);
  assert.match(css, /crud-navegavel--vertical/);
  assert.match(css, /crud-navegavel--selecao/);
  assert.match(javascript, /data-seletor-registro/);
  assert.match(javascript, /data-contador-registros/);
  assert.match(css, /data-tipo="erro"/);
  assert.match(css, /@media \(max-width: 850px\)/);
  assert.match(css, /prefers-reduced-motion/);
});
