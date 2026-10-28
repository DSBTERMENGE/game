import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";


test("painel de distribuições mantém dez gráficos em grade com rolagem interna", async () => {
  const html = await readFile(new URL("../distribuicoes.html", import.meta.url), "utf8");
  const css = await readFile(new URL("../css/distribuicoes.css", import.meta.url), "utf8");
  const javascript = await readFile(new URL("../js/distribuicoes.js", import.meta.url), "utf8");

  for (const id of [
    "botao-atualizar-distribuicoes", "botao-configurar-faixas",
    "mensagem-distribuicoes", "resumo-amostra",
    "resumo-concursos", "resumo-datas", "resumo-faixa", "grade-distribuicoes",
    "dialogo-configuracao-faixas", "form-configuracao-faixas",
    "config-metodo-faixa", "config-margem-inferior", "config-margem-superior",
    "botao-calcular-previa", "corpo-previa-faixas", "botao-salvar-configuracao",
  ]) assert.match(html, new RegExp(`id=["']${id}["']`));
  assert.match(html, /Estudo — screener inativo/);
  assert.match(html, /curva normal é somente uma referência visual/i);
  assert.match(css, /\.distribuicoes-pagina\s*\{[^}]*grid-template-rows:\s*auto auto auto minmax\(0, 1fr\)/s);
  assert.match(css, /\.grade-distribuicoes\s*\{[^}]*overflow:\s*auto/s);
  assert.match(css, /grid-template-columns:\s*repeat\(2, minmax\(25rem, 1fr\)\)/);
  assert.match(javascript, /\/api\/perfis\/distribuicoes/);
  assert.match(javascript, /EST_SOMA/);
  assert.match(javascript, /GEO_CENTRO_GRAVIDADE_Y/);
  assert.match(javascript, /curva_normal_referencia/);
  assert.match(javascript, /grafico-faixa/);
  assert.match(javascript, /salvarConfiguracaoDistribuicoes/);
  assert.match(javascript, /Calcule a prévia antes de salvar/);
});
