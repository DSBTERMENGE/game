# Evidência do Item 14.6 — quadro de avaliação

Data: 2026-10-27.

## Dados do quadro

O quadro registra versão, modo, semente, limite, configuração dos critérios,
duração, totais e, para cada critério, ordem, avaliações, exclusões e saldo.
Ele conserva o relatório e as combinações aprovadas para a etapa seguinte. Uma
serialização de tipos simples foi criada para futura API ou tela.

## Execução controlada

A amostra com semente `20261027` foi executada sem filtros reais. O quadro
recebeu 5.000, aprovou 5.000 e não apresentou linhas de exclusão. As tolerâncias
foram registradas, mas os três critérios permaneceram inativos.

## Testes

- 5 testes específicos aprovados.
- Regressão Python completa: 289 testes aprovados.
- Tempo, configuração, semente, ordem, contadores, saldos e JSON comprovados.

Nenhum resultado foi persistido e nenhum banco foi modificado.
