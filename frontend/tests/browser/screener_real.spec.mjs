import { expect, test } from "@playwright/test";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";


const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
let servidor;


test.beforeAll(async () => {
  servidor = spawn("python", [
    "-c",
    "import sys; sys.path.insert(0, 'MSen/src'); from msen.api import criar_app; criar_app().run(host='127.0.0.1', port=4174, use_reloader=False)",
  ], { cwd: raiz, stdio: ["ignore", "pipe", "pipe"] });
  await new Promise((resolver, rejeitar) => {
    const temporizador = setTimeout(
      () => rejeitar(new Error("O servidor Flask local não iniciou.")),
      20_000,
    );
    const verificar = (dados) => {
      if (!dados.toString().includes("Running on")) return;
      clearTimeout(temporizador);
      resolver();
    };
    servidor.stdout.on("data", verificar);
    servidor.stderr.on("data", verificar);
    servidor.once("error", rejeitar);
    servidor.once("exit", (codigo) => {
      if (codigo) rejeitar(new Error(`Servidor Flask encerrou com código ${codigo}.`));
    });
  });
});


test.afterAll(async () => {
  if (!servidor || servidor.exitCode !== null) return;
  const encerrou = new Promise((resolver) => servidor.once("exit", resolver));
  servidor.kill();
  await encerrou;
  servidor.stdout.destroy();
  servidor.stderr.destroy();
});


test("Chrome serve o Screener oficial em três níveis", async ({ page }) => {
  await page.goto("http://127.0.0.1:4174/screener.html");
  await expect(page.locator("h1")).toHaveText("Screener");
  await expect(page.locator(".navegacao-pagina")).toHaveText("Funil em três níveis");
  await expect(page.locator("#botao-executar-extensivel")).toBeEnabled();
  await expect(page.locator("#corpo-validacoes-screener")).toHaveCount(0);
});
