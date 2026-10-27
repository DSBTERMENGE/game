# Casos de aceitação do padrão PD_009

Padrão: `PD_009 — Mais de três dezenas na mesma linha`.

O maior grupo deve possuir quatro, cinco ou seis dezenas na mesma linha da
matriz. Elas não precisam ser sequenciais. Grupos de dois pertencem a PD_007 e
grupos de três a PD_008.

## Casos positivos

| Dezenas | Ocupação máxima | Esperado |
|---|---:|---|
| 31, 33, 36, 40, 45, 56 | 4 | `true` |
| 41, 42, 43, 44, 45, 56 | 5 | `true` |
| 01, 02, 03, 04, 05, 06 | 6 | `true` |
| 09, 01, 07, 03, 25, 46 | 4, fora de ordem | `true` |

## Casos negativos

| Dezenas | Motivo | Esperado |
|---|---|---|
| 01, 12, 23, 34, 45, 56 | Uma em cada linha | `false` |
| 01, 05, 18, 27, 44, 59 | Maior ocupação tem dois | `false` |
| 21, 25, 30, 34, 45, 56 | Maior ocupação tem três | `false` |
| 01, 05, 09, 12, 18, 44 | Tripla e par não são somados | `false` |

Entradas fora do contrato comum dos detectores permanecem inválidas.
