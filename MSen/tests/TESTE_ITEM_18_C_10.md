# Teste da subetapa 18-C.10 — ensaio protegido com 5.000 combinações

Data: 2026-10-29

## Objetivo

Repetir a amostra reproduzível de 5.000 combinações com os três níveis do
screener, aplicar somente os padrões eleitos pela consulta de raridade e provar
o fechamento contábil sem liberar o processamento integral.

## Configuração fotografada

- semente: `20261027`;
- limite de raridade: `10.000000%`;
- operador: `<`;
- limite da amostra: 5.000 combinações;
- processamento integral: bloqueado;
- checksum SHA-256:
  `45b9f7eb48f98da6d44458501be22354c5ec10f50d6b50999e91b7c7c034eb99`.

Duas execuções produziram o mesmo resumo, os mesmos saldos e o mesmo checksum.

## Fechamento dos três níveis

| Nível | Entrada | Exclusões | Saldo |
| --- | ---: | ---: | ---: |
| Estatística | 5.000 | 2.999 | 2.001 |
| Geometria | 2.001 | 1.578 | 423 |
| Padrões | 423 | 9 | 414 |

Fechamento geral: `5.000 = 4.586 excluídas + 414 aprovadas`. A exclusão foi de
`91,720000%` e a aprovação de `8,280000%`.

## Padrões eleitos e aplicados

A consulta retornou somente incidências históricas estritamente menores que
10%. Cada filtro recebeu o saldo deixado pelos anteriores.

| Grupo | Padrão | Incidência | Avaliações | Exclusões | Saldo |
| --- | --- | ---: | ---: | ---: | ---: |
| PG_001 | PD_002 | 2,997719% | 423 | 3 | 420 |
| PG_001 | PD_003 | 0,162920% | 420 | 0 | 420 |
| PG_002 | PD_005 | 2,150538% | 420 | 3 | 417 |
| PG_002 | PD_006 | 0,130336% | 417 | 0 | 417 |
| PG_003 | PD_009 | 3,030303% | 417 | 3 | 414 |

Zero exclusões em PD_003 e PD_006 significa que eles foram selecionados e
executados, mas nenhuma combinação que chegou a esses filtros correspondeu ao
padrão. Padrões ausentes não foram eleitos pela consulta e não foram executados.

## Comparação com o ensaio anterior

Usando a mesma amostra e semente, o ensaio anterior aprovava 4.409 e excluía
591 combinações. O novo funil aprovou 414 e excluiu 4.586; a diferença foi de
3.995 aprovações a menos. A resposta registra como causas a nova ordem dos três
níveis, as faixas estatísticas, os cinco filtros geométricos e os detectores
raros selecionados dos três grupos.

## Regressão

- 508 testes Python aprovados;
- 35 testes JavaScript aprovados;
- 18 fluxos no Google Chrome aprovados;
- o resumo de cada filtro de padrão mostra código e nome do padrão, seguidos do
  código e nome do grupo, sem acrescentar uma coluna ao quadro;
- banco de dados não alterado;
- nenhum commit criado.

## Resultado

Subetapa 18-C.10 aprovada tecnicamente. O ensaio permanece experimental e o
processamento integral continua bloqueado.
