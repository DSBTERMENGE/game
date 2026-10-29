# Teste da subetapa 18-C.7 — adaptadores dos três grupos de padrões

Data: 2026-10-29

## Objetivo

Integrar ao novo funil somente os detectores dos padrões selecionados pela
consulta de raridade, cobrindo os grupos PG_001, PG_002 e PG_003.

## Implementação

- Cada padrão raro selecionado gera um filtro próprio, identificado como
  `PAD_PD_nnn`.
- O filtro usa o detector oficial registrado para o código estável do padrão.
- Padrões no limite ou acima dele não geram filtro e seus detectores não são
  executados.
- Uma correspondência rara exclui imediatamente a combinação; os filtros
  seguintes não a recebem.
- A exclusão é contabilizada no padrão específico que a provocou.
- As evidências registram grupo, padrão, resultado do detector, quantidade e
  percentual históricos, limite, operador e denominador.

## Casos manuais

Foram validados casos positivos individuais para PD_001 a PD_009. Também foram
testados:

- detector cadastrado, mas não selecionado, sem nenhuma chamada;
- combinação que corresponde a dois padrões raros, sendo contabilizada apenas
  no primeiro filtro do funil;
- segunda combinação chegando ao filtro seguinte após passar pelo primeiro.

## Execução real somente leitura

Configuração: limite estrito de 10%, fotografia de 3.069 sorteios e amostra
protegida de 5.000 combinações.

Padrões selecionados pelo SQL:

- PG_001: PD_002 e PD_003;
- PG_002: PD_005 e PD_006;
- PG_003: PD_009.

Resultado após os níveis estatístico e geométrico:

| Filtro | Avaliações | Exclusões | Saldo |
|---|---:|---:|---:|
| PD_002 | 423 | 3 | 420 |
| PD_003 | 420 | 0 | 420 |
| PD_005 | 420 | 3 | 417 |
| PD_006 | 417 | 0 | 417 |
| PD_009 | 417 | 3 | 414 |

Fechamento completo da amostra:

- analisadas: 5.000;
- excluídas pelos três níveis: 4.586;
- aprovadas: 414;
- reconciliação: verdadeira;
- checksum da fotografia:
  `45b9f7eb48f98da6d44458501be22354c5ec10f50d6b50999e91b7c7c034eb99`.

## Regressão

- 3 testes específicos novos aprovados;
- 503 testes Python aprovados;
- os `ResourceWarning` antigos de arquivos do frontend não causaram falha.

## Resultado

Subetapa 18-C.7 aprovada tecnicamente. Nenhum dado do banco foi alterado.
