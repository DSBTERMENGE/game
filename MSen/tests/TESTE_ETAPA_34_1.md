# Teste da etapa 34.1 — Limites visuais da faixa

Data: 14/11/2026.

## Objetivo

Confirmar que cada distribuição exibe os limites inferior e superior da faixa
calculada como linhas verticais verdes e tracejadas, sem confundi-los com a
linha azul da média nem alterar os dados observados.

## Verificações automatizadas

- `node --test frontend/tests/distribuicoes.test.mjs frontend/tests/configuracao_distribuicoes.test.mjs`
  — 5 testes aprovados.
- `npm run test:frontend` — 163 testes aprovados, nenhuma falha.

Os testes conferem a presença das duas linhas, os pontos geométricos usados
para posicioná-las e o estilo verde tracejado.

## Verificação no navegador

A página foi aberta contra a aplicação real, com 3.069 concursos e dez
gráficos. Foi calculada uma prévia pelo método de desvio-padrão com margem
inferior 0,5 e superior 1,5.

Resultado:

- 10 limites inferiores e 10 limites superiores foram desenhados;
- as linhas apresentaram a cor `rgb(22, 128, 60)` e o tracejado `4px 2px`;
- no primeiro gráfico, a distância entre média e limite superior foi três
  vezes a distância entre média e limite inferior, de acordo com as margens;
- a linha azul da média permaneceu visível;
- nenhuma informação foi gravada no banco de dados; o ensaio usou somente o
  armazenamento isolado do navegador de teste.
