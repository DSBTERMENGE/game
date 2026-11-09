import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const html = await readFile(new URL("../selecao-dezenas.html", import.meta.url), "utf8");
const css = await readFile(new URL("../css/selecao-dezenas.css", import.meta.url), "utf8");
const javascript = await readFile(new URL("../js/selecao-dezenas.js", import.meta.url), "utf8");

test("página possui navegação e blocos da subetapa 23.10", () => {
  assert.match(html, /aria-current="page">Seleção de dezenas/);
  for (const id of [
    "form-configuracao-selecao", "titulo-concurso-alvo", "form-backtest-selecao",
    "form-comparacao-selecao", "corpo-detalhes-backtest", "painel-jogos",
  ]) assert.match(html, new RegExp(`id="${id}"`));
  assert.match(html, /js\/selecao-dezenas\.js/);
});

test("página contém ajuda modal por blocos", () => {
  assert.match(html, /id="botao-ajuda-selecao"/);
  assert.match(html, /id="dialogo-ajuda-selecao"/);
  assert.match(html, /Como usar Seleção de dezenas/);
  assert.match(html, /1\.1 Abordagem técnica/);
  assert.match(html, /1\.2 Configurando/);
  assert.match(html, /1\.3 Botões de comando/);
  assert.match(html, /Concurso-alvo \(CA\)<\/strong> é sempre o concurso imediatamente posterior/);
  assert.match(html, /Analisar configuração<\/button>/);
  assert.match(html, /Registrar previsão do próximo concurso<\/button>/);
  assert.match(html, /Registros do screener de dezenas/);
  assert.match(html, /posterior elaboração das combinações possíveis/);
  assert.match(html, /Esse botão <strong>não executa o backtest<\/strong> e <strong>não gera as combinações<\/strong>/);
  assert.match(html, /não cria uma cópia nem altera a lista original/);
  assert.match(html, /Concurso previsto/);
  assert.match(html, /Dados utilizados até/);
  assert.match(html, /Estado da conferência/);
  assert.match(html, /Próxima ação/);
  assert.doesNotMatch(html, /id="selecao-horizonte"/);
  assert.doesNotMatch(javascript, /selecao_horizonte/);
  assert.doesNotMatch(html, /id="assinatura-selecao"/);
  assert.match(html, /os campos ficam desabilitados porque uma configuração salva não pode ser alterada/);
  assert.match(javascript, /Configuração salva: os campos estão protegidos contra alterações/);
  assert.match(javascript, /Configuração salva com sucesso/);
  assert.match(html, /formação de jogos/i);
  assert.match(html, /Mₐ = U \+ μ \+ j × σ/);
  assert.match(html, /LIA = ⌊Mₐ − k × σ⌋/);
  assert.match(html, /LSA = ⌈Mₐ \+ k × σ⌉/);
  assert.match(html, /base estiver desatualizada/);
  assert.match(html, /j<\/strong> desloca Mₐ em relação a μ/);
  assert.match(html, /gráficos atualizados das distribuições históricas/);
  assert.match(html, /sistema não mede nem corrige automaticamente a assimetria/);
  assert.match(html, /testar diferentes pares de <strong>k<\/strong> e <strong>j<\/strong> pelo backtest/);
  assert.match(html, /quantidade de dezenas retornadas e o número de combinações de seis/);
  assert.match(html, /equilíbrio entre quantidade de dezenas, cobertura observada no backtest e custo/);
  assert.match(html, /class="selecao-diagrama-faixa"/);
  assert.match(html, /LIH\/LSH:/);
  assert.match(html, /LIA\/LSA:/);
  assert.match(html, /Faixa ajustada por k e j/i);
  assert.match(html, /escala horizontal: intervalos desde U/);
  assert.match(html, /class="selecao-diagrama-faixa__legenda"/);
  assert.match(html, /class="selecao-diagrama-faixa__deslocamento"/);
  assert.match(html, /j = 0: Mₐ e μ coincidem/);
  assert.match(html, /orient="auto-start-reverse"/);
  assert.match(html, /A dezena é aprovada somente quando/);
  assert.match(html, /LIA ≤ CA ≤ LSA/);
  assert.match(html, /C\(N,6\)/);
  assert.match(html, /Fluxo recomendado/);
  assert.match(html, /sistema passa a considerar o concurso seguinte para um novo registro/);
  assert.match(html, /não garante desempenho futuro/);
});

test("javascript usa os endpoints da API e confirma jogos", () => {
  for (const trecho of [
    "/api/selecao-dezenas/configuracoes", "/api/selecao-dezenas/previa",
    "/api/selecao-dezenas/backtests", "/api/selecao-dezenas/previsoes",
    "/jogos/previa",
  ]) assert.match(javascript, new RegExp(trecho.replaceAll("/", "\\/")));
  assert.match(javascript, /window\.confirm/);
  assert.match(javascript, /criarModalAndamento/);
  assert.match(javascript, /dialogo_previa_backtest\.showModal/);
  assert.match(javascript, /Dados analíticos da configuração/);
  assert.match(javascript, /Esta análise é momentânea e não foi armazenada/);
  assert.match(html, /id="dialogo-confirmar-registro"/);
  assert.match(html, /Cancelar — não registrar/);
  assert.match(html, /Confirmar e registrar seleção/);
  assert.match(javascript, /id_configuracao_selecao: idConfiguracao/);
  assert.match(javascript, /Operação cancelada\. Nenhum dado foi gravado/);
});

test("layout possui duas colunas e adaptação responsiva", () => {
  assert.match(css, /\.selecao-duas-colunas\s*\{[^}]*grid-template-columns:\s*1fr 1fr/s);
  assert.match(css, /@media \(max-width: 950px\)/);
  assert.match(css, /\.selecao-diagrama-faixa svg/);
});
