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


test.beforeAll(async () => {
  servidor = http.createServer(async (requisicao, resposta) => {
    const caminhos = {
      "/": ["index.html", "text/html; charset=utf-8"],
      "/cadastros.html": ["cadastros.html", "text/html; charset=utf-8"],
      "/grupos-padroes.html": ["grupos-padroes.html", "text/html; charset=utf-8"],
      "/padroes.html": ["padroes.html", "text/html; charset=utf-8"],
      "/css/style.css": ["css/style.css", "text/css; charset=utf-8"],
      "/css/navegacao.css": ["css/navegacao.css", "text/css; charset=utf-8"],
      "/css/grupos-padroes.css": ["css/grupos-padroes.css", "text/css; charset=utf-8"],
      "/css/padroes.css": ["css/padroes.css", "text/css; charset=utf-8"],
      "/js/main.js": ["js/main.js", "text/javascript; charset=utf-8"],
      "/js/navegacao.js": ["js/navegacao.js", "text/javascript; charset=utf-8"],
      "/js/grupos-padroes.js": ["js/grupos-padroes.js", "text/javascript; charset=utf-8"],
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


test("menu horizontal navega entre Painel e páginas de Cadastros", async ({ page }) => {
  await simularApi(page);
  await page.goto("/");
  await expect(page.locator(".barra-navegacao")).toBeVisible();
  await page.locator(".navegacao-menu summary").click();
  await page.locator('.navegacao-menu a[href="/cadastros.html"]').click();
  await expect(page).toHaveURL(/cadastros\.html$/);
  await expect(page.locator(".navegacao-pagina")).toHaveText("Cadastros");

  await page.locator('a[href="/grupos-padroes.html"]').last().click();
  await expect(page).toHaveURL(/grupos-padroes\.html$/);
  await expect(page.locator(".navegacao-pagina")).toHaveText("Grupos de padrões");

  await page.locator("#botao-voltar").click();
  await expect(page).toHaveURL(/cadastros\.html$/);
  await page.locator('a[href="/padroes.html"]').last().click();
  await expect(page).toHaveURL(/padroes\.html$/);
  await expect(page.locator(".navegacao-pagina")).toHaveText("Padrões");
});


test("grade de grupos permite incluir, editar e excluir", async ({ page }) => {
  await simularApiGrupos(page);
  await page.goto("/grupos-padroes.html");

  await expect(page.locator("#corpo-tabela-grupos tr")).toHaveCount(1);
  await expect(page.locator("#mensagem-grupos")).toHaveText("1 grupo(s) carregado(s).");

  await page.locator("#novo-grupo-nome").fill("Mesma coluna");
  await page.locator("#novo-grupo-descr").fill("Padrões na mesma coluna.");
  await page.locator("#botao-adicionar-grupo").click();

  const novo = page.locator('#corpo-tabela-grupos tr[data-codigo="PG_002"]');
  await expect(novo).toHaveCount(1);
  await novo.locator("input").fill("Mesma coluna da matriz");
  await novo.locator('button[data-acao="salvar"]').click();
  await expect(page.locator("#mensagem-grupos")).toHaveText("PG_002 atualizado.");
  await expect(novo.locator("input")).toHaveValue("Mesma coluna da matriz");

  page.once("dialog", (dialogo) => dialogo.accept());
  await novo.locator('button[data-acao="excluir"]').click();
  await expect(novo).toHaveCount(0);
  await expect(page.locator("#mensagem-grupos")).toHaveText("PG_002 excluído.");

  const ocupado = page.locator('#corpo-tabela-grupos tr[data-codigo="PG_001"]');
  page.once("dialog", (dialogo) => dialogo.accept());
  await ocupado.locator('button[data-acao="excluir"]').click();
  await expect(ocupado).toHaveCount(1);
  await expect(page.locator("#mensagem-grupos")).toHaveText(
    "Não foi possível concluir: O grupo possui padrões e não pode ser excluído.",
  );
});


test("grade de padrões filtra, inclui, transfere e protege estatísticas", async ({ page }) => {
  await simularApi(page);
  await simularApiGrupos(page, true);
  await page.goto("/padroes.html");

  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(3);
  const primeira = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_001"]');
  await expect(primeira.locator("td").nth(4)).toHaveText("1192");
  await expect(primeira.locator("td").nth(5)).toHaveText("2,575147");
  await expect(primeira.locator("select")).toHaveValue("PG_001");

  await page.locator("#novo-padrao-grupo").selectOption("PG_002");
  await page.locator("#novo-padrao-nome").fill("Duas dezenas na coluna");
  await page.locator("#novo-padrao-descr").fill("Descrição futura.");
  await page.locator("#botao-adicionar-padrao").click();
  const novo = page.locator('#corpo-tabela-padroes tr[data-codigo="PD_004"]');
  await expect(novo).toHaveCount(1);
  await expect(novo.locator("select")).toHaveValue("PG_002");
  await expect(novo.locator("td").nth(4)).toHaveText("—");

  await novo.locator("select").selectOption("PG_001");
  await novo.locator("input").fill("Padrão transferido");
  await novo.locator('button[data-acao="salvar"]').click();
  await expect(page.locator("#mensagem-padroes")).toHaveText("PD_004 atualizado.");
  await expect(novo.locator("select")).toHaveValue("PG_001");

  await page.locator("#filtro-grupo").selectOption("PG_002");
  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(0);
  await page.locator("#filtro-grupo").selectOption("");
  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(4);

  page.once("dialog", (dialogo) => dialogo.accept());
  await novo.locator('button[data-acao="excluir"]').click();
  await expect(novo).toHaveCount(0);
});


test("página de padrões conserva espaço e contém suas rolagens", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await simularCatalogoExtenso(page);
  await page.goto("/padroes.html");
  await expect(page.locator("#corpo-tabela-padroes tr")).toHaveCount(45);

  const antes = await page.evaluate(() => {
    const barra = document.querySelector(".barra-navegacao").getBoundingClientRect();
    const pagina = document.querySelector(".pagina-conteudo").getBoundingClientRect();
    const grade = document.querySelector(".padroes-grade");
    return {
      alturaBarra: barra.height,
      topoPagina: pagina.top,
      corpoLargura: document.documentElement.scrollWidth,
      janelaLargura: window.innerWidth,
      gradeDireita: grade.getBoundingClientRect().right,
      gradeBaixo: grade.getBoundingClientRect().bottom,
      gradeAltura: grade.clientHeight,
      rolagemHorizontal: grade.scrollWidth > grade.clientWidth,
      rolagemVertical: grade.scrollHeight > grade.clientHeight,
    };
  });
  expect(antes.alturaBarra).toBeLessThanOrEqual(46);
  expect(antes.corpoLargura).toBeLessThanOrEqual(antes.janelaLargura);
  expect(antes.gradeDireita).toBeLessThanOrEqual(1280);
  expect(antes.gradeBaixo).toBeLessThanOrEqual(720);
  expect(antes.gradeAltura).toBeGreaterThan(300);
  expect(antes.rolagemHorizontal).toBe(true);
  expect(antes.rolagemVertical).toBe(true);

  await page.locator(".navegacao-menu summary").click();
  const depoisMenu = await page.evaluate(() => ({
    alturaBarra: document.querySelector(".barra-navegacao").getBoundingClientRect().height,
    topoPagina: document.querySelector(".pagina-conteudo").getBoundingClientRect().top,
  }));
  expect(depoisMenu.alturaBarra).toBe(antes.alturaBarra);
  expect(depoisMenu.topoPagina).toBe(antes.topoPagina);

  const fixacao = await page.evaluate(() => {
    const grade = document.querySelector(".padroes-grade");
    grade.scrollTop = 500;
    const topoGrade = grade.getBoundingClientRect().top;
    const topoCabecalho = document.querySelector("#tabela-padroes th").getBoundingClientRect().top;
    return { topoGrade, topoCabecalho };
  });
  expect(Math.abs(fixacao.topoCabecalho - fixacao.topoGrade)).toBeLessThanOrEqual(2);
});


test("páginas compactas não alargam a janela estreita", async ({ page }) => {
  await page.setViewportSize({ width: 700, height: 600 });
  await simularCatalogoExtenso(page);
  for (const caminho of ["/grupos-padroes.html", "/padroes.html"]) {
    await page.goto(caminho);
    const medidas = await page.evaluate(() => {
      const grade = document.querySelector(".grupos-grade, .padroes-grade");
      const barraFormulario = document.querySelector(".grupos-barra, .padroes-barra");
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
    expect(medidas.barraRola).toBe(true);
    expect(medidas.gradeRola).toBe(true);
    expect(medidas.gradeDireita).toBeLessThanOrEqual(700);
    expect(medidas.gradeBaixo).toBeLessThanOrEqual(600);
  }
});
