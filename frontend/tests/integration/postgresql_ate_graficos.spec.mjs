import { expect, test } from "@playwright/test";
import { spawn } from "node:child_process";
import path from "node:path";


let servidor;
let diagnostico = "";


async function aguardarServidor() {
  const limite = Date.now() + 15_000;
  while (Date.now() < limite) {
    try {
      const resposta = await fetch("http://127.0.0.1:5051/api/saude");
      if (resposta.ok) return;
    } catch {
      // O processo ainda está iniciando.
    }
    await new Promise((resolver) => setTimeout(resolver, 100));
  }
  throw new Error(`Servidor Flask não iniciou. ${diagnostico}`);
}


test.beforeAll(async () => {
  servidor = spawn(
    "python",
    [
      "-c",
      "from dotenv import load_dotenv; load_dotenv(); from msen.api import criar_app; criar_app().run(host='127.0.0.1', port=5051, debug=False, use_reloader=False)",
    ],
    {
      cwd: path.resolve("MSen"),
      env: { ...process.env, PYTHONPATH: "src" },
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
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
});


test("PostgreSQL real alimenta navegação, voo e mancha no Chrome", async ({ page }) => {
  const antes = await (await page.request.get("/api/resultados")).json();
  expect(antes.total).toBe(3069);

  await page.goto("/");
  await expect(page.locator("#mensagem-sistema")).toHaveText(
    "3069 resultados carregados.",
    { timeout: 15_000 },
  );
  await expect(page.locator("#seletor-resultado option")).toHaveCount(3069);
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await expect(page.locator("circle.marca-resultado")).toHaveCount(6);
  await expect(page.locator("circle.marca-media")).toHaveCount(1);

  await page.locator("#seletor-resultado").selectOption("3068");
  await expect(page.locator("#jogo-numero")).toHaveText("3069");
  await page.locator("#botao-proximo").click();
  await expect(page.locator("#jogo-numero")).toHaveText("1");

  await page.locator("#tempo-voo").fill("0.1");
  await page.locator("#botao-voo").click();
  await expect(page.locator("#jogo-numero")).toHaveText("2", { timeout: 1_000 });
  await page.locator("#botao-voo").click();

  await page.goto("/padroes.html");
  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(9);
  const padraoDuas = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_001"]');
  await expect(padraoDuas.locator("td").nth(4)).toHaveText("1192");
  await expect(padraoDuas.locator("td").nth(5)).toHaveText("2,575147");
  await expect(padraoDuas.locator("td").nth(7)).toHaveText("Implementada");
  await expect(padraoDuas.locator("select")).toHaveValue("PG_001");

  await page.goto("/");

  const inicioMancha = Date.now();
  await page.locator("#botao-mancha").click();
  await expect(page.locator("circle.marca-mancha-resultado")).toHaveCount(18_414);
  await expect(page.locator("circle.marca-mancha-media")).toHaveCount(3_069);
  expect(Date.now() - inicioMancha).toBeLessThan(15_000);
  await page.locator("#botao-limpar").click();
  await expect(page.locator("#camada-marcas circle")).toHaveCount(0);

  const depois = await (await page.request.get("/api/resultados")).json();
  expect(depois.total).toBe(3069);
});
