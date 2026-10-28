# Evidência da subetapa 16.1 — contrato de classificação por grupos

Data: 28/10/2026

## Escopo

Foram inspecionados o esquema PostgreSQL, o catálogo dos nove detectores e as
funções dos três grupos atuais. Nenhuma tabela, migração ou função foi alterada.

## Constatações

- PG_001 classifica pelo maior bloco horizontal consecutivo.
- PG_002 classifica pela maior sequência vertical em linhas subjacentes.
- PG_003 classifica pela maior ocupação de uma linha.
- PD_001 a PD_009 são exclusivos dentro dos respectivos grupos.
- Os três grupos produzem `SEM_CORRESPONDENCIA` quando a maior métrica é um.
- O mesmo resultado pode e deve possuir classificações diferentes em grupos
  diferentes.

## Casos executados com as funções reais

- `01 02 10 20 30 40`: PG_001 = PD_001.
- `01 02 03 20 40 60`: PG_001 = PD_002.
- `01 02 03 04 20 40`: PG_001 = PD_003.
- `01 11 22 33 44 55`: PG_002 = PD_004.
- `01 11 21 32 43 54`: PG_002 = PD_005.
- `01 11 21 31 42 53`: PG_002 = PD_006.
- `01 02 11 21 31 41`: PG_003 = PD_007.
- `01 02 03 11 21 31`: PG_003 = PD_008.
- `01 02 03 04 11 21`: PG_003 = PD_009.
- `01 12 23 34 45 56`: nenhuma classe atual nos três grupos, confirmando a
  diferença que deverá ser contabilizada como `SEM_CORRESPONDENCIA`.

## Resultado

Foi criado `docs/CONTRATO_CLASSIFICACAO_GRUPOS.md`. Após os esclarecimentos, o
contrato conceitual foi aprovado e a subetapa 16.2 depende somente de autorização
para preparar o DDL.

Após esclarecimento do usuário, as propostas PD_010, PD_011 e PD_012 foram
retiradas. A diferença até 100% não é um padrão: é `SEM_CORRESPONDENCIA` e passa
pelo screener quando nenhuma função configurada para exclusão corresponder.

A raridade será revelada pela aplicação das funções ao espaço amostral. O
contrato passou a prever limite percentual configurável, operador estrito `<` e
fotografia das frequências e padrões excludentes no início da execução. O valor
de 10% permanece apenas como hipótese experimental.
