import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const html = await readFile(new URL("../frequencias.html", import.meta.url), "utf8");
const css = await readFile(new URL("../css/frequencias.css", import.meta.url), "utf8");
const javascript = await readFile(new URL("../js/frequencias.js", import.meta.url), "utf8");

test("página expõe estado, configurações gravada e calculada e ações", () => {
  for (const id of [
    "resumo-resultados", "resumo-ultimo-processado", "resumo-linhas",
    "configuracao-gravada", "form-configuracao-frequencia",
    "frequencia-salvar-dados", "botao-calcular-previa-frequencia",
    "botao-executar-frequencia",
  ]) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /frequencia-salvar-dados" type="checkbox" checked/);
  assert.match(html, /aria-current="page">Frequência das dezenas/);
  assert.match(html, /id="frequencia-tipo-grafico"/);
  assert.match(html, /id="grade-graficos-frequencia"/);
  assert.match(html, /id="form-historico-frequencia"/);
  assert.match(html, /id="grade-historico-frequencia"/);
  assert.match(html, /id="assertividade-percentual"/);
  assert.match(html, /id="corpo-erros-assertividade"/);
});

test("página usa API, prévia, confirmação, progresso e cancelamento", () => {
  assert.match(javascript, /\/api\/frequencias\/estado/);
  assert.match(javascript, /\/api\/frequencias\/previa/);
  assert.match(javascript, /\/api\/frequencias\/execucoes/);
  assert.match(javascript, /confirmacao_gravacao/);
  assert.match(javascript, /criarControleFrequencia/);
  assert.match(javascript, /criarModalAndamento/);
  assert.match(javascript, /cancelamento/);
  assert.match(javascript, /fotografia-atual\?tipo_evento=/);
  assert.match(javascript, /MEDICOES_FREQUENCIA/);
  assert.match(javascript, /\/api\/frequencias\/serie\?/);
  assert.match(javascript, /ocorrencias_reais/);
  assert.match(javascript, /renderizarAssertividade/);
});

test("layout mantém regiões densas roláveis em largura normal e estreita", () => {
  assert.match(css, /grid-template-rows:\s*auto auto auto auto minmax\(14rem, 1fr\) minmax\(14rem, 1fr\)/);
  assert.match(css, /\.frequencias-configuracoes[^}]*overflow:\s*auto/s);
  assert.match(css, /@media \(max-width: 900px\)/);
  assert.match(css, /@media \(max-width: 560px\)/);
  assert.match(css, /\.grade-graficos-frequencia[^}]*overflow:\s*auto/s);
  assert.match(css, /\.grade-historico-frequencia[^}]*overflow:\s*auto/s);
});
