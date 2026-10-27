import { expect, test } from "@playwright/test";
import { execFileSync, spawn } from "node:child_process";
import path from "node:path";


const nomeBanco = `games_test_7_1_${process.pid}`;
const origem = "http://127.0.0.1:5053";
const raiz = path.resolve(".");
const pastaMSen = path.join(raiz, "MSen");
const suporteBanco = path.join(pastaMSen, "tests", "suporte_banco_integracao.py");
const ambientePython = { ...process.env, PYTHONPATH: "src" };
let servidor;
let diagnostico = "";


function banco(operacao) {
  return execFileSync("python", [suporteBanco, operacao, nomeBanco], {
    cwd: pastaMSen,
    env: ambientePython,
    encoding: "utf8",
    windowsHide: true,
  });
}


async function aguardarServidor() {
  const limite = Date.now() + 15_000;
  while (Date.now() < limite) {
    try {
      const resposta = await fetch(`${origem}/api/saude`);
      if (resposta.ok) return;
    } catch {
      // O processo ainda está iniciando.
    }
    await new Promise((resolver) => setTimeout(resolver, 100));
  }
  throw new Error(`Servidor Flask não iniciou. ${diagnostico}`);
}


test.beforeAll(async () => {
  banco("criar");
  servidor = spawn(
    "python",
    [
      "-c",
      "from dotenv import load_dotenv; load_dotenv(); from msen.api import criar_app; criar_app().run(host='127.0.0.1', port=5053, debug=False, use_reloader=False)",
    ],
    {
      cwd: pastaMSen,
      env: { ...ambientePython, GAME_DB_NAME: nomeBanco },
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
  banco("remover");
});


async function incluirResultado(page, numero_ap, data_resultado, dezenas) {
  const resposta = await page.request.post(`${origem}/api/resultados`, {
    data: { numero_ap, data_resultado, dezenas },
  });
  expect(resposta.status()).toBe(201);
}


test("histórico, estatísticas, PostgreSQL, API e grade CRUD funcionam em conjunto", async ({ page }) => {
  const historico = [
    [10, "2020-01-10", [10, 25, 26, 38, 50, 58]],
    [25, "2020-01-25", [1, 10, 20, 40, 41, 60]],
    [40, "2020-02-09", [10, 25, 26, 27, 50, 58]],
    [60, "2020-02-29", [10, 25, 26, 27, 28, 58]],
    [80, "2020-03-20", [25, 26, 27, 28, 29, 30]],
  ];
  for (const [numero, data, dezenas] of historico) {
    await incluirResultado(page, numero, data, dezenas);
  }

  const respostaPadroes = await page.request.get(`${origem}/api/padroes`);
  expect(await respostaPadroes.json()).toMatchObject({
    total: 9,
    padroes: [
      { padrao_cod: "PD_001", num_oco: 2, intervalo_medio: "15.000000", desv_padrao: "0.000000" },
      { padrao_cod: "PD_002", num_oco: 1, intervalo_medio: null, desv_padrao: null },
      { padrao_cod: "PD_003", num_oco: 2, intervalo_medio: "20.000000", desv_padrao: "0.000000" },
      { padrao_cod: "PD_004", num_oco: 1, intervalo_medio: null, desv_padrao: null },
      { padrao_cod: "PD_005", num_oco: 0, intervalo_medio: null, desv_padrao: null },
      { padrao_cod: "PD_006", num_oco: 0, intervalo_medio: null, desv_padrao: null },
      { padrao_cod: "PD_007", num_oco: 2, intervalo_medio: "15.000000", desv_padrao: "0.000000" },
      { padrao_cod: "PD_008", num_oco: 1, intervalo_medio: null, desv_padrao: null },
      { padrao_cod: "PD_009", num_oco: 2, intervalo_medio: "20.000000", desv_padrao: "0.000000" },
    ],
  });

  await page.goto(`${origem}/grupos-padroes.html`);
  await expect(page.locator("#corpo-tabela-grupos tr")).toHaveCount(3);
  await page.locator("#novo-grupo-nome").fill("Grupo temporário integrado");
  await page.locator("#novo-grupo-descr").fill("Criado pelo fluxo Chrome/PostgreSQL.");
  await page.locator("#botao-adicionar-grupo").click();
  await expect(page.locator('#corpo-tabela-grupos tr[data-codigo="PG_004"]')).toHaveCount(1);

  await page.goto(`${origem}/padroes.html`);
  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(9);
  const pd001 = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_001"]');
  await expect(pd001.locator("td").nth(4)).toHaveText("2");
  await expect(pd001.locator("td").nth(5)).toHaveText("15,000000");

  await pd001.locator("input").fill("Duas sequenciais — texto revisto");
  await pd001.locator('button[data-acao="salvar"]').click();
  await expect(page.locator("#mensagem-padroes")).toHaveText("PD_001 atualizado.");

  await incluirResultado(page, 90, "2020-03-30", [1, 3, 5, 7, 9, 11]);
  await page.reload();
  await expect(pd001.locator("input")).toHaveValue("Duas sequenciais — texto revisto");

  await page.locator("#novo-padrao-grupo").selectOption("PG_004");
  await page.locator("#novo-padrao-nome").fill("Padrão ainda sem função");
  await page.locator("#novo-padrao-descr").fill("Será implementado futuramente.");
  await page.locator("#botao-adicionar-padrao").click();
  const pd010 = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_010"]');
  await expect(pd010.locator("td").nth(7)).toHaveText("Pendente");
  await expect(pd010.locator("td").nth(4)).toHaveText("—");
  await expect(pd010.locator("select")).toHaveValue("PG_004");

  await pd010.locator("select").selectOption("PG_001");
  await pd010.locator("textarea").fill("Descrição revista antes da exclusão.");
  await pd010.locator('button[data-acao="salvar"]').click();
  await expect(page.locator("#mensagem-padroes")).toHaveText("PD_010 atualizado.");
  await expect(pd010.locator("select")).toHaveValue("PG_001");
  page.once("dialog", (dialogo) => dialogo.accept());
  await pd010.locator('button[data-acao="excluir"]').click();
  await expect(pd010).toHaveCount(0);

  await page.locator("#novo-padrao-nome").fill("Código seguinte");
  await page.locator("#novo-padrao-descr").fill("Não pode reutilizar PD_010.");
  await page.locator("#botao-adicionar-padrao").click();
  await expect(page.locator('#corpo-tabela-padroes tr[data-codigo="PD_011"]')).toHaveCount(1);

  const pd003 = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_003"]');
  page.once("dialog", (dialogo) => dialogo.accept());
  await pd003.locator('button[data-acao="excluir"]').click();
  await incluirResultado(page, 100, "2020-04-09", [2, 4, 6, 8, 10, 12]);
  await page.reload();
  await expect(pd003).toHaveCount(0);

  const final = await (await page.request.get(`${origem}/api/padroes`)).json();
  expect(final.padroes.map((item) => item.padrao_cod)).toEqual([
    "PD_001", "PD_002", "PD_004", "PD_005", "PD_006",
    "PD_007", "PD_008", "PD_009", "PD_011",
  ]);
  expect(final.padroes.at(-1)).toMatchObject({
    detector_implementado: false,
    num_oco: null,
    intervalo_medio: null,
    desv_padrao: null,
  });

  await page.goto(`${origem}/grupos-padroes.html`);
  const pg004 = page.locator('#corpo-tabela-grupos tr[data-codigo="PG_004"]');
  page.once("dialog", (dialogo) => dialogo.accept());
  await pg004.locator('button[data-acao="excluir"]').click();
  await expect(pg004).toHaveCount(0);
});
