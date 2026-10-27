# Evidência do Item 14.5 — adaptadores dos critérios

Data: 2026-10-27.

## Adaptadores entregues

- `AdaptadorPadroesHistoricos`.
- `AdaptadorMedidasEstatisticas`.
- `AdaptadorMedidasGeometricas`.

Cada adaptador recebe uma função específica e converte seu resultado para a
decisão comum do funil: aprovada/reprovada, código do critério e valores usados
na avaliação. As tolerâncias validadas são repassadas à função.

Um adaptador desabilitado aprova de forma neutra e não chama a função. Um
adaptador habilitado sem função ou que devolva um tipo incorreto é rejeitado.

## Testes

- 5 testes específicos aprovados.
- Regressão Python completa: 284 testes aprovados.
- Avaliadores artificiais comprovaram integração, valores explicativos e salto
  do segundo adaptador após reprovação no primeiro.

Nenhuma função real de exclusão foi associada ou ativada. Nenhuma combinação
foi gravada e nenhum banco foi modificado.
