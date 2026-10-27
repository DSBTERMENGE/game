# Casos de aceitação do padrão PD_005

Padrão: `PD_005 — Três dezenas em linhas subjacentes na mesma coluna`.

O maior grupo vertical deve possuir exatamente três dezenas. Elas precisam
estar na mesma coluna e em linhas imediatamente subsequentes, com diferença 10.
Grupos de dois pertencem a PD_004 e grupos de quatro ou mais a PD_006.

## Casos positivos

| Caso | Dezenas | Sequência vertical | Esperado |
|---|---|---|---|
| P1 | 07, 17, 27, 34, 45, 56 | 07–27 | `true` |
| P2 | 05, 15, 25, 32, 42, 59 | 05–25; par adicional não altera | `true` |
| P3 | 30, 40, 50, 01, 23, 56 | 30–50 | `true` |
| P4 | 40, 20, 30, 01, 23, 56 | 20–40 fora de ordem | `true` |
| P5 | 01, 11, 21, 35, 45, 60 | 01–21; par adicional | `true` |

## Casos negativos

| Caso | Dezenas | Motivo | Esperado |
|---|---|---|---|
| N1 | 01, 12, 23, 34, 45, 56 | Nenhuma sequência vertical | `false` |
| N2 | 10, 25, 35, 48, 51, 59 | Maior sequência tem dois | `false` |
| N3 | 05, 15, 25, 35, 48, 59 | Maior sequência tem quatro | `false` |
| N4 | 05, 15, 22, 32, 48, 59 | Dois pares não são somados | `false` |
| N5 | 05, 25, 45, 01, 32, 59 | Mesma coluna, linhas não subsequentes | `false` |

Entradas com quantidade diferente de seis, repetição, valores fora de 01–60
ou tipos não inteiros permanecem inválidas.
