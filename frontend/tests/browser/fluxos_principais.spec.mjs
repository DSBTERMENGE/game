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
    dezenas: [1, 2, 3, 10, 11, 20],
    analise_geometrica: {
      vertices: [
        { x: "0", y: "0" }, { x: "1", y: "0" }, { x: "2", y: "0" },
        { x: "9", y: "0" }, { x: "0", y: "1" }, { x: "9", y: "1" },
      ],
      regioes: [
        [{ x: "0", y: "0" }, { x: "9", y: "0" }, { x: "4.5", y: "0.5" }],
        [{ x: "0", y: "1" }, { x: "4.5", y: "0.5" }, { x: "9", y: "1" }],
      ],
      quantidade_regioes: 2,
      extensao_aberta: "27.055385",
      perimetro_fechado: "36.110770",
      area_total: "4.5",
      centro_gravidade: { x: "4.5", y: "0.5" },
      poligono_2: {
        vertices: [
          { x: "0", y: "0" }, { x: "2", y: "0" }, { x: "9", y: "0" },
          { x: "9", y: "1" }, { x: "0", y: "1" }, { x: "1", y: "0" },
        ],
        area: "8.5",
        centro_gravidade: { x: "4.5", y: "0.5" },
      },
    },
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
    id_grupo: 1, grupo_cod: "PG_001", grupo_nome: "Dezenas sequenciais",
    padrao_descr: "Maior grupo com duas dezenas.", num_oco: 1192,
    intervalo_medio: "2.575147", desv_padrao: "1.995592", detector_implementado: true,
  },
  {
    id_padrao: 2, padrao_cod: "PD_002", padrao_nome: "Três dezenas sequenciais",
    id_grupo: 1, grupo_cod: "PG_001", grupo_nome: "Dezenas sequenciais",
    padrao_descr: "Maior grupo com três dezenas.", num_oco: 92,
    intervalo_medio: "33.527473", desv_padrao: "33.637806", detector_implementado: true,
  },
  {
    id_padrao: 3, padrao_cod: "PD_003", padrao_nome: "Mais de três dezenas sequenciais",
    id_grupo: 1, grupo_cod: "PG_001", grupo_nome: "Dezenas sequenciais",
    padrao_descr: "Maior grupo com mais de três dezenas.", num_oco: 5,
    intervalo_medio: "680.500000", desv_padrao: "545.478460", detector_implementado: true,
  },
];
const raizFrontend = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
let servidor;
const porta = Number(process.env.PLAYWRIGHT_TEST_PORT || 4173);


