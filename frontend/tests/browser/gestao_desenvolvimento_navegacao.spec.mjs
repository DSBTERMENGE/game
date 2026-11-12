import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const porta = Number(process.env.PLAYWRIGHT_TEST_PORT || 4175);
let servidor;

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    try {
      const url = new URL(requisicao.url, "http://127.0.0.1");
      const relativo = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
      if (relativo.includes("..")) return resposta.writeHead(400).end();
      const extensao = path.extname(relativo);
      const tipos = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css" };
      resposta.writeHead(200, { "Content-Type": `${tipos[extensao] || "application/octet-stream"}; charset=utf-8` });
      resposta.end(await readFile(path.join(raiz, relativo)));
    } catch (_erro) {
      resposta.writeHead(404).end();
    }
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(porta, "127.0.0.1", resolver);
  });
});

test.afterAll(async () => {
  if (servidor) await new Promise((resolver) => servidor.close(resolver));
});

const base = {
  tipo: "MODIFICACAO", descricao: "Descrição",
  data_registro: "2026-11-11", status_trabalho: "NAO_INICIADO",
  status_publicacao: "NAO_APLICAVEL",
  pagina_origem: null, observacao_publicacao: null,
  versao_registro: 1, arquivado_em: null,
};

test("localiza por trecho, abre o primeiro registro e mantém filtros horizontais", async ({ page }) => {
  await page.setViewportSize({ width: 1900, height: 1000 });
  const registros = [
    { ...base, id_manutencao: 2, titulo: "Segundo registro" },
    { ...base, id_manutencao: 1, titulo: "Primeiro registro" },
  ];
  let gravacoes = 0;
  await page.route("**/api/gestao-desenvolvimento**", async (rota) => {
    const requisicao = rota.request();
    if (requisicao.method() !== "GET") {
      gravacoes += 1;
      return rota.fulfill({ status: 500, contentType: "application/json", body: "{}" });
    }
    const url = new URL(requisicao.url());
    if (/\/historico$/.test(url.pathname)) {
      return rota.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ eventos: [] }) });
    }
    const trecho = (url.searchParams.get("busca") || "").toLocaleLowerCase("pt-BR");
    const encontrados = registros.filter((item) => item.titulo.toLocaleLowerCase("pt-BR").includes(trecho));
    return rota.fulfill({
      status: 200, contentType: "application/json",
      body: JSON.stringify({ registros: encontrados, total: encontrados.length, pagina: 1, por_pagina: 20 }),
    });
  });

  await page.goto("/gestao-desenvolvimento.html");
  const localizar = page.getByLabel("Localizar");
  const tituloFormulario = page.locator("[data-formulario]").getByRole("textbox", { name: "Título", exact: true });
  await expect(localizar).toBeVisible();
  await expect(tituloFormulario).toHaveValue("Segundo registro");
  await expect(page.locator("[data-titulos] option")).toHaveCount(2);
  await expect(page.getByLabel("Consultar arquivados")).toBeVisible();

  const colunas = await page.locator(".crud-navegavel__consulta").evaluate(
    (elemento) => getComputedStyle(elemento).gridTemplateColumns.split(" ").length,
  );
  expect(colunas).toBe(5);

  await localizar.fill("primeiro");
  await expect(tituloFormulario).toHaveValue("Primeiro registro");
  expect(gravacoes).toBe(0);

  await page.getByRole("button", { name: "Novo registro" }).click();
  const formulario = page.locator("#gestao-desenvolvimento [data-formulario]");
  const anterior = await page.locator("#gestao-desenvolvimento [data-pagina='0']").boundingBox();
  const [tipo, titulo, data, trabalho, publicacao, pagina, descricao] = await Promise.all([
    formulario.locator("[name=tipo]").boundingBox(),
    formulario.locator("[name=titulo]").boundingBox(),
    formulario.locator("[name=data_registro]").boundingBox(),
    formulario.locator("[name=status_trabalho]").boundingBox(),
    formulario.locator("[name=status_publicacao]").boundingBox(),
    formulario.locator("[name=pagina_origem]").boundingBox(),
    formulario.locator("[name=descricao]").boundingBox(),
  ]);
  expect(tipo.width).toBeLessThan(titulo.width);
  expect(data.width).toBeLessThan(descricao.width);
  expect(Math.abs(tipo.x - anterior.x)).toBeLessThanOrEqual(2);
  expect(new Set([tipo.y, titulo.y, data.y, trabalho.y]).size).toBe(1);
  expect(new Set([publicacao.y, pagina.y]).size).toBe(1);
  const espacos = [
    titulo.x - (tipo.x + tipo.width),
    data.x - (titulo.x + titulo.width),
    trabalho.x - (data.x + data.width),
    pagina.x - (publicacao.x + publicacao.width),
  ];
  expect(Math.max(...espacos) - Math.min(...espacos)).toBeLessThanOrEqual(2);
  expect(Math.min(...espacos)).toBeGreaterThanOrEqual(15);
  expect(descricao.y).toBeGreaterThan(pagina.y);
  expect(gravacoes).toBe(0);
});
