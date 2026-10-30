# Teste da subetapa 22.8 — página Frequência das dezenas

Data: 2026-10-30.

## Interface implementada

- o item `Frequência das dezenas` foi incluído em todas as páginas da navegação
  comum, sem retirar os itens existentes;
- `/frequencias.html` usa arquivos HTML, CSS e JavaScript separados;
- a página exibe quantidade e intervalo dos resultados, último concurso
  processado, quantidade de linhas históricas e estado da geração;
- a configuração gravada aparece ao lado da configuração a calcular;
- alterações no formulário ou nos ticks invalidam a prévia anterior;
- `Salvar dados` começa marcado e a gravação exige a confirmação aprovada;
- com o tick desmarcado, a execução é uma simulação sem persistência;
- o modal compartilhado apresenta progresso, resultado, erro e cancelamento;
- o controle opcional de reconstrução da origem começa desmarcado;
- a área de visualizações informa que os gráficos pertencem às subetapas 22.9
  e 22.10.

## Google Chrome

O teste `frontend/tests/browser/frequencias.spec.mjs` confirmou:

- carregamento da configuração e do estado devolvidos pela API;
- formatação de 3.069 resultados, último concurso 3.069 e 462.600 linhas;
- tick de gravação inicialmente marcado;
- simulação concluída no modal sem confirmação de gravação;
- página utilizável em 1280 px e 520 px.

A regressão completa do navegador também confirmou que o item adicional não
alarga páginas em 700 px. A navegação passa a rolar internamente até 50 rem.

## Regressão

- Python: **626 testes aprovados**.
- JavaScript: **45 testes aprovados**.
- Google Chrome: **27 fluxos aprovados**.

Permaneceram somente avisos preexistentes de arquivos abertos em testes do
Screener e de módulos JavaScript sem `type: module`. O banco `games` não foi
alterado.
