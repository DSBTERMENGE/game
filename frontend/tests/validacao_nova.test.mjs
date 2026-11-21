import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  filtrosDoGrupo,
  corpoInicioTeste,
  apresentarEstadoExecucao,
  formatarIncidencia,
  formatarCombinacao,
  idsFiltrosSelecionados,
  resumirSelecao,
  organizarRelatorio,
  prepararDesenhoPainel,
  podeContinuarExecucao,
  selecaoDirigidaValida,
  corpoTesteDirigido,
  apresentarTesteDirigido,
  ocorrenciaDirigidaParaPainel,
  resumirResultadoDirigido,
  controlesPorAtividade,
  validarCatalogo,
} from "../js/validacao-nova.js";

test("teste dirigido exige grupo e filtro específicos e monta o pacote", () => {
  assert.equal(selecaoDirigidaValida("", ""), false);
  assert.equal(selecaoDirigidaValida("2", ""), false);
  assert.equal(selecaoDirigidaValida("2", "12"), true);
  assert.deepEqual(corpoTesteDirigido("2", "12"), { id_grupo: 2, id_filtro: 12 });
  assert.throws(() => corpoTesteDirigido("", "12"), /grupo e um filtro específicos/);
  assert.equal(apresentarTesteDirigido({ estado: "GERADO", total_combinacoes: 10 }),
    "10 combinações geradas e mantidas em memória.");
});

test("teste dirigido adapta cada combinação ao painel e resume o resultado", () => {
  const painel = ocorrenciaDirigidaParaPainel({
    nome_grupo: "Grupo", nome_filtro: "Filtro", total_combinacoes: 10,
    ocorrencia_atual: {
      numero: 3, combinacao: [1, 2, 3, 4, 5, 6], detectada: true,
      desenho: { dezenas_marcadas: [1, 2, 3, 4, 5, 6], segmentos: [] },
    },
  });
  assert.equal(painel.indice_combinacao, 3);
  assert.equal(painel.total_combinacoes, 10);
  assert.equal(painel.nome_filtro, "Filtro");
  assert.equal(resumirResultadoDirigido({ total_testado: 10, ocorrencias_detectadas: 9 }),
    "10 combinações testadas · 9 ocorrência(s) detectada(s).");
  assert.throws(() => ocorrenciaDirigidaParaPainel({}), /não possui combinação/);
});

test("controles impedem testes simultâneos e respeitam pré-requisitos", () => {
  assert.deepEqual(controlesPorAtividade({
    atividade: null, catalogoVazio: false, selecaoDirigida: true,
  }), {
    selecaoGeral: true, iniciarGeral: true, selecaoDirigida: true,
    testarDirigido: true,
  });
  assert.deepEqual(controlesPorAtividade({
    atividade: "geral", catalogoVazio: false, selecaoDirigida: true,
  }), {
    selecaoGeral: false, iniciarGeral: false, selecaoDirigida: false,
    testarDirigido: false,
  });
});

const catalogo = validarCatalogo({ grupos: [
  { id_grupo: 2, nome_grupo: "Grupo B", filtros: [
    { id_filtro: 20, nome_filtro: "Filtro B", descricao: "B" },
    { id_filtro: 21, nome_filtro: "Filtro C", descricao: "C" },
  ] },
  { id_grupo: 1, nome_grupo: "Grupo A", filtros: [
    { id_filtro: 10, nome_filtro: "Filtro A", descricao: "A" },
  ] },
] });

test("seleção Todos reúne todos os filtros e grupo limita sua lista", () => {
  assert.deepEqual(idsFiltrosSelecionados(catalogo, "", ""), [20, 21, 10]);
  assert.deepEqual(filtrosDoGrupo(catalogo, "2").map((item) => item.id_filtro), [20, 21]);
  assert.deepEqual(idsFiltrosSelecionados(catalogo, "2", ""), [20, 21]);
  assert.deepEqual(idsFiltrosSelecionados(catalogo, "2", "21"), [21]);
});

test("continuar somente é liberado durante pausa com ocorrência", () => {
  assert.equal(podeContinuarExecucao({ estado: "EXECUTANDO" }), false);
  assert.equal(podeContinuarExecucao({ estado: "AGUARDANDO_CONFIRMACAO" }), false);
  assert.equal(podeContinuarExecucao({
    estado: "AGUARDANDO_CONFIRMACAO", ocorrencia_atual: { combinacao: [1, 2, 3, 4, 5, 6] },
  }), true);
});

