import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const html = await readFile(new URL("../frequencias.html", import.meta.url), "utf8");
const css = await readFile(new URL("../css/frequencias.css", import.meta.url), "utf8");
const javascript = await readFile(new URL("../js/frequencias.js", import.meta.url), "utf8");
const paginaGraficos = await readFile(new URL("../graficos-frequencias.html", import.meta.url), "utf8");
const navegacaoGraficos = await readFile(new URL("../js/navegacao-graficos-frequencias.js", import.meta.url), "utf8");
const javascriptGraficos = await readFile(new URL("../js/graficos-frequencias.js", import.meta.url), "utf8");
const cssGraficos = await readFile(new URL("../css/graficos-frequencias.css", import.meta.url), "utf8");

test("página expõe estado, configurações gravada e calculada e ações", () => {
  for (const id of [
    "resumo-resultados", "resumo-ultimo-processado", "resumo-linhas",
    "configuracao-gravada", "form-configuracao-frequencia",
    "frequencia-salvar-dados", "botao-calcular-previa-frequencia",
    "dialogo-previa-frequencia", "botao-prosseguir-previa-frequencia",
  ]) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /frequencia-salvar-dados" type="checkbox" checked/);
  assert.match(html, /aria-current="page">Frequência das dezenas/);
  assert.match(html, /id="frequencia-tipo-grafico"/);
  assert.match(html, /id="grade-graficos-frequencia"/);
  assert.match(html, /id="form-historico-frequencia"/);
  assert.doesNotMatch(html, /id="grade-historico-frequencia"/);
  assert.doesNotMatch(html, /frequencias-historico-legenda/);
  assert.match(html, /id="assertividade-percentual"/);
  assert.match(html, /id="backtest-intervalo"/);
  assert.match(html, /id="dezena-resumo-concurso"/);
  assert.match(html, /id="corpo-erros-assertividade"/);
  assert.match(html, /id="evolucao-historica-dezena"/);
  assert.match(html, /id="botao-abrir-graficos-historico"/);
  assert.doesNotMatch(html, /id="botao-executar-frequencia"/);
  assert.match(html, />Consultar dezena</);
  assert.match(html, /<strong>Backtest<\/strong>/);
  assert.doesNotMatch(html, /assertividade-censurados/);
  assert.doesNotMatch(html, /assertividade-erro-absoluto/);
  assert.doesNotMatch(html, /assertividade-erro-percentual/);
});

test("página auxiliar possui ida, volta e preserva os quatro filtros", () => {
  assert.match(paginaGraficos, /Gráficos de frequência das dezenas/);
  assert.match(paginaGraficos, /id="botao-voltar-frequencias"/);
  for (const id of ["graficos-dezena", "graficos-tipo-evento", "graficos-concurso-inicial", "graficos-concurso-final"]) {
    assert.match(paginaGraficos, new RegExp(`id=["']${id}["']`));
  }
  assert.match(navegacaoGraficos, /graficos-frequencias\.html/);
  assert.match(navegacaoGraficos, /#evolucao-historica-dezena/);
  assert.match(navegacaoGraficos, /concurso_inicial/);
  assert.match(navegacaoGraficos, /concurso_final/);
  assert.match(paginaGraficos, /id="grade-graficos-historicos"/);
  assert.match(paginaGraficos, /id="botao-consultar-graficos"/);
  assert.match(paginaGraficos, /Escalas X e Y independentes/);
  assert.match(paginaGraficos, /id="botao-ajuda-graficos"/);
  assert.match(paginaGraficos, /ajuda\.html\?origem=%2Fgraficos-frequencias\.html#pagina-graficos-frequencia/);
  assert.match(javascriptGraficos, /\/api\/frequencias\/serie\?/);
  assert.match(javascriptGraficos, /Evolução dos intervalos/);
  assert.match(javascriptGraficos, /Faixa prevista e ocorrências reais/);
  assert.match(javascriptGraficos, /marcasEixoConcursos/);
  assert.match(javascriptGraficos, /intervalos_individuais/);
  assert.match(javascriptGraficos, /historico-intervalo-degrau/);
  assert.match(javascriptGraficos, /historico-intervalo-transicao/);
  assert.match(javascriptGraficos, /media_menos_desvio/);
  assert.match(javascriptGraficos, /media_mais_desvio/);
  assert.match(paginaGraficos, /Média dos intervalos − desvio-padrão/);
  assert.match(paginaGraficos, /Média dos intervalos \+ desvio-padrão/);
  assert.match(paginaGraficos, /Intervalos/);
  assert.doesNotMatch(paginaGraficos, /<span><i class="legenda-minimo"/);
  assert.doesNotMatch(paginaGraficos, /<span><i class="legenda-maximo"/);
  assert.match(javascriptGraficos, /Número do concurso/);
  assert.match(cssGraficos, /\.grafico-historico-ampliado[^}]*height:\s*clamp/s);
  assert.match(cssGraficos, /historico-marca-degrau/);
  assert.match(cssGraficos, /historico-intervalo-curto/);
  assert.match(cssGraficos, /\.grade-graficos-historicos[^}]*display:\s*grid/s);
});

