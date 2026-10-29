import { expect, test } from "@playwright/test";
import { execFileSync, spawn } from "node:child_process";
import path from "node:path";


const nomeBanco = `games_test_7_1_${process.pid}`;
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
      const resposta = await fetch("http://127.0.0.1:5052/api/saude");
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
      "from dotenv import load_dotenv; load_dotenv(); from msen.api import criar_app; criar_app().run(host='127.0.0.1', port=5052, debug=False, use_reloader=False)",
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


test("Excel percorre API, cálculos, PostgreSQL e relatório sem duplicar", async ({ page }) => {
  await page.goto("http://127.0.0.1:5052/");
  await expect(page.locator("#mensagem-sistema")).toHaveText("Nenhum resultado foi carregado.");
  const planilha = path.join(pastaMSen, "tests", "fixtures", "resultados_validos.xlsx");

  await page.locator("#arquivo-excel").setInputFiles(planilha);
  await page.locator("#botao-importar-excel").click();
  await expect(page.locator("#mensagem-sistema")).toHaveText(
    "Importação concluída: 2 inseridos, 0 iguais, 0 alterados e 0 inválidos.",
    { timeout: 15_000 },
  );
  await expect(page.locator("#seletor-resultado option")).toHaveCount(2);

  const resposta = await page.request.get("http://127.0.0.1:5052/api/resultados");
  const corpo = await resposta.json();
  expect(corpo.total).toBe(2);
  expect(corpo.resultados[0]).toMatchObject({
    numero_ap: 100,
    dezenas: [1, 10, 20, 30, 40, 60],
    soma_res: 161,
    media_aritmetica_res: "26.833333",
    mediana_res: "25.0",
  });

  const resumoInicial = JSON.parse(banco("resumo"));
  expect(resumoInicial).toEqual({ resultados: 2, frequencias: 60, ocorrencias: 12 });
  expect(JSON.parse(banco("resumo_padroes"))).toEqual([
    { padrao_cod: "PD_001", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
    { padrao_cod: "PD_002", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
    { padrao_cod: "PD_003", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
    { padrao_cod: "PD_004", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
    { padrao_cod: "PD_005", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
    { padrao_cod: "PD_006", num_oco: 2, intervalo_medio: "1.000000", desv_padrao: "0.000000", total_sorteios: 2, percentual_ocorrencia: "100.000000" },
    { padrao_cod: "PD_007", num_oco: 1, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "50.000000" },
    { padrao_cod: "PD_008", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
    { padrao_cod: "PD_009", num_oco: 0, intervalo_medio: null, desv_padrao: null, total_sorteios: 2, percentual_ocorrencia: "0.000000" },
  ]);

  await page.locator("#botao-importar-excel").click();
  await expect(page.locator("#mensagem-sistema")).toHaveText(
    "Importação concluída: 0 inseridos, 2 iguais, 0 alterados e 0 inválidos.",
  );
  expect(JSON.parse(banco("resumo"))).toEqual(resumoInicial);
});
