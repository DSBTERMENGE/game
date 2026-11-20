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

test("ajuda do Screener descreve teste, aplicação integral e cancelamento", () => {
  const topico = topicosAjuda.find((item) => item.id === "pagina-preparacao-screener");
  const texto = JSON.stringify(topico);

  assert.equal(topico.estado, "confirmado");
  assert.match(texto, /5\.000 combinações/);
  assert.match(texto, /50\.063\.860 combinações/);
  assert.match(texto, /mesmo motor/);
  assert.match(texto, /segundo ponto seguro|próximo ponto seguro/);
  assert.match(texto, /servidor da aplicação funcionando/);
  assert.doesNotMatch(texto, /aplicação integral permanece bloqueada/);
});

test("ajuda dos cadastros explica Grupo, Padrões e confirmações atuais", () => {
  const cadastros = JSON.stringify(localizarTopico("pagina-cadastros"));
  const grupos = JSON.stringify(localizarTopico("pagina-grupos-padroes"));
  const padroes = JSON.stringify(localizarTopico("pagina-padroes"));

  assert.match(cadastros, /acesso direto|diretamente o formulário/);
  assert.match(grupos, /Localizar/);
  assert.match(grupos, /parte de seu nome/);
  assert.match(padroes, /Escolha primeiro o Grupo/);
  assert.match(padroes, /somente os registros vinculados/);
  assert.match(padroes, /confirmação positiva/);
  assert.match(padroes, /Validação e Auditoria/);
  assert.doesNotMatch(padroes, /Perfil de padrões|Limite %|Filtro e grade/);
});

test("ajuda do Painel explica integralmente a camada Quadrantes", () => {
  const painel = JSON.stringify(localizarTopico("pagina-painel"));

  assert.match(painel, /entre as dezenas 05 e 06/);
  assert.match(painel, /entre as dezenas 21 e 31/);
  assert.match(painel, /Q1 é a região superior direita/);
  assert.match(painel, /referência = total de ocorrências ÷ 4/);
  assert.match(painel, /lado do quadrado = quantidade do quadrante × passo/);
  assert.match(painel, /não são gravados no banco/);
  assert.match(painel, /Verde-escuro identifica a maior quantidade/);
  assert.match(painel, /mesma posição e a mesma cor/);
  assert.match(painel, /desmarque Quadrantes/);
  assert.match(painel, /importar concursos novos/);
});

test("ajuda do Painel explica ocorrências das dezenas e resumo combinado", () => {
  const painel = JSON.stringify(localizarTopico("pagina-painel"));

  assert.match(painel, /matriz de 10 por 10/);
  assert.match(painel, /mais de 100 ocorrências/);
  assert.match(painel, /proximidade entre a quantidade daquela dezena e a média/);
  assert.match(painel, /não classifica uma dezena como mais provável/);
  assert.match(painel, /quatro colunas de quinze itens/);
  assert.match(painel, /primeira coluna contém 01–15/);
  assert.match(painel, /formato dezena: quantidade/);
  assert.match(painel, /resumos dessas análises permanecem acima/);
  assert.match(painel, /rolagem interna do resumo/);
});

test("ajuda do Painel diferencia voo, geometria, médias e configuração visual", () => {
  const painel = JSON.stringify(localizarTopico("pagina-painel"));

  assert.match(painel, /Voo trabalha|Voo dos pássaros apresenta um concurso por vez/);
  assert.match(painel, /não é a média dos números sorteados/);
  assert.match(painel, /Linha Poligonal liga as seis dezenas/);
  assert.match(painel, /Polígono 1 acrescenta o fechamento/);
  assert.match(painel, /Polígono 2 mostra o contorno fechado sem cruzamentos/);
  assert.match(painel, /CG1 é o centro de gravidade do Polígono 1/);
  assert.match(painel, /CG2 é o centro de gravidade do Polígono 2/);
  assert.match(painel, /referências circulares de 20%, 40% e 60%/);
  assert.match(painel, /proporção 1:n/);
  assert.match(painel, /Salvar aplica os valores e os conserva neste navegador/);
  assert.match(painel, /Fechar sem salvar mantém a última configuração gravada/);
  assert.match(painel, /não alteram resultados, áreas, centros de gravidade ou dados do banco/);
});

test("ajuda de Distribuições explica gráficos, faixas, formulário e exemplos", () => {
  const distribuicoes = JSON.stringify(localizarTopico("pagina-distribuicoes"));

  assert.match(distribuicoes, /barras representam os valores realmente observados/);
  assert.match(distribuicoes, /linha azul tracejada marca a média histórica/);
  assert.match(distribuicoes, /duas linhas verdes tracejadas/);
  assert.match(distribuicoes, /Mín\. e Máx\. são os menores e maiores valores que realmente ocorreram/);
  assert.match(distribuicoes, /Faixa mín\. e Faixa máx\. são limites calculados/);
  assert.match(distribuicoes, /margens devem ser iguais ou maiores que zero e podem ser diferentes/);
  assert.match(distribuicoes, /Faixa mín\. = média − margem inferior × desvio-padrão/);
  assert.match(distribuicoes, /margem inferior 0,5 e superior 1,5 produzem faixa de 27,5 a 37,5/);
  assert.match(distribuicoes, /margem inferior 10% e superior 20% produzem faixa de 27 a 36/);
  assert.match(distribuicoes, /prévia deixa de ser válida e deve ser calculada novamente/);
  assert.match(distribuicoes, /salvo somente no navegador/);
  assert.match(distribuicoes, /não ativa nem executa o Screener/);
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
    "pagina-distribuicoes", "pagina-preparacao-screener",
    "pagina-validacao-auditoria-nova",
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
    "distribuicoes.html", "screener.html", "validacao-nova.html", "frequencias.html",
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
    "validacao-nova.html",
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

