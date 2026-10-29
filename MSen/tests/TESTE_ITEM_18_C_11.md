# Teste da subetapa 18-C.11 — regressão e fechamento

Data: 2026-10-29

## Regressão automatizada

- 508 testes Python aprovados;
- 35 testes JavaScript aprovados;
- 18 fluxos completos no Google Chrome aprovados;
- três fluxos integrados Chrome/PostgreSQL aprovados;
- dois fluxos Chrome contra a API local real aprovados: distribuições e
  screener extensível.

## PostgreSQL temporário

O backup com 3.069 resultados foi restaurado no database protegido
`games_test_7_1_1811`. As migrações 002–010 foram aplicadas sobre a migração 001
já existente no backup. O recálculo produziu os nove percentuais esperados,
inclusive valores iguais a zero quando aplicável ao conjunto analisado.

O database temporário foi removido automaticamente. A listagem antes e depois
do ensaio retornou `[]`. O database local `games` não recebeu escrita nesse
ensaio.

## Correções reveladas pela regressão

1. O teste de importação ainda esperava somente quantidade, intervalo e desvio.
   Ele passou a conferir também `total_sorteios` e `percentual_ocorrencia`.
2. O teste real do screener contava saldos dos grupos internos junto aos três
   níveis principais. O seletor foi restringido aos cabeçalhos diretos e passou
   a conferir apenas `2.001`, `423` e `414`.

As duas divergências estavam nas expectativas de teste; os cálculos e dados da
aplicação estavam corretos.

## Documentação revisada

- funcionalidades do screener de padrões;
- decisões sobre incidência e raridade;
- critérios de seleção das combinações;
- plano de etapas;
- continuidade para a próxima sessão.

Foi removida da documentação vigente a regra antiga de
`SEM_CORRESPONDENCIA`. Novos padrões somente participam do screener após detector
Python, testes, integração ao registro e recálculo histórico.

## Resultado

Etapa 18-C encerrada tecnicamente. Nenhum commit ou push foi executado.