test("painel valida seis marcações e preserva segmentos geométricos", () => {
  const desenho = prepararDesenhoPainel({ desenho: {
    dezenas_marcadas: [2, 5, 7, 9, 29, 49],
    segmentos: [
      { tipo: "horizontal", x1: 0, y1: .5, x2: 10, y2: .5 },
      { tipo: "vertical", x1: 8.5, y1: 0, x2: 8.5, y2: 6 },
    ],
  } });
  assert.deepEqual([...desenho.marcadas], [2, 5, 7, 9, 29, 49]);
  assert.equal(desenho.segmentos[0].x2, 10);
  assert.equal(desenho.segmentos[1].y2, 6);
  assert.equal(formatarCombinacao([2, 5, 29]), "02 · 05 · 29");
});

test("painel aceita a circunferência do arranjo circular", () => {
  const desenho = prepararDesenhoPainel({ desenho: {
    dezenas_marcadas: [15, 17, 24, 28, 44, 48],
    segmentos: [],
    circulos: [{
      tipo: "arranjo_circular", centro_x: 5.5, centro_y: 3.5, raio: 2.236,
    }],
  } });

  assert.equal(desenho.circulos.length, 1);
  assert.equal(desenho.circulos[0].tipo, "arranjo_circular");
});

test("painel aceita a elipse inclinada do arranjo elíptico", () => {
  const desenho = prepararDesenhoPainel({ desenho: {
    dezenas_marcadas: [1, 2, 11, 13, 22, 23],
    segmentos: [],
    circulos: [],
    elipses: [{
      tipo: "arranjo_eliptico", centro_x: 1.5, centro_y: 1.5,
      raio_x: 1.414, raio_y: 0.816, angulo_graus: 45,
    }],
  } });

  assert.equal(desenho.elipses.length, 1);
  assert.equal(desenho.elipses[0].tipo, "arranjo_eliptico");
  assert.equal(desenho.elipses[0].angulo_graus, 45);
});

test("relatório agrupa filtros e mantém total, ocorrências e incidência", () => {
  const linhas = organizarRelatorio([
    { nome_grupo: "Grupo A", nome_filtro: "Filtro 1", total_testado: 1000,
      ocorrencias: 8, incidencia_percentual: "0.800000" },
    { nome_grupo: "Grupo A", nome_filtro: "Filtro 2", total_testado: 1000,
      ocorrencias: 20, incidencia_percentual: "2.000000" },
    { nome_grupo: "Grupo B", nome_filtro: "Filtro 3", total_testado: 1000,
      ocorrencias: 5, incidencia_percentual: "0.500000" },
  ]);
  assert.deepEqual(linhas.map((item) => item.tipo), ["grupo", "filtro", "filtro", "grupo", "filtro"]);
  assert.equal(linhas[1].total_testado, 1000);
  assert.equal(linhas[1].ocorrencias, 8);
  assert.equal(formatarIncidencia(linhas[1].incidencia_percentual), "0,800000%");
});

test("estado da execução limita percentual e informa grupo, filtro e término", () => {
  assert.deepEqual(apresentarEstadoExecucao({
    estado: "EXECUTANDO", percentual: 32.5, grupo_atual: "Grupo", filtro_atual: "Filtro",
  }), {
    percentual: 32.5, grupo: "Grupo", filtro: "Filtro",
    mensagem: "Teste em execução.", terminou: false, erro: false,
  });
  const concluida = apresentarEstadoExecucao({ estado: "CONCLUIDA", percentual: 120 });
  assert.equal(concluida.percentual, 100);
  assert.equal(concluida.terminou, true);
});

test("resumo e pacote de início respeitam todos, grupo e filtro", () => {
  assert.equal(resumirSelecao(catalogo, "", "").texto, "Todos os 3 filtros disponíveis.");
  assert.match(resumirSelecao(catalogo, "2", "").texto, /2 filtro\(s\) do grupo Grupo B/);
  assert.equal(resumirSelecao(catalogo, "2", "21").texto, "1 filtro: Filtro C.");
  assert.deepEqual(corpoInicioTeste(catalogo, "2", "21"), { ids_filtros: [21] });
});

