import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";


const resultados = [
  {
    id_resultado: 1,
    numero_ap: 1,
    data_resultado: "1996-03-11",
    dezenas: [4, 5, 30, 33, 41, 52],
  },
  {
    id_resultado: 2,
    numero_ap: 2,
    data_resultado: "1996-03-18",
    dezenas: [9, 37, 39, 41, 43, 49],
  },
];
const padroesIniciais = [
  {
    id_padrao: 1, padrao_cod: "PD_001", padrao_nome: "Duas dezenas sequenciais",
    padrao_descr: "Maior grupo com duas dezenas.", num_oco: 1192,
    intervalo_medio: "2.575147", desv_padrao: "1.995592", detector_implementado: true,
  },
  {
    id_padrao: 2, padrao_cod: "PD_002", padrao_nome: "Três dezenas sequenciais",
    padrao_descr: "Maior grupo com três dezenas.", num_oco: 92,
    intervalo_medio: "33.527473", desv_padrao: "33.637806", detector_implementado: true,
  },
  {
    id_padrao: 3, padrao_cod: "PD_003", padrao_nome: "Mais de três dezenas sequenciais",
    padrao_descr: "Maior grupo com mais de três dezenas.", num_oco: 5,
    intervalo_medio: "680.500000", desv_padrao: "545.478460", detector_implementado: true,
  },
];
const raizFrontend = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
let servidor;


test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const caminhos = {
      "/": ["index.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/padroes.css": ["css/padroes.css", "text/css; charset=utf-8"],
      "/js/main.js": ["js/main.js", "text/javascript; charset=utf-8"],
      "/js/padroes.js": ["js/padroes.js", "text/javascript; charset=utf-8"],
    };
    const recurso = caminhos[requisicao.url];
    if (!recurso) {
      resposta.writeHead(404).end();
      return;
    }
    resposta.writeHead(200, { "Content-Type": recurso[1] });
    resposta.end(await readFile(path.join(raizFrontend, recurso[0])));
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(4173, "127.0.0.1", resolver);
  });
});


test.afterAll(async () => {
  await new Promise((resolver, rejeitar) => {
    servidor.close((erro) => (erro ? rejeitar(erro) : resolver()));
  });
});


async function simularApi(page) {
  let importacoes = 0;
  let padroes = structuredClone(padroesIniciais);
  await page.route("**/api/resultados", async (rota) => {
    await rota.fulfill({ json: { resultados, total: resultados.length } });
  });
  await page.route("**/api/resultados/importar", async (rota) => {
    importacoes += 1;
    await rota.fulfill({
      json: {
        mensagem: "Importação concluída: 0 resultado(s) inserido(s).",
        relatorio: { inseridas: 0, iguais: 2, alteradas: 0, invalidas: 0 },
      },
    });
  });
  await page.route("**/api/padroes**", async (rota) => {
    const requisicao = rota.request();
    const metodo = requisicao.method();
    const caminho = new URL(requisicao.url()).pathname;
    const codigo = caminho.split("/").at(-1);
    if (metodo === "GET") {
      await rota.fulfill({ json: { padroes, total: padroes.length } });
      return;
    }
    if (metodo === "POST") {
      const dados = requisicao.postDataJSON();
      const criado = {
        id_padrao: 4, padrao_cod: "PD_004", ...dados,
        num_oco: null, intervalo_medio: null, desv_padrao: null,
        detector_implementado: false,
      };
      padroes.push(criado);
      await rota.fulfill({ status: 201, json: { padrao: criado } });
      return;
    }
    if (metodo === "PUT") {
      const dados = requisicao.postDataJSON();
      const indice = padroes.findIndex((item) => item.padrao_cod === codigo);
      padroes[indice] = { ...padroes[indice], ...dados };
      await rota.fulfill({ json: { padrao: padroes[indice] } });
      return;
    }
    if (metodo === "DELETE") {
      const excluido = padroes.find((item) => item.padrao_cod === codigo);
      padroes = padroes.filter((item) => item.padrao_cod !== codigo);
      await rota.fulfill({ json: { padrao: excluido, mensagem: "Padrão excluído." } });
    }
  });
  return () => importacoes;
}


