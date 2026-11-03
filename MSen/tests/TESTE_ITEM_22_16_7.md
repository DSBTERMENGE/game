# Teste do item 22.16.7 — Remoção dos gráficos duplicados

Data: 2026-10-31

## Objetivo

Confirmar que a página principal recupera o espaço antes ocupado pelos gráficos
históricos sem perder a análise e a navegação para a página gráfica.

## Critérios

- Não existe grade, legenda nem cartão gráfico histórico em `frequencias.html`.
- Dezena, evento, período e `Consultar série` permanecem disponíveis.
- A consulta continua preenchendo assertividade e relatório de falhas.
- `Abrir gráficos` continua preservando os quatro filtros.
- Os gráficos permanecem disponíveis em `graficos-frequencias.html`.

## Resultado

- 56 testes JavaScript aprovados.
- 10 fluxos Chrome do módulo aprovados em tela normal e estreita.
- A consulta continuou preenchendo 10 avaliações e uma falha no cenário
  controlado, sem criar cartões gráficos na página principal.
- A navegação confirmou dois gráficos na página auxiliar e preservou os quatro
  filtros na ida e na volta.
- A página real respondeu HTTP 200 na porta 5050, sem a grade histórica e com
  o botão `Abrir gráficos` e os indicadores de assertividade presentes.
