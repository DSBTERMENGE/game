import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";


const codigos = [
  "EST_SOMA", "EST_MEDIA", "EST_MEDIANA", "EST_DESVIO_PADRAO",
  "GEO_EXTENSAO_ABERTA", "GEO_PERIMETRO_FECHADO", "GEO_QUANTIDADE_REGIOES",
  "GEO_AREA_TOTAL", "GEO_CENTRO_GRAVIDADE_X", "GEO_CENTRO_GRAVIDADE_Y",
];
const raizFrontend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
let servidor;

test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, respostaHttp) => {
    const arquivos = {
      "/distribuicoes.html": ["distribuicoes.html", "text/html; charset=utf-8"],
      "/screener-prototipo.html": ["screener-prototipo.html", "text/html; charset=utf-8"],
      "/screener-prototipo.html": ["screener-prototipo.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/distribuicoes.css": ["css/distribuicoes.css", "text/css; charset=utf-8"],
      "/css/screener.css": ["css/screener.css", "text/css; charset=utf-8"],
      "/css/screener.css": ["css/screener.css", "text/css; charset=utf-8"],
      "/js/distribuicoes.js": ["js/distribuicoes.js", "text/javascript; charset=utf-8"],
      "/js/configuracao-distribuicoes.js": ["js/configuracao-distribuicoes.js", "text/javascript; charset=utf-8"],
      "/js/navegacao.js": ["js/navegacao.js", "text/javascript; charset=utf-8"],
      "/js/screener-prototipo.js": ["js/screener-prototipo.js", "text/javascript; charset=utf-8"],
      "/js/screener-prototipo-dados.js": ["js/screener-prototipo-dados.js", "text/javascript; charset=utf-8"],
      "/js/screener-prototipo.js": ["js/screener-prototipo.js", "text/javascript; charset=utf-8"],
      "/js/screener-prototipo-dados.js": ["js/screener-prototipo-dados.js", "text/javascript; charset=utf-8"],
    };
    const item = arquivos[new URL(requisicao.url, "http://127.0.0.1").pathname];
    if (!item) {
      respostaHttp.writeHead(404).end();
      return;
    }
    respostaHttp.writeHead(200, { "Content-Type": item[1] });
    respostaHttp.end(await readFile(path.join(raizFrontend, item[0])));
  });
  await new Promise((resolver, rejeitar) => {
    servidor.once("error", rejeitar);
    servidor.listen(4173, "127.0.0.1", resolver);
  });
});

test.afterAll(async () => {
  if (servidor) await new Promise((resolver) => servidor.close(resolver));
});

function parametro(codigo) {
  return {
    codigo,
    quantidade: 3069,
    ausentes: codigo.includes("CENTRO") ? 17 : 0,
    media: "30",
    desvio_padrao_populacional: "5",
    minimo: "10",
    maximo: "50",
    faixa: {
      metodo: "desvio_padrao", margem_inferior: "1", margem_superior: "1",
      limite_inferior: "25", limite_superior: "35", ativa_no_screener: false,
    },
    histograma: Array.from({ length: 10 }, (_, indice) => ({
      limite_inferior: String(10 + 4 * indice),
      limite_superior: String(14 + 4 * indice),
      frequencia: 100 + indice * 20,
      percentual: String(3 + indice),
    })),
    curva_normal_referencia: {
      disponivel: true,
      uso: "REFERENCIA_VISUAL",
      pontos: Array.from({ length: 10 }, (_, indice) => ({
        x: String(12 + 4 * indice),
        densidade: String(0.01 + 0.005 * Math.min(indice, 9 - indice)),
      })),
    },
  };
}

const resposta = {
  distribuicoes: {
    janela: {
      quantidade_resultados: 3069, numero_ap_inicial: 1, numero_ap_final: 3069,
      data_inicial: "1996-03-11", data_final: "2026-10-24", corte_exclusivo: true,
    },
    parametros: codigos.map(parametro),
    ativa_no_screener: false,
  },
};

async function abrir(page, largura) {
  await page.setViewportSize({ width: largura, height: 820 });
  await page.route("**/api/perfis/distribuicoes*", (rota) => rota.fulfill({
    status: 200, contentType: "application/json", body: JSON.stringify(resposta),
  }));
  await page.goto("/distribuicoes.html");
  await expect(page.locator(".cartao-distribuicao")).toHaveCount(10);
  await expect(page.locator("#mensagem-distribuicoes")).toHaveText("Perfis históricos carregados.");
}