test("carrega, desenha, seleciona e navega circularmente", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");

  await expect(page.locator("#mensagem-sistema")).toHaveText("2 resultados carregados.");
  await expect(page.locator("#seletor-resultado option")).toHaveCount(2);
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await expect(page.locator("circle.marca-resultado")).toHaveCount(6);
  await expect(page.locator("circle.marca-media")).toHaveCount(1);

  await page.locator("#botao-anterior").click();
  await expect(page.locator("#jogo-numero")).toHaveText("2");
  await page.locator("#botao-proximo").click();
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await page.locator("#seletor-resultado").selectOption("1");
  await expect(page.locator("#jogo-numero")).toHaveText("2");
});


test("inicia, avança e pausa o voo", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");
  await page.locator("#tempo-voo").fill("0.1");
  await page.locator("#botao-voo").click();

  await expect(page.locator("#botao-voo")).toHaveText("Pausar voo dos pássaros");
  await expect(page.locator("#jogo-numero")).toHaveText("2", { timeout: 1_000 });
  await page.locator("#botao-voo").click();
  await expect(page.locator("#botao-voo")).toHaveText("Iniciar voo dos pássaros");
  await expect(page.locator("#mensagem-sistema")).toHaveText("Voo interrompido.");
});


test("seleciona Excel, importa, desenha mancha e limpa", async ({ page }) => {
  const totalImportacoes = await simularApi(page);
  await page.goto("/");
  const planilha = path.resolve("MSen/tests/fixtures/resultados_validos.xlsx");

  await page.locator("#arquivo-excel").setInputFiles(planilha);
  await expect(page.locator("#nome-arquivo")).toHaveText("resultados_validos.xlsx");
  await expect(page.locator("#botao-importar-excel")).toBeEnabled();
  await page.locator("#botao-importar-excel").click();
  await expect.poll(totalImportacoes).toBe(1);
  await expect(page.locator("#mensagem-sistema")).toHaveText(
    "Importação concluída: 0 inseridos, 2 iguais, 0 alterados e 0 inválidos.",
  );

  await page.locator("#botao-mancha").click();
  await expect(page.locator("circle.marca-mancha-resultado")).toHaveCount(12);
  await expect(page.locator("circle.marca-mancha-media")).toHaveCount(2);
  await expect(page.locator("#jogo-numero")).toHaveText("Todos");

  await page.locator("#botao-limpar").click();
  await expect(page.locator("#camada-marcas circle")).toHaveCount(0);
  await expect(page.locator("#mensagem-sistema")).toHaveText("Gráfico limpo.");
});


test("grade de padrões permite incluir, editar e excluir sem editar estatísticas", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");

  await expect(page.locator("#painel-padroes")).toBeHidden();
  await page.locator("#botao-cadastro-padroes").click();
  await expect(page.locator("#painel-padroes")).toBeVisible();
  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(3);
  await expect(page.locator("#mensagem-padroes")).toHaveText("3 padrão(ões) carregado(s).");

  const primeira = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_001"]');
  await expect(primeira.locator("input, textarea")).toHaveCount(2);
  await expect(primeira.locator("td").nth(3)).toHaveText("1192");
  await expect(primeira.locator("td").nth(4)).toHaveText("2,575147");

  await page.locator("#novo-padrao-nome").fill("Padrão futuro");
  await page.locator("#novo-padrao-descr").fill("Descrição para função futura.");
  await page.locator("#botao-adicionar-padrao").click();
  const nova = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_004"]');
  await expect(nova).toHaveCount(1);
  await expect(nova.locator("td").nth(3)).toHaveText("—");
  await expect(nova.locator("td").nth(6)).toHaveText("Pendente");

  await nova.locator("input").fill("Padrão futuro revisto");
  await nova.locator('button[data-acao="salvar"]').click();
  await expect(page.locator("#mensagem-padroes")).toHaveText("PD_004 atualizado.");
  await expect(nova.locator("input")).toHaveValue("Padrão futuro revisto");

  page.once("dialog", (dialogo) => dialogo.accept());
  await nova.locator('button[data-acao="excluir"]').click();
  await expect(nova).toHaveCount(0);
  await expect(page.locator("#mensagem-padroes")).toHaveText("PD_004 excluído.");

  await page.locator("#botao-fechar-padroes").click();
  await expect(page.locator("#painel-padroes")).toBeHidden();
});
