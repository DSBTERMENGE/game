import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { secoesAjuda, topicosAjuda } from "../js/ajuda-conteudo.js";
import { buscarTopicos, localizarTopico, normalizarBusca, validarOrigemAjuda } from "../js/ajuda.js";


test("conteúdo possui as quatro seções editoriais e IDs únicos", () => {
  assert.deepEqual(
    secoesAjuda.map((secao) => secao.titulo),
    ["Começar aqui", "Conceitos gerais", "Ajuda por página", "Referência funcional"],
  );
  const ids = topicosAjuda.map((topico) => topico.id);
  assert.equal(new Set(ids).size, ids.length);
  assert.ok(ids.every((id) => /^(inicio|conceito|pagina|referencia)-[a-z0-9-]+$/.test(id)));
});
test("busca ignora acentos e encontra títulos, aliases e conteúdo", () => {
  assert.equal(normalizarBusca("  Seleção  "), "selecao");
  assert.equal(buscarTopicos("selecao dezenas")[0].id, "pagina-selecao-dezenas");
  assert.equal(buscarTopicos("executar 5000")[0].id, "pagina-preparacao-screener");
  assert.ok(buscarTopicos("concurso 500").some((topico) => topico.id === "referencia-linha-tempo"));
  assert.equal(buscarTopicos("fator k fator j")[0].id, "conceito-faixa-k-j");
  assert.equal(buscarTopicos("SHA-256 imutável")[0].id, "conceito-configuracao-assinatura");
  assert.ok(buscarTopicos("230.230").some((topico) => topico.id === "referencia-quantidades"));
  assert.deepEqual(buscarTopicos("assunto inexistente"), []);
});

test("conceitos comprovados possuem fórmulas, linha do tempo e persistência", () => {
  const faixa = localizarTopico("conceito-faixa-k-j");
  assert.ok(faixa.blocos.flatMap((bloco) => bloco.formulas ?? []).some((formula) => formula.includes("j × σ")));
  assert.equal(localizarTopico("referencia-persistencia").estado, "confirmado");
  assert.match(localizarTopico("referencia-linha-tempo").resumo, /marcos iniciais diferentes/);
  assert.ok(localizarTopico("conceito-atualizacao-calculo"));
});

test("todas as páginas vigentes possuem ajuda operacional central", () => {
  const idsPaginas = [
    "pagina-painel", "pagina-cadastros", "pagina-grupos-padroes", "pagina-padroes",
    "pagina-distribuicoes", "pagina-preparacao-screener", "pagina-validacao-auditoria",
    "pagina-frequencia-dezenas", "pagina-graficos-frequencia", "pagina-selecao-dezenas",
    "pagina-gestao-desenvolvimento", "pagina-ajuda",
  ];
  for (const id of idsPaginas) {
    const topico = localizarTopico(id);
    assert.ok(topico, `tópico ausente: ${id}`);
    assert.notEqual(topico.estado, "em-desenvolvimento", `tópico incompleto: ${id}`);
    assert.ok(topico.blocos.length >= 2, `conteúdo insuficiente: ${id}`);
  }
  assert.equal(buscarTopicos("salvar estudo navegador")[0].id, "pagina-distribuicoes");
  assert.equal(buscarTopicos("conferir configuração jogos")[0].id, "pagina-selecao-dezenas");
  assert.equal(buscarTopicos("concluir trabalho PythonAnywhere")[0].id, "pagina-gestao-desenvolvimento");
});

test("localização por link direto possui retorno seguro", () => {
  assert.equal(localizarTopico("conceito-corte-historico")?.titulo, "Corte histórico");
  assert.equal(localizarTopico("nao-existe"), null);
});

test("retorno contextual aceita somente páginas internas conhecidas", () => {
  assert.deepEqual(
    validarOrigemAjuda("/frequencias.html?dezena=7#evolucao", "http://game.local"),
    { href: "/frequencias.html?dezena=7#evolucao", rotulo: "Frequência das dezenas" },
  );
  assert.equal(validarOrigemAjuda("https://exemplo.com/frequencias.html", "http://game.local"), null);
  assert.equal(validarOrigemAjuda("/pagina-inexistente.html", "http://game.local"), null);
});

test("página central possui pesquisa, regiões acessíveis e scripts separados", async () => {
  const html = await readFile(new URL("../ajuda.html", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/ajuda.css", import.meta.url), "utf8");
  for (const id of [
    "ajuda-busca", "ajuda-limpar-busca", "ajuda-estado-busca", "ajuda-arvore",
    "ajuda-resultados-busca", "ajuda-aviso", "ajuda-artigo", "ajuda-voltar-origem",
  ]) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /role="search"/);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /href="\/ajuda\.html" aria-current="page">Ajuda<\/a>/);
  assert.match(html, /js\/ajuda\.js/);
  assert.match(css, /grid-template-columns:\s*minmax\(15rem, 21rem\) minmax\(0, 1fr\)/);
  assert.match(css, /@media \(max-width: 50rem\)/);
  assert.match(css, /\.ajuda-formula/);
});

test("Ajuda é o último item da barra em todas as páginas", async () => {
  const arquivos = [
    "index.html", "cadastros.html", "grupos-padroes.html", "padroes.html",
    "distribuicoes.html", "screener.html", "auditoria.html", "frequencias.html",
    "graficos-frequencias.html", "selecao-dezenas.html", "gestao-desenvolvimento.html",
    "ajuda.html",
  ];
  for (const arquivo of arquivos) {
    const html = await readFile(new URL(`../${arquivo}`, import.meta.url), "utf8");
    const barra = html.match(/<header class="barra-navegacao">([\s\S]*?)<\/header>/)?.[1] ?? "";
    assert.match(barra, /href="\/ajuda\.html"/);
    const destinos = [...barra.matchAll(/href="([^"]+)"/g)].map((resultado) => resultado[1]);
    assert.equal(destinos.at(-1), "/ajuda.html");
  }
});

test("todos os acessos contextuais apontam para tópicos centrais existentes", async () => {
  for (const arquivo of [
    "frequencias.html", "graficos-frequencias.html", "selecao-dezenas.html",
    "gestao-desenvolvimento.html",
  ]) {
    const html = await readFile(new URL(`../${arquivo}`, import.meta.url), "utf8");
    const destinos = [...html.matchAll(/href="\/ajuda\.html\?origem=[^"]+#([a-z0-9-]+)"/g)];
    assert.ok(destinos.length > 0, `acesso contextual ausente: ${arquivo}`);
    for (const destino of destinos) {
      assert.ok(localizarTopico(destino[1]), `tópico inexistente em ${arquivo}: ${destino[1]}`);
    }
  }
});

