import { expect, test } from "@playwright/test";
import { execFileSync, spawn } from "node:child_process";
import path from "node:path";

const nomeBanco = `games_test_7_1_${process.pid}`;
const origem = "http://127.0.0.1:5054";
const pastaMSen = path.resolve("MSen");
const suporteBanco = path.join(pastaMSen, "tests", "suporte_banco_integracao.py");
const ambientePython = { ...process.env, PYTHONPATH: "src" };
let servidor;
let diagnostico = "";

function banco(operacao) {
  return execFileSync("python", [suporteBanco, operacao, nomeBanco], {
    cwd: pastaMSen, env: ambientePython, encoding: "utf8", windowsHide: true,
  });
}

async function aguardarServidor() {
  const limite = Date.now() + 15_000;
  while (Date.now() < limite) {
    try {
      const resposta = await fetch(`${origem}/api/saude`);
      if (resposta.ok) return;
    } catch { /* servidor iniciando */ }
    await new Promise((resolver) => setTimeout(resolver, 100));
  }
  throw new Error(`Servidor Flask não iniciou. ${diagnostico}`);
}

test.beforeAll(async () => {
  banco("criar");
  servidor = spawn("python", [
    "-c",
    "from dotenv import load_dotenv; load_dotenv(); from msen.api import criar_app; criar_app().run(host='127.0.0.1', port=5054, debug=False, use_reloader=False)",
  ], {
    cwd: pastaMSen,
    env: { ...ambientePython, GAME_DB_NAME: nomeBanco },
    windowsHide: true,
    stdio: ["ignore", "pipe", "pipe"],
  });
  servidor.stdout.on("data", (dados) => { diagnostico += dados.toString(); });
  servidor.stderr.on("data", (dados) => { diagnostico += dados.toString(); });
  await aguardarServidor();
});

test.afterAll(async () => {
  if (servidor?.exitCode === null) servidor.kill();
  await new Promise((resolver) => {
    if (!servidor || servidor.exitCode !== null) resolver();
    else {
      servidor.once("exit", resolver);
      setTimeout(resolver, 3_000);
    }
  });
  banco("remover");
});

test("cria, consulta, altera e exclui Padrão mantendo id_grupo", async ({ page }) => {
  const grupos = await (await page.request.get(`${origem}/api/grupos-padroes`)).json();
  const grupo = grupos.grupos.find((item) => item.grupo_cod === "PG_002");
  expect(grupo).toBeTruthy();

  await page.goto(`${origem}/padroes.html`);
  const filtroGrupo = page.locator('[data-filtro="grupo_cod"]');
  const seletorPadrao = page.locator("[data-seletor-registro]");
  await expect(page.getByRole("button", { name: "Novo registro" })).toBeDisabled();
  await filtroGrupo.selectOption(grupo.grupo_cod);

  await page.getByRole("button", { name: "Novo registro" }).click();
  await page.getByLabel("Nome do padrão").fill("Padrão temporário integrado");
  await page.getByLabel("Descrição").fill("Registro temporário da etapa 30.4.3.");
  await page.getByRole("button", { name: "Salvar registro" }).click();
  const criacaoConcluida = page.waitForResponse((respostaHttp) =>
    respostaHttp.request().method() === "POST" && respostaHttp.url().endsWith("/api/padroes"));
  await page.getByRole("button", { name: "Sim, salvar registro" }).click();
  await criacaoConcluida;
  await expect(seletorPadrao).toContainText("Padrão temporário integrado");

  let resposta = await (await page.request.get(`${origem}/api/padroes?grupo_cod=${grupo.grupo_cod}`)).json();
  let criado = resposta.padroes.find((item) => item.padrao_nome === "Padrão temporário integrado");
  expect(criado.id_grupo).toBe(grupo.id_grupo);

  await page.getByRole("button", { name: "Editar" }).click();
  await page.getByLabel("Descrição").fill("Descrição alterada e vínculo preservado.");
  await page.getByRole("button", { name: "Salvar registro" }).click();
  const alteracaoConcluida = page.waitForResponse((respostaHttp) =>
    respostaHttp.request().method() === "PUT" && respostaHttp.url().includes("/api/padroes/"));
  await page.getByRole("button", { name: "Sim, salvar registro" }).click();
  await alteracaoConcluida;
  resposta = await (await page.request.get(`${origem}/api/padroes?grupo_cod=${grupo.grupo_cod}`)).json();
  criado = resposta.padroes.find((item) => item.padrao_cod === criado.padrao_cod);
  expect(criado.id_grupo).toBe(grupo.id_grupo);
  expect(criado.padrao_descr).toBe("Descrição alterada e vínculo preservado.");

  await page.getByRole("button", { name: "Excluir" }).click();
  const exclusaoConcluida = page.waitForResponse((respostaHttp) =>
    respostaHttp.request().method() === "DELETE" && respostaHttp.url().includes("/api/padroes/"));
  await page.getByRole("button", { name: "Sim, excluir registro" }).click();
  await exclusaoConcluida;
  resposta = await (await page.request.get(`${origem}/api/padroes?grupo_cod=${grupo.grupo_cod}`)).json();
  expect(resposta.padroes.some((item) => item.padrao_cod === criado.padrao_cod)).toBe(false);
});
