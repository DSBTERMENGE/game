import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";


const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
let servidor;
let consultas;
let resultadoFinal;
let falhaFinal;

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    if (requisicao.url === "/api/validacao/relatorio") {
      resposta.writeHead(200, { "Content-Type": "application/json" });
      resposta.end(JSON.stringify({
        fechamento: { exigidas: 200, executadas: 200, aprovadas: 199, divergentes: 1, pendentes: 0, valido: true },
        criterios: [{ codigo: "EST_SOMA", nome: "Soma das dezenas", categoria: "ESTATISTICA", estado: "APROVADO", exigidas: 200, executadas: 200, aprovadas: 199, divergentes: 1, pendentes: 0, estado_catalogo: "ATUAL" }],
        divergencias: [{ criterio: { codigo: "EST_SOMA", nome: "Soma das dezenas", categoria: "ESTATISTICA" },
          assinatura_atual: "assinatura-atual", assinatura_executada: "assinatura-atual", numero_ap: 1,
          dezenas: [4, 5, 30, 33, 41, 52], grupo: null,
          esperado: { estado: "VALOR_IDENTIFICADO", valor: "165", subgrupo_codigo: null, subgrupo_nome: null },
          calculado: { estado: "VALOR_IDENTIFICADO", valor: "164", subgrupo_codigo: null, subgrupo_nome: null },
          diferenca: "-1", hipotese_diagnostica: "Revisar a fórmula e o arredondamento." }],
      }));
      return;
    }
    if (requisicao.url.startsWith("/api/validacao/quadro")) {
      resposta.writeHead(200, { "Content-Type": "application/json" });
      resposta.end(JSON.stringify({
        estado_global: { atualizado: false, motivo: "HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA", mensagem: "Algoritmo de seleção de combinações desatualizado" },
        resumo: { total: 3800, aprovadas: 3800, reprovadas: 0, pendentes: 0 },
        paginacao: { pagina: 1, limite: 50, total_itens: 3800, total_paginas: 76 },
        filtros: {
          criterios: [{ codigo: "EST_SOMA", nome: "Soma das dezenas", categoria: "ESTATISTICA" }],
          grupos: [{ codigo: "PG_001", nome: "Sequenciais" }],
          subgrupos: [{ codigo: "PD_001", nome: "Duas sequenciais", grupo_codigo: "PG_001" }],
        },
        avaliacoes: [{
          id_resultado: 1, numero_ap: 1, dezenas: [4, 5, 30, 33, 41, 52],
          criterio: { codigo: "EST_SOMA", nome: "Soma das dezenas", categoria: "ESTATISTICA", estado: "APROVADO" },
          grupo: null, esperado: { estado: "VALOR_IDENTIFICADO", valor: "165" },
          calculado: { estado: "VALOR_IDENTIFICADO", valor: "165" }, aprovado: "S",
        }],
      }));
      return;
    }
    if (requisicao.url === "/api/validacao/execucoes" && requisicao.method === "POST") {
      resposta.writeHead(202, { "Content-Type": "application/json" });
      resposta.end(JSON.stringify({
        id: "teste-20-12", estado: "EXECUTANDO", etapa: "Sincronizando catálogo",
        concluido: 0, total: 4, percentual: 0, duracao_segundos: 0.1,
      }));
      return;
    }
    if (requisicao.url === "/api/validacao/execucoes/teste-20-12") {
      consultas += 1;
      const terminou = consultas >= 2;
      const falhou = terminou && falhaFinal;
      resposta.writeHead(200, { "Content-Type": "application/json" });
      resposta.end(JSON.stringify({
        id: "teste-20-12", estado: falhou ? "FALHOU" : (terminou ? "CONCLUIDA" : "EXECUTANDO"),
        etapa: falhou ? "Execução interrompida" : (terminou ? "Concluída" : "Executando critérios geométricos"),
        concluido: terminou ? 4 : 2, total: 4,
        percentual: terminou ? 100 : 50, duracao_segundos: terminou ? 1.2 : 0.7,
        erro: falhou ? { mensagem: "Falha técnica controlada." } : null,
        resultado: terminou && !falhou ? resultadoFinal : null,
      }));
      return;
    }
    const arquivos = {
      "/auditoria.html": ["auditoria.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/auditoria.css": ["css/auditoria.css", "text/css; charset=utf-8"],
      "/css/modal-andamento.css": ["css/modal-andamento.css", "text/css; charset=utf-8"],
      "/js/navegacao.js": ["js/navegacao.js", "text/javascript; charset=utf-8"],
      "/js/auditoria.js": ["js/auditoria.js", "text/javascript; charset=utf-8"],
      "/js/modal-andamento.js": ["js/modal-andamento.js", "text/javascript; charset=utf-8"],
    };
    const item = arquivos[requisicao.url];
    if (!item) {
      resposta.writeHead(404); resposta.end(); return;
    }
    resposta.writeHead(200, { "Content-Type": item[1] });
    resposta.end(await readFile(path.join(raiz, item[0])));
  });
  await new Promise((resolver) => servidor.listen(0, "127.0.0.1", resolver));
});