test("gráficos auxiliares compartilham um único modal reutilizável", () => {
  assert.equal((paginaGraficos.match(/id="dialogo-grafico-auxiliar"/g) || []).length, 1);
  assert.equal((paginaGraficos.match(/id="svg-grafico-auxiliar"/g) || []).length, 1);
  assert.match(javascriptGraficos, /Curva de distribuição/);
  assert.match(javascriptGraficos, /Ocorrências em ordem crescente/);
  assert.match(javascriptGraficos, /renderizarCurvaDistribuicao/);
  assert.match(javascriptGraficos, /renderizarOcorrenciasOrdenadas/);
  assert.match(javascriptGraficos, /dialogoAuxiliar\.addEventListener\("close", limparGraficoAuxiliar\)/);
  assert.match(javascriptGraficos, /svgAuxiliar\.replaceChildren\(\)/);
});

test("três acessos de ajuda abrem tópicos da Ajuda central", () => {
  assert.doesNotMatch(paginaGraficos, /<dialog id="dialogo-ajuda-grafico"/);
  assert.match(paginaGraficos, /id="botao-ajuda-grafico-auxiliar"/);
  assert.match(javascriptGraficos, /botao-ajuda-evolucao-intervalos/);
  assert.match(javascriptGraficos, /pagina-graficos-frequencia-evolucao/);
  assert.match(javascriptGraficos, /pagina-graficos-frequencia-distribuicao/);
  assert.match(javascriptGraficos, /pagina-graficos-frequencia-ordenado/);
});

test("ajuda da página abre diretamente o tópico central", () => {
  assert.match(html, /id="botao-ajuda-frequencias"/);
  assert.match(html, /ajuda\.html\?origem=%2Ffrequencias\.html#pagina-frequencia-dezenas/);
  assert.doesNotMatch(html, /<dialog id="dialogo-ajuda-frequencias"/);
});

test("página usa API, prévia modal, confirmação, progresso e cancelamento", () => {
  assert.match(javascript, /\/api\/frequencias\/estado/);
  assert.match(javascript, /\/api\/frequencias\/previa/);
  assert.match(javascript, /\/api\/frequencias\/execucoes/);
  assert.match(javascript, /confirmacao_gravacao/);
  assert.match(javascript, /criarModalAndamento/);
  assert.match(javascript, /abrirPrevia/);
  assert.match(javascript, /linhas_estimadas/);
  assert.match(javascript, /dialogoPrevia\.showModal/);
  assert.match(javascript, /cancelamento/);
  assert.match(javascript, /fotografia-atual\?tipo_evento=/);
  assert.match(javascript, /MEDICOES_FREQUENCIA/);
  assert.match(javascript, /\/api\/frequencias\/serie\?/);
  assert.match(javascript, /ocorrencias_reais/);
  assert.match(javascript, /renderizarAssertividade/);
});

test("layout mantém regiões densas roláveis em largura normal e estreita", () => {
  assert.match(css, /grid-template-rows:\s*auto auto auto auto minmax\(14rem, 1fr\) auto/);
  assert.match(css, /\.frequencias-configuracoes[^}]*overflow:\s*auto/s);
  assert.match(css, /@media \(max-width: 900px\)/);
  assert.match(css, /@media \(max-width: 560px\)/);
  assert.match(css, /\.grade-graficos-frequencia[^}]*overflow:\s*auto/s);
  assert.doesNotMatch(css, /\.grade-historico-frequencia/);
});