test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const caminhos = {
      "/": ["index.html", "text/html; charset=utf-8"],
      "/cadastros.html": ["cadastros.html", "text/html; charset=utf-8"],
      "/grupos-padroes.html": ["grupos-padroes.html", "text/html; charset=utf-8"],
      "/padroes.html": ["padroes.html", "text/html; charset=utf-8"],
      "/screener.html": ["screener.html", "text/html; charset=utf-8"],
      "/auditoria.html": ["auditoria.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/crud-navegavel.css": ["css/crud-navegavel.css", "text/css; charset=utf-8"],
      "/css/grupos-padroes.css": ["css/grupos-padroes.css", "text/css; charset=utf-8"],
      "/css/padroes.css": ["css/padroes.css", "text/css; charset=utf-8"],
      "/css/screener.css": ["css/screener.css", "text/css; charset=utf-8"],
      "/css/auditoria.css": ["css/auditoria.css", "text/css; charset=utf-8"],
      "/js/main.js": ["js/main.js", "text/javascript; charset=utf-8"],
      "/js/configuracao-visual.js": ["js/configuracao-visual.js", "text/javascript; charset=utf-8"],
      "/js/navegacao.js": ["js/navegacao.js", "text/javascript; charset=utf-8"],
      "/js/crud-navegavel.js": ["js/crud-navegavel.js", "text/javascript; charset=utf-8"],
      "/js/grupos-padroes.js": ["js/grupos-padroes.js", "text/javascript; charset=utf-8"],
      "/js/grupos-padroes-api.js": ["js/grupos-padroes-api.js", "text/javascript; charset=utf-8"],
      "/js/padroes.js": ["js/padroes.js", "text/javascript; charset=utf-8"],
      "/js/padroes-api.js": ["js/padroes-api.js", "text/javascript; charset=utf-8"],
      "/js/screener-extensivel.js": ["js/screener-extensivel.js", "text/javascript; charset=utf-8"],
      "/js/screener-extensivel-contrato.js": ["js/screener-extensivel-contrato.js", "text/javascript; charset=utf-8"],
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
    servidor.listen(porta, "127.0.0.1", resolver);
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
  await page.route(/\/api\/resultados(?:\?.*)?$/, async (rota) => {
    await rota.fulfill({ json: { resultados, total: resultados.length } });
  });
  await page.route(/\/api\/resultados\/\d+\/geometria$/, async (rota) => {
    await rota.fulfill({
      json: {
        numero_ap: 2,
        analise_geometrica: resultados[0].analise_geometrica,
      },
    });
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
      const grupo = new URL(requisicao.url()).searchParams.get("grupo_cod");
      const filtrados = grupo ? padroes.filter((item) => item.grupo_cod === grupo) : padroes;
      await rota.fulfill({ json: { padroes: filtrados, total: filtrados.length } });
      return;
    }
    if (metodo === "POST") {
      const dados = requisicao.postDataJSON();
      const criado = {
        id_padrao: 4, padrao_cod: "PD_004", ...dados,
        id_grupo: dados.grupo_cod === "PG_001" ? 1 : 2,
        grupo_nome: dados.grupo_cod === "PG_001" ? "Dezenas sequenciais" : "Mesma coluna",
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


async function simularApiGrupos(page, incluirSegundo = false) {
  let grupos = [{
    id_grupo: 1,
    grupo_cod: "PG_001",
    grupo_nome: "Dezenas sequenciais",
    grupo_descr: "Padrões baseados em dezenas consecutivas.",
  }];
  if (incluirSegundo) grupos.push({
    id_grupo: 2,
    grupo_cod: "PG_002",
    grupo_nome: "Mesma coluna",
    grupo_descr: "Padrões baseados em dezenas na mesma coluna.",
  });
  await page.route("**/api/grupos-padroes**", async (rota) => {
    const requisicao = rota.request();
    const metodo = requisicao.method();
    const codigo = new URL(requisicao.url()).pathname.split("/").at(-1);
    if (metodo === "GET") {
      await rota.fulfill({ json: { grupos, total: grupos.length } });
      return;
    }
    if (metodo === "POST") {
      const dados = requisicao.postDataJSON();
      const criado = { id_grupo: 2, grupo_cod: "PG_002", ...dados };
      grupos.push(criado);
      await rota.fulfill({ status: 201, json: { grupo: criado } });
      return;
    }
    if (metodo === "PUT") {
      const dados = requisicao.postDataJSON();
      const indice = grupos.findIndex((item) => item.grupo_cod === codigo);
      grupos[indice] = { ...grupos[indice], ...dados };
      await rota.fulfill({ json: { grupo: grupos[indice] } });
      return;
    }
    if (metodo === "DELETE") {
      if (codigo === "PG_001") {
        await rota.fulfill({
          status: 409,
          json: { erro: { codigo: "GRUPO_EM_USO", mensagem: "O grupo possui padrões e não pode ser excluído." } },
        });
        return;
      }
      const excluido = grupos.find((item) => item.grupo_cod === codigo);
      grupos = grupos.filter((item) => item.grupo_cod !== codigo);
      await rota.fulfill({ json: { grupo: excluido, mensagem: "Grupo excluído." } });
    }
  });
}


async function simularPerfilPadroes(page) {
  const consultas = [];
  await page.route("**/api/grupos-padroes/PG_001/perfil**", async (rota) => {
    consultas.push(new URL(rota.request().url()).searchParams.toString());
    await rota.fulfill({ json: { perfil: {
      grupo_cod: "PG_001",
      amostra: {
        total_resultados: 3069, total_classificados: 1289,
        numero_ap_inicial: 1, numero_ap_final: 3069,
        data_inicial: "1996-03-11", data_final: "2026-10-25",
      },
      raridade: {
        limite_percentual: "10.000000", operador: "<",
        padroes_indicados: ["PD_002", "PD_003"], ativa_no_screener: false,
      },
      versoes_calculo: [1],
      classes: [
        { padrao_cod: "PD_001", quantidade: 1192, percentual_total: "38.840013", percentual_classificados: "92.474787", intervalo_medio: "2.575147", desvio_padrao: "1.995592", raro: false },
        { padrao_cod: "PD_002", quantidade: 92, percentual_total: "2.997719", percentual_classificados: "7.137316", intervalo_medio: "33.527473", desvio_padrao: "33.637806", raro: true },
        { padrao_cod: "PD_003", quantidade: 5, percentual_total: "0.162920", percentual_classificados: "0.387898", intervalo_medio: "680.500000", desvio_padrao: "545.478460", raro: true },
      ],
    } } });
  });
  return consultas;
}


async function simularCatalogoExtenso(page) {
  const grupos = Array.from({ length: 30 }, (_, indice) => ({
    id_grupo: indice + 1,
    grupo_cod: `PG_${String(indice + 1).padStart(3, "0")}`,
    grupo_nome: `Grupo conceitual ${indice + 1}`,
    grupo_descr: `Descrição detalhada do grupo conceitual ${indice + 1}.`,
  }));
  const padroes = Array.from({ length: 45 }, (_, indice) => ({
    id_padrao: indice + 1,
    id_grupo: (indice % grupos.length) + 1,
    grupo_cod: grupos[indice % grupos.length].grupo_cod,
    grupo_nome: grupos[indice % grupos.length].grupo_nome,
    padrao_cod: `PD_${String(indice + 1).padStart(3, "0")}`,
    padrao_nome: `Padrão estatístico ${indice + 1}`,
    padrao_descr: `Descrição detalhada do padrão estatístico ${indice + 1}.`,
    num_oco: indice * 3,
    intervalo_medio: "12.500000",
    desv_padrao: "2.250000",
    detector_implementado: indice < 3,
  }));
  await page.route("**/api/grupos-padroes**", (rota) => rota.fulfill({
    json: { grupos, total: grupos.length },
  }));
  await page.route("**/api/padroes**", (rota) => {
    const grupo = new URL(rota.request().url()).searchParams.get("grupo_cod");
    const itens = grupo ? padroes.filter((item) => item.grupo_cod === grupo) : padroes;
    return rota.fulfill({ json: { padroes: itens, total: itens.length } });
  });
}


test("carrega, desenha, seleciona e navega circularmente", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");

  await expect(page.locator("#mensagem-sistema")).toHaveText("2 resultados carregados.");
  await expect(page.locator("#seletor-resultado option")).toHaveCount(2);
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await expect(page.locator("circle.marca-resultado")).toHaveCount(6);
  await expect(page.locator("circle.marca-media")).toHaveCount(1);
  await expect(page.locator("polyline.linha-geometrica")).toHaveCount(1);
  await expect(page.locator("polygon.poligono-1-geometrico")).toHaveCount(1);
  await expect(page.locator("polygon.regiao-geometrica")).toHaveCount(2);
  await expect(page.locator("circle.centro-gravidade")).toHaveCount(1);
  await expect(page.locator("#resumo-geometrico")).toContainText("Área P1: 4,500");
  await expect(page.locator("#resumo-geometrico")).toContainText("Área P2: 8,500");
  await expect(page.locator("polygon.poligono-2-geometrico")).toHaveCount(1);
  await page.locator("#voo-mostrar-poligono-2").uncheck();
  await expect(page.locator("polygon.poligono-2-geometrico")).toHaveCount(0);
  await page.locator("#voo-mostrar-poligono-2").check();

  await page.locator("#botao-anterior").click();
  await expect(page.locator("#jogo-numero")).toHaveText("2");
  await page.locator("#botao-proximo").click();
  await expect(page.locator("#jogo-numero")).toHaveText("1");
  await page.locator("#seletor-resultado").selectOption("1");
  await expect(page.locator("#jogo-numero")).toHaveText("2");
});


test("configuração visual persiste após recarregar a página", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");
  await page.locator("#botao-aparencia").click();
  await expect(page.locator("#dialogo-aparencia")).toBeVisible();
  await page.locator("#cor-linha").fill("#123456");
  await page.locator("#espessura-linhas").fill("1.5");
  await page.locator("#mostrar-regioes").uncheck();
  await page.locator('#form-aparencia button[type="submit"]').click();
  await expect(page.locator("#dialogo-aparencia")).not.toBeVisible();

  await page.reload();
  await page.locator("#botao-aparencia").click();
  await expect(page.locator("#cor-linha")).toHaveValue("#123456");
  await expect(page.locator("#espessura-linhas")).toHaveValue("1.5");
  await expect(page.locator("#mostrar-regioes")).not.toBeChecked();
  const corAplicada = await page.locator("#mapa-dezenas").evaluate(
    (elemento) => elemento.style.getPropertyValue("--cor-linha-geometrica"),
  );
  expect(corAplicada).toBe("#123456");
});

test("Linha Poligonal e Polígono 1 podem ser exibidos separadamente", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");

  await page.locator("#botao-aparencia").click();
  await page.locator("#mostrar-linha").uncheck();
  await page.locator("#mostrar-poligono-1").check();
  await page.locator('#form-aparencia button[type="submit"]').click();
  await expect(page.locator("polyline.linha-geometrica")).toHaveCount(0);
  await expect(page.locator("polygon.poligono-1-geometrico")).toHaveCount(1);

  await page.locator("#botao-aparencia").click();
  await page.locator("#mostrar-linha").check();
  await page.locator("#mostrar-poligono-1").uncheck();
  await page.locator('#form-aparencia button[type="submit"]').click();
  await expect(page.locator("polyline.linha-geometrica")).toHaveCount(1);
  await expect(page.locator("polygon.poligono-1-geometrico")).toHaveCount(0);
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
  await expect(page.locator("circle.marca-ocorrencia-dezena")).toHaveCount(12);
  await expect(page.locator("circle.marca-mancha-media")).toHaveCount(2);
  const aparenciaRestaurada = await page.locator("circle.marca-mancha-media").first().evaluate((circulo) => ({
    raio: circulo.getAttribute("r"),
    cor: getComputedStyle(circulo).fill,
    opacidade: getComputedStyle(circulo).fillOpacity,
  }));
  expect(Number(aparenciaRestaurada.raio)).toBeCloseTo((3 / 25.4) * 96 / 2, 8);
  expect(aparenciaRestaurada.cor).toBe("rgb(230, 126, 34)");
  expect(aparenciaRestaurada.opacidade).toBe("0.28");
  await expect(page.locator("#jogo-numero")).toHaveText("Todos");

  await page.locator("#botao-limpar").click();
  await expect(page.locator("#camada-marcas circle")).toHaveCount(0);
  await expect(page.locator("#mensagem-sistema")).toHaveText("Gráfico limpo.");
});


test("menu horizontal navega entre Painel e páginas de Cadastros", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");
  await expect(page.locator(".barra-navegacao")).toBeVisible();
  await page.locator(".navegacao-menu summary").click();
  const menu = page.locator(".navegacao-menu nav");
  await expect(menu).toBeVisible();
  await expect.poll(() => page.locator(".navegacao-menu").evaluate(
    (elemento) => elemento.style.getPropertyValue("--navegacao-menu-top"),
  )).not.toBe("");
  const posicao = await page.evaluate(() => {
    const barra = document.querySelector(".barra-navegacao").getBoundingClientRect();
    const elemento = document.querySelector(".navegacao-menu nav");
    const painel = elemento.getBoundingClientRect();
    return {
      barraFim: barra.bottom,
      painelFim: painel.bottom,
      posicao: getComputedStyle(elemento).position,
    };
  });
  expect(posicao.posicao).toBe("fixed");
  expect(posicao.painelFim).toBeGreaterThan(posicao.barraFim);

  await menu.getByRole("link", { name: "Grupo", exact: true }).click();
  await expect(page).toHaveURL(/grupos-padroes\.html$/);
  await expect(page.locator('[aria-current="page"]')).toHaveText("Grupo");

  await page.locator(".navegacao-menu summary").click();
  await page.locator(".navegacao-menu nav").getByRole("link", { name: "Padrões", exact: true }).click();
  await expect(page).toHaveURL(/padroes\.html$/);
  await expect(page.locator('[aria-current="page"]')).toHaveText("Padrões");

  await page.goto("/cadastros.html");
  await expect(page).toHaveURL(/grupos-padroes\.html$/);

  await page.locator('a[href="/auditoria.html"]').click();
  await expect(page).toHaveURL(/auditoria\.html$/);
  await expect(page.locator('[aria-current="page"]')).toHaveText("Validação e auditoria");
  await expect(page.getByRole("heading", { name: "Validação e auditoria" })).toBeVisible();
  await expect(page.getByText("Relatório por função")).toBeVisible();
  await page.setViewportSize({ width: 700, height: 600 });
  const larguraAuditoria = await page.evaluate(() => ({
    documento: document.documentElement.scrollWidth,
    janela: window.innerWidth,
  }));
  expect(larguraAuditoria.documento).toBeLessThanOrEqual(larguraAuditoria.janela);
});


test("cadastro de grupos permite localizar, incluir, editar e excluir com confirmação", async ({ page }) => {
  await simularApiGrupos(page);
  await page.goto("/grupos-padroes.html");

  const seletor = page.getByLabel("Registro", { exact: true });
  const contador = page.locator("[data-contador-registros]");
  await expect(seletor).toContainText("Dezenas sequenciais");
  await expect(contador).toHaveText("1 registro(s) encontrado(s)");
  const organizacao = await page.evaluate(() => {
    const seletor = document.querySelector(".crud-navegavel__seletor").getBoundingClientRect();
    const novo = document.querySelector(".crud-navegavel__novo").getBoundingClientRect();
    const formulario = document.querySelector("[data-formulario]").getBoundingClientRect();
    const contador = document.querySelector("[data-contador-registros]").getBoundingClientRect();
    return { seletorFim: seletor.bottom, novoTopo: novo.top, formularioTopo: formulario.top, contadorTopo: contador.top };
  });
  expect(organizacao.novoTopo).toBeGreaterThanOrEqual(organizacao.seletorFim);
  expect(organizacao.formularioTopo).toBeGreaterThanOrEqual(organizacao.novoTopo);
  expect(organizacao.contadorTopo).toBeLessThan(organizacao.seletorFim);

  await page.getByRole("button", { name: "Novo registro" }).click();
  await page.getByLabel("Nome do grupo").fill("Mesma coluna");
  await page.getByLabel("Descrição").fill("Padrões na mesma coluna.");
  await page.getByRole("button", { name: "Salvar registro" }).click();
  await page.getByRole("button", { name: "Sim, salvar registro" }).click();
  await expect(seletor).toContainText("Mesma coluna");

  await page.getByLabel("Localizar").fill("Mesma");
  await expect(page.locator("[data-contador-registros]")).toHaveText("1 registro(s) encontrado(s)");
  await expect(seletor.locator("option")).toHaveCount(2);
  await page.getByLabel("Localizar").fill("");
  await expect(page.locator("[data-contador-registros]")).toHaveText("2 registro(s) encontrado(s)");
  await seletor.selectOption({ label: "Mesma coluna" });

  await page.getByRole("button", { name: "Editar" }).click();
  await page.getByLabel("Nome do grupo").fill("Mesma coluna da matriz");
  await page.getByRole("button", { name: "Salvar registro" }).click();
  await page.getByRole("button", { name: "Sim, salvar registro" }).click();
  await expect(seletor).toContainText("Mesma coluna da matriz");

  await page.getByRole("button", { name: "Excluir" }).click();
  await page.getByRole("button", { name: "Sim, excluir registro" }).click();
  await expect(seletor).not.toContainText("Mesma coluna da matriz");

  await seletor.selectOption({ label: "Dezenas sequenciais" });
  await page.getByRole("button", { name: "Excluir" }).click();
  await page.getByRole("button", { name: "Sim, excluir registro" }).click();
  await expect(seletor).toContainText("Dezenas sequenciais");
  await expect(page.locator(".crud-navegavel__mensagem")).toHaveText(
    "O grupo possui padrões e não pode ser excluído.",
  );
});


test("cadastro de Padrões filtra pelo Grupo e preserva o relacionamento", async ({ page }) => {
  await simularApi(page);
  await simularApiGrupos(page, true);
  await page.goto("/padroes.html");

  const grupo = page.locator('[data-filtro="grupo_cod"]');
  const padrao = page.locator("[data-seletor-registro]");
  await expect(page.getByRole("button", { name: "Novo registro" })).toBeDisabled();
  await grupo.selectOption("PG_001");
  await expect(padrao.locator("option")).toHaveCount(4);
  await expect(padrao).toContainText("Duas dezenas sequenciais");

  await grupo.selectOption("PG_002");
  await expect(page.locator("[data-contador-registros]")).toHaveText("0 registro(s) encontrado(s)");
  await page.getByRole("button", { name: "Novo registro" }).click();
  await page.getByLabel("Nome do padrão").fill("Duas dezenas na coluna");
  await page.getByLabel("Descrição").fill("Descrição futura.");
  await page.getByRole("button", { name: "Salvar registro" }).click();
  await page.getByRole("button", { name: "Sim, salvar registro" }).click();
  await expect(padrao).toContainText("Duas dezenas na coluna");

  await grupo.selectOption("PG_001");
  await expect(padrao).not.toContainText("Duas dezenas na coluna");
  await expect(page.locator("#tabela-padroes, #perfil-padroes")).toHaveCount(0);
});


test("cadastro de Padrões não exibe dados estatísticos", async ({ page }) => {
  await simularApi(page);
  await simularApiGrupos(page, true);
  await page.goto("/padroes.html");
  await expect(page.getByText("Ocorrências", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Intervalo médio", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Desvio-padrão", { exact: true })).toHaveCount(0);
});


test("página de Padrões conserva espaço com muitos registros", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await simularCatalogoExtenso(page);
  await page.goto("/padroes.html");
  await page.locator('[data-filtro="grupo_cod"]').selectOption("PG_001");
  await expect(page.locator("[data-contador-registros]")).toHaveText(/^[1-9][0-9]* registro\(s\) encontrado\(s\)$/);

  const antes = await page.evaluate(() => {
    const barra = document.querySelector(".barra-navegacao").getBoundingClientRect();
    const pagina = document.querySelector(".pagina-conteudo").getBoundingClientRect();
    const grade = document.querySelector(".crud-navegavel__corpo");
    return {
      alturaBarra: barra.height,
      topoPagina: pagina.top,
      corpoLargura: document.documentElement.scrollWidth,
      janelaLargura: window.innerWidth,
      gradeDireita: grade.getBoundingClientRect().right,
      gradeBaixo: grade.getBoundingClientRect().bottom,
      gradeAltura: grade.clientHeight,
    };
  });
  expect(antes.alturaBarra).toBeLessThanOrEqual(46);
  expect(antes.corpoLargura).toBeLessThanOrEqual(antes.janelaLargura);
  expect(antes.gradeDireita).toBeLessThanOrEqual(1280);
  expect(antes.gradeBaixo).toBeLessThanOrEqual(720);
  expect(antes.gradeAltura).toBeGreaterThan(100);

  await page.locator(".navegacao-menu summary").click();
  const depoisMenu = await page.evaluate(() => ({
    alturaBarra: document.querySelector(".barra-navegacao").getBoundingClientRect().height,
    topoPagina: document.querySelector(".pagina-conteudo").getBoundingClientRect().top,
  }));
  expect(depoisMenu.alturaBarra).toBe(antes.alturaBarra);
  expect(depoisMenu.topoPagina).toBe(antes.topoPagina);

});