test("página possui bloco, duas caixas Todos e informação da coleção fixa", async () => {
  const html = await readFile(new URL("../validacao-nova.html", import.meta.url), "utf8");
  assert.match(html, /Seleção de Filtros/);
  assert.match(html, /id="validacao-nova-grupo"/);
  assert.match(html, /id="validacao-nova-filtro"/);
  assert.match(html, /1\.000 combinações fixas de 6 dezenas/);
  assert.equal((html.match(/<option value="">Todos<\/option>/g) || []).length, 2);
  assert.match(html, /id="validacao-nova-iniciar"/);
  assert.match(html, /id="validacao-nova-confirmacao"/);
  assert.match(html, /Confirmar e iniciar/);
  assert.match(html, /id="validacao-nova-progresso"/);
  assert.match(html, /<dialog id="validacao-nova-progresso"/);
  assert.match(html, /id="validacao-nova-cancelar"/);
  assert.match(html, /Grupo atual/);
  assert.match(html, /Filtro atual/);
  assert.match(html, /id="validacao-nova-relatorio"/);
  assert.match(html, /id="validacao-nova-relatorio"[^>]*\shidden/);
  assert.match(html, /id="validacao-nova-relatorio-inspecao"/);
  assert.match(html, /Combinações testadas/);
  assert.match(html, /Ocorrências do padrão/);
  assert.match(html, /% de ocorrência/);
  assert.doesNotMatch(html, /Saldo|Total removido|Exclusões/);
  assert.match(html, /id="validacao-nova-painel"/);
  assert.doesNotMatch(html, /id="validacao-nova-painel"[^>]*\shidden/);
  assert.match(html, /viewBox="0 0 10 6"/);
  assert.match(html, /id="validacao-nova-painel-cancelar"[^>]*disabled[^>]*>Cancelar/);
  assert.match(html, /id="validacao-nova-continuar"/);
  assert.match(html, /id="validacao-nova-continuar"[^>]*disabled/);
  assert.match(html, /id="validacao-nova-final"[^>]*disabled[^>]*>Final/);
  assert.match(html, /id="validacao-nova-dirigido"/);
  assert.doesNotMatch(html, /id="validacao-nova-dirigido-gerar"/);
  assert.match(html, /Dez combinações que testam True para o filtro serão geradas para teste/);
  assert.match(html, /Iniciar teste dirigido/);
  assert.match(html, /somente na memória/);
  assert.match(html, /id="validacao-nova-dirigido-resultado"/);
  assert.match(html, /pagina-validacao-auditoria-nova/);
  assert.equal((html.match(/<option value="">Todos<\/option>/g) || []).length, 2);
});

test("interface não apresenta códigos técnicos nem nomes de função", async () => {
  const html = await readFile(new URL("../validacao-nova.html", import.meta.url), "utf8");
  assert.doesNotMatch(html, /PD_|PG_|PAD_|função detectora/i);
});

test("layout compacta os dois blocos de seleção lado a lado", async () => {
  const css = await readFile(new URL("../css/validacao-nova.css", import.meta.url), "utf8");
  assert.match(css, /grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\)/);
  assert.match(css, /\.validacao-nova-cabecalho\s*\{\s*grid-column:\s*1 \/ -1;\s*grid-row:\s*1;/);
  assert.match(css, /\.validacao-nova-aplicacao\s*\{\s*grid-column:\s*1;\s*grid-row:\s*2;/);
  assert.match(css, /\.validacao-nova-dirigido\s*\{\s*grid-column:\s*2;\s*grid-row:\s*2;/);
  assert.match(css, /width:\s*clamp\(12rem, 18vw, 19rem\)/);
  assert.match(css, /@media \(max-width: 72rem\)/);
  assert.match(css, /\.validacao-nova-painel\s*\{\s*grid-column:\s*1 \/ -1;\s*grid-row:\s*3/);
  assert.match(css, /grid-template-columns:\s*minmax\(0, 34rem\) minmax\(0, 1fr\)/);
  assert.match(css, /#validacao-nova-painel-combinacao\s*\{\s*margin:\s*0 1ch 0 0;/);
  assert.match(css, /width:\s*min\(100%, 34rem\)/);
});
