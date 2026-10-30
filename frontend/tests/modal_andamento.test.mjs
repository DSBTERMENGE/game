import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";


const html = await readFile(new URL("../auditoria.html", import.meta.url), "utf8");
const componente = await readFile(new URL("../js/modal-andamento.js", import.meta.url), "utf8");
const pagina = await readFile(new URL("../js/auditoria.js", import.meta.url), "utf8");
const css = await readFile(new URL("../css/modal-andamento.css", import.meta.url), "utf8");


test("página reserva botão e carrega componente reutilizável", () => {
  assert.match(html, /id="botao-atualizar-validacao"/);
  assert.match(html, /css\/modal-andamento\.css/);
  assert.match(html, /js\/auditoria\.js/);
  assert.match(pagina, /criarModalAndamento/);
});

test("página completa possui estado, resumo, filtros, grade e paginação", () => {
  for (const id of [
    "estado-algoritmo", "resumo-total", "filtro-categoria", "filtro-criterio",
    "filtro-grupo", "filtro-subgrupo", "filtro-situacao", "corpo-avaliacoes",
    "pagina-anterior", "pagina-seguinte",
  ]) assert.match(html, new RegExp(`id="${id}"`));
  assert.match(pagina, /\/api\/validacao\/quadro/);
  assert.match(pagina, /formatarDezenas/);
  assert.match(pagina, /formatarResultado/);
});

test("relatório fecha por função e detalha divergências sem alterar resultados", () => {
  for (const id of ["relatorio-fechamento", "relatorio-sincronizacao", "corpo-relatorio-criterios", "lista-divergencias"])
    assert.match(html, new RegExp(`id="${id}"`));
  assert.match(pagina, /\/api\/validacao\/relatorio/);
  assert.match(pagina, /Hipótese diagnóstica da IA/);
  assert.match(pagina, /assinatura_executada/);
  assert.match(pagina, /implementacoes_alteradas/);
  assert.match(html, /\/api\/validacao\/exportacao\?formato=json/);
  assert.match(html, /\/api\/validacao\/exportacao\?formato=csv/);
  assert.match(html, /Exportar tabela CSV segura/);
});

test("modal apresenta progresso real, duração, erro e bloqueio de fechamento", () => {
  assert.match(componente, /role="progressbar"/);
  assert.match(componente, /dados\.concluido/);
  assert.match(componente, /dados\.total/);
  assert.match(componente, /duracao_segundos/);
  assert.match(componente, /dados\.erro/);
  assert.match(componente, /evento\.preventDefault\(\)/);
  assert.match(componente, /fechar\.disabled = !terminal/);
  assert.match(componente, /modal-andamento__resultado/);
  assert.match(componente, /apresentarResultado/);
  assert.match(pagina, /Validação e auditoria concluída e aprovada/);
  assert.match(pagina, /Use o filtro Situação para localizar as ocorrências/);
  assert.match(pagina, /Validação e auditoria aprovada/);
  assert.match(pagina, /nenhuma reprovação ou pendência/);
  assert.match(css, /prefers-reduced-motion/);
});

test("página inicia uma execução e consulta seu identificador", () => {
  assert.match(pagina, /fetch\("\/api\/validacao\/execucoes"/);
  assert.match(pagina, /method\s*:\s*"POST"/);
  assert.match(pagina, /encodeURIComponent\((identificador|id)\)/);
  assert.match(pagina, /(botao|e\.atualizar)\.disabled\s*=\s*true/);
});
