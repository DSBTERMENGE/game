# Evidência do Item 15.1 — inventário dos critérios

Data: 2026-10-27.

Fonte: leitura do PostgreSQL local e do catálogo Python pelo script
`MSen/tests/inventariar_criterios.py`. Denominador: 3.069 resultados.

## PG_001 — Dezenas sequenciais

| Código | Nome | Função Python | Ocorrências | Percentual | Intervalo médio | Desvio-padrão | Estado |
|---|---|---|---:|---:|---:|---:|---|
| PD_001 | Duas dezenas sequenciais | `detectar_duas_dezenas_sequenciais` | 1.192 | 38,840013% | 2,575147 | 1,995592 | Implementado |
| PD_002 | Três dezenas sequenciais | `detectar_tres_dezenas_sequenciais` | 92 | 2,997719% | 33,527473 | 33,637806 | Implementado |
| PD_003 | Mais de três dezenas sequenciais | `detectar_mais_de_tres_dezenas_sequenciais` | 5 | 0,162920% | 680,500000 | 545,478460 | Implementado |

## PG_002 — Dezenas na mesma coluna

| Código | Nome | Função Python | Ocorrências | Percentual | Intervalo médio | Desvio-padrão | Estado |
|---|---|---|---:|---:|---:|---:|---|
| PD_004 | Duas dezenas em linhas subjacentes na mesma coluna | `detectar_duas_dezenas_na_mesma_coluna` | 1.037 | 33,789508% | 2,960425 | 2,387099 | Implementado |
| PD_005 | Três dezenas em linhas subjacentes na mesma coluna | `detectar_tres_dezenas_na_mesma_coluna` | 66 | 2,150538% | 45,969231 | 42,006948 | Implementado |
| PD_006 | Mais de três dezenas em linhas subjacentes na mesma coluna | `detectar_mais_de_tres_dezenas_na_mesma_coluna` | 4 | 0,130336% | 696,666667 | 373,443734 | Implementado |

## PG_003 — Dezenas na mesma linha

| Código | Nome | Função Python | Ocorrências | Percentual | Intervalo médio | Desvio-padrão | Estado |
|---|---|---|---:|---:|---:|---:|---|
| PD_007 | Duas dezenas na mesma linha | `detectar_duas_dezenas_na_mesma_linha` | 2.053 | 66,894754% | 1,495127 | 0,852399 | Implementado |
| PD_008 | Três dezenas na mesma linha | `detectar_tres_dezenas_na_mesma_linha` | 863 | 28,119909% | 3,554524 | 2,902303 | Implementado |
| PD_009 | Mais de três dezenas na mesma linha | `detectar_mais_de_tres_dezenas_na_mesma_linha` | 93 | 3,030303% | 33,141304 | 35,099728 | Implementado |

## Conferências e observações

- 3 grupos, 9 cadastros e 9 detectores.
- Nenhum cadastro sem detector e nenhum detector sem cadastro.
- Todos possuem estatísticas preenchidas no banco.
- O catálogo executável agrega corretamente PD_001 a PD_009, mas sua docstring
  ainda declara PD_001 a PD_006. Isso foi apenas registrado, não corrigido.
- O nome armazenado de PD_008 contém dois espaços entre `mesma` e `linha`.
  Também foi apenas registrado, pois o item é somente de leitura.
- Os percentuais são descritivos. Nenhum deles autoriza exclusão.

Nenhuma escrita, recálculo, correção ou ativação foi realizada.