test.beforeEach(() => {
  consultas = 0;
  falhaFinal = false;
  resultadoFinal = {
    homologacao_concluida: true, avaliacoes: 3800, aprovadas: 3800,
    reprovadas: 0, pendentes: 0, sincronizacao: {
      incluidos: ["NOVO"], implementacoes_alteradas: [], regras_alteradas: [],
      excluidos: [], avaliacoes_criadas: 200,
    },
  };
});
test.afterAll(async () => new Promise((resolver) => servidor.close(resolver)));

test("modal mostra progresso real e só fecha após concluir", async ({ page }) => {
  const endereco = servidor.address();
  await page.goto(`http://127.0.0.1:${endereco.port}/auditoria.html`);
  await page.getByRole("button", { name: "Atualizar Validação e auditoria" }).click();
  const dialogo = page.getByRole("dialog");
  await expect(dialogo).toBeVisible();
  await expect(dialogo.getByRole("button", { name: "Fechar" })).toBeDisabled();
  await expect(dialogo.getByText("Executando critérios geométricos")).toBeVisible();
  await expect(dialogo.getByText("2 / 4 — 50%")).toBeVisible();
  await expect(dialogo.getByRole("button", { name: "Fechar" })).toBeEnabled();
  await expect(dialogo.getByText("4 / 4 — 100%")).toBeVisible();
  await expect(dialogo.getByText(/Validação e auditoria concluída e aprovada/)).toBeVisible();
  await expect(dialogo.getByText(/3\.800 aprovadas; 0 reprovadas; 0 pendentes/)).toBeVisible();
  await dialogo.getByRole("button", { name: "Fechar" }).click();
  await expect(dialogo).toBeHidden();
});

test("página mostra estado, filtros e grade em larguras normal e estreita", async ({ page }) => {
  const endereco = servidor.address();
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto(`http://127.0.0.1:${endereco.port}/auditoria.html`);
  await expect(page.getByText("Validação e auditoria aprovada")).toBeVisible();
  await expect(page.getByText("3.800 avaliações aprovadas; nenhuma reprovação ou pendência.")).toBeVisible();
  await expect(page.getByText("3.800").first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "04 · 05 · 30 · 33 · 41 · 52" })).toBeVisible();
  await expect(page.getByLabel("Categoria")).toBeVisible();
  await page.getByText("Relatório por função").click();
  await expect(page.getByText("199 S · 1 N · 0 pendentes")).toBeVisible();
  await expect(page.getByText("Hipótese diagnóstica da IA:")).toBeVisible();
  await expect(page.getByText("Revisar a fórmula e o arredondamento.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Exportar JSON técnico" })).toHaveAttribute("download", "");
  await expect(page.getByRole("link", { name: "Exportar tabela CSV segura" })).toHaveAttribute("href", /formato=csv/);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.getByRole("button", { name: "Atualizar Validação e auditoria" })).toBeVisible();
  await expect(page.getByText("Página 1 de 76")).toBeVisible();
});

test("modal conclui sem aprovar e orienta o filtro Situação", async ({ page }) => {
  resultadoFinal = {
    ...resultadoFinal, homologacao_concluida: false, aprovadas: 3798,
    reprovadas: 1, pendentes: 1,
  };
  const endereco = servidor.address();
  await page.goto(`http://127.0.0.1:${endereco.port}/auditoria.html`);
  await page.getByRole("button", { name: "Atualizar Validação e auditoria" }).click();
  const dialogo = page.getByRole("dialog");
  await expect(dialogo.getByText(/não foi aprovada/)).toBeVisible();
  await expect(dialogo.getByText(/3\.798 aprovadas; 1 reprovadas; 1 pendentes/)).toBeVisible();
  await expect(dialogo.getByText(/Use o filtro Situação/)).toBeVisible();
});

test("modal distingue falha técnica de validação não aprovada", async ({ page }) => {
  falhaFinal = true;
  const endereco = servidor.address();
  await page.goto(`http://127.0.0.1:${endereco.port}/auditoria.html`);
  await page.getByRole("button", { name: "Atualizar Validação e auditoria" }).click();
  const dialogo = page.getByRole("dialog");
  await expect(dialogo.getByText("Falha técnica controlada.")).toBeVisible();
  await expect(dialogo.getByText(/não foi aprovada/)).toHaveCount(0);
  await expect(dialogo.getByRole("button", { name: "Fechar" })).toBeEnabled();
});
