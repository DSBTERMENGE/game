# Etapa 11.2 — referência anterior à unificação do Screener

Fotografia do Teste do Screener executado em 18/11/2026, antes da troca do
motor usado pela página Seleção de dezenas.

## Identificação

- execução: `77081a95-6271-475e-ab3b-6fbfcf397f7a`;
- escopo: amostra pseudoaleatória reproduzível de 5.000 combinações;
- semente: `20261027`;
- limite de raridade ainda vigente nesta referência: `10.000000%`;
- checksum da fotografia: `b2ca2d3f152bc49a4f7988b380a83fa0814dfe7341e55b804c73be04b648b7d1`;
- duração do motor: `1,836199 s`;
- duração total da execução assíncrona: `3,202 s`.

## Fechamento geral

| Analisadas | Excluídas | Aprovadas |
|---:|---:|---:|
| 5.000 | 4.633 | 367 |

Fechamento esperado: `5.000 = 4.633 + 367`.

## Família estatística

| Filtro | Entrada | Exclusões | Saldo |
|---|---:|---:|---:|
| `EST_SOMA_MEDIA` | 5.000 | 1.701 | 3.299 |
| `EST_MEDIANA` | 3.299 | 441 | 2.858 |
| `EST_DESVIO_PADRAO` | 2.858 | 857 | 2.001 |

Subtotal: entrada 5.000, exclusões 2.999 e saldo 2.001.

## Família geométrica

| Filtro | Entrada | Exclusões | Saldo |
|---|---:|---:|---:|
| `GEO_EXTENSAO` | 2.001 | 640 | 1.361 |
| `GEO_PERIMETRO` | 1.361 | 96 | 1.265 |
| `GEO_AREA` | 1.265 | 289 | 976 |
| `GEO_REGIOES` | 976 | 229 | 747 |
| `GEO_CENTRO_GRAVIDADE` | 747 | 324 | 423 |

Subtotal: entrada 2.001, exclusões 1.578 e saldo 423.

## Família de padrões

| Filtro | Entrada | Exclusões | Saldo |
|---|---:|---:|---:|
| `PAD_PD_002` | 423 | 3 | 420 |
| `PAD_PD_003` | 420 | 0 | 420 |
| `PAD_PD_005` | 420 | 3 | 417 |
| `PAD_PD_006` | 417 | 0 | 417 |
| `PAD_PD_009` | 417 | 3 | 414 |
| `PAD_PD_011` | 414 | 0 | 414 |
| `PAD_PG_004` | 414 | 47 | 367 |

Subtotal: entrada 423, exclusões 56 e saldo 367.

Os padrões booleanos selecionados pelo comportamento anterior foram `PD_002`,
`PD_003`, `PD_005`, `PD_006`, `PD_009` e `PD_011`. O filtro categórico de
diagonais foi aplicado separadamente como `PAD_PG_004`.

## Comparação anterior já produzida pelo sistema

- Screener anterior: 4.409 aprovadas;
- Screener extensível atual: 367 aprovadas;
- diferença: -4.042.

## Limitação desta referência

O contrato público da execução conserva as contagens e o relatório reconciliado,
mas não expõe a relação das 367 combinações aprovadas. Por isso esta fotografia
registra o fechamento por filtro, que é o dado disponível para a comparação da
unificação. Uma comparação futura de identidade das combinações exigirá que os
dois motores sejam executados diretamente sobre o mesmo iterador controlado.