test("páginas compactas não alargam a janela estreita", async ({ page }) => {
  await page.setViewportSize({ width: 700, height: 600 });
  await simularCatalogoExtenso(page);
  for (const caminho of ["/grupos-padroes.html", "/padroes.html"]) {
    await page.goto(caminho);
    if (caminho === "/padroes.html") await page.locator('[data-filtro="grupo_cod"]').selectOption("PG_001");
    const medidas = await page.evaluate(() => {
      const grade = document.querySelector(".crud-navegavel__corpo");
      const barraFormulario = document.querySelector(".crud-navegavel__consulta");
      return {
        documento: document.documentElement.scrollWidth,
        janela: window.innerWidth,
        barraRola: barraFormulario.scrollWidth > barraFormulario.clientWidth,
        gradeRola: grade.scrollWidth > grade.clientWidth,
        gradeDireita: grade.getBoundingClientRect().right,
        gradeBaixo: grade.getBoundingClientRect().bottom,
      };
    });
    expect(medidas.documento).toBeLessThanOrEqual(medidas.janela);
    expect(medidas.gradeDireita).toBeLessThanOrEqual(700);
    expect(medidas.gradeBaixo).toBeLessThanOrEqual(600);
  }
});


test("menu Screener abre diretamente o funil oficial em três níveis", async ({ page }) => {
  await page.goto("/screener.html");
  await expect(page.locator("h1")).toHaveText("Sistema de preparação e aplicação do Screener");
  await expect(page.locator('[aria-current="page"]')).toHaveText("Preparação do Screener");
  await expect(page.locator("#botao-executar-extensivel")).toHaveText("Iniciar teste");
  await expect(page.locator("#corpo-validacoes-screener")).toHaveCount(0);
  await expect(page.getByText("Abrir novo funil")).toHaveCount(0);
  await expect(page.getByText("Screener atual")).toHaveCount(0);

  const medidas = await page.evaluate(() => ({
    documento: document.documentElement.scrollWidth,
    janela: window.innerWidth,
    barra: document.querySelector(".barra-navegacao").getBoundingClientRect().height,
    painelDireita: document.querySelector("#extensivel-niveis").getBoundingClientRect().right,
  }));
  expect(medidas.documento).toBeLessThanOrEqual(medidas.janela);
  expect(medidas.barra).toBeLessThanOrEqual(46);
  expect(medidas.painelDireita).toBeLessThanOrEqual(medidas.janela + 1);
});