test("mostra os dez gráficos juntos e mantém o screener inativo", async ({ page }) => {
  await abrir(page, 1280);
  await expect(page.locator(".grafico-distribuicao")).toHaveCount(10);
  await expect(page.locator(".grafico-barra")).toHaveCount(100);
  await expect(page.locator(".grafico-normal")).toHaveCount(10);
  await expect(page.locator(".screener-inativo")).toContainText("screener inativo");
  await expect(page.locator("#resumo-amostra")).toHaveText("3.069");
});

test("calcula prévia antes de salvar e recupera o estudo no navegador", async ({ page }) => {
  const consultas = [];
  await page.setViewportSize({ width: 1280, height: 820 });
  await page.route("**/api/perfis/distribuicoes*", (rota) => {
    consultas.push(new URL(rota.request().url()).searchParams.toString());
    return rota.fulfill({
      status: 200, contentType: "application/json", body: JSON.stringify(resposta),
    });
  });
  await page.goto("/distribuicoes.html");
  await page.locator("#botao-configurar-faixas").click();
  await expect(page.locator("#dialogo-configuracao-faixas")).toBeVisible();
  await page.locator("#config-metodo-faixa").selectOption("percentual_media");
  await page.locator("#config-margem-inferior").fill("10");
  await page.locator("#config-margem-superior").fill("20");
  await expect(page.locator("#botao-salvar-configuracao")).toBeDisabled();
  await page.locator("#botao-calcular-previa").click();
  await expect(page.locator("#corpo-previa-faixas tr")).toHaveCount(10);
  await expect(page.locator("#botao-salvar-configuracao")).toBeEnabled();
  await page.locator("#botao-salvar-configuracao").click();
  await expect(page.locator("#dialogo-configuracao-faixas")).not.toBeVisible();
  await expect(page.locator("#mensagem-distribuicoes")).toContainText("screener inativo");
  expect(consultas.at(-1)).toContain("metodo_faixa=percentual_media");
  expect(consultas.at(-1)).toContain("margem_inferior=10");
  expect(consultas.at(-1)).toContain("margem_superior=20");

  await page.reload();
  await page.locator("#botao-configurar-faixas").click();
  await expect(page.locator("#config-metodo-faixa")).toHaveValue("percentual_media");
  await expect(page.locator("#config-margem-inferior")).toHaveValue("10");
  await expect(page.locator("#config-margem-superior")).toHaveValue("20");
});

for (const largura of [1280, 760]) {
  test(`grade permanece contida na janela com ${largura}px`, async ({ page }) => {
    await abrir(page, largura);
    const medidas = await page.locator("#grade-distribuicoes").evaluate((elemento) => ({
      direita: elemento.getBoundingClientRect().right,
      inferior: elemento.getBoundingClientRect().bottom,
      larguraDocumento: document.documentElement.clientWidth,
      alturaDocumento: document.documentElement.clientHeight,
      rolagemVertical: elemento.scrollHeight > elemento.clientHeight,
    }));
    expect(medidas.direita).toBeLessThanOrEqual(medidas.larguraDocumento + 1);
    expect(medidas.inferior).toBeLessThanOrEqual(medidas.alturaDocumento + 1);
    expect(medidas.rolagemVertical).toBeTruthy();
  });
}

test("protótipo mostra o funil compacto e expande detalhes sem API", async ({ page }) => {
  let requisicoesApi = 0;
  page.on("request", (requisicao) => {
    if (requisicao.url().includes("/api/")) requisicoesApi += 1;
  });
  await page.setViewportSize({ width: 1280, height: 820 });
  await page.goto("/screener-prototipo.html");
  await expect(page.locator(".prototipo-nivel")).toHaveCount(3);
  await expect(page.locator("#prototipo-total-inicial")).toHaveText("50.063.860");
  await expect(page.locator("#prototipo-total-aprovado")).toHaveText("25.344.829");
  await expect(page.locator("#prototipo-reconciliacao")).toContainText("Fechamento correto");
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(0);
  await page.locator("#botao-abrir-todos").click();
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(3);
  await expect(page.locator(".prototipo-detalhes tbody tr")).toHaveCount(12);
  await page.locator("#botao-fechar-todos").click();
  await expect(page.locator(".prototipo-nivel[open]")).toHaveCount(0);
  expect(requisicoesApi).toBe(0);
});
