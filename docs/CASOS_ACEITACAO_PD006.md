# Casos de aceitação do padrão PD_006

Padrão: `PD_006 — Mais de três dezenas em linhas subjacentes na mesma coluna`.

O detector procura a maior sequência vertical na matriz de seis linhas por dez
colunas. As dezenas precisam estar na mesma coluna e em linhas imediatamente
subsequentes, portanto a diferença entre vizinhas é 10. O padrão é exclusivo:
sequências verticais de dois pertencem a PD_004 e de três a PD_005.

## Casos positivos

| Caso | Dezenas | Sequência vertical | Esperado |
|---|---|---|---|
| P1 | 05, 15, 25, 35, 48, 59 | 05–35 (4) | `true` |
| P2 | 05, 15, 25, 35, 45, 59 | 05–45 (5) | `true` |
| P3 | 10, 20, 30, 40, 50, 60 | 10–60 (6) | `true` |
| P4 | 01, 11, 21, 31, 45, 56 | 01–31 (4) | `true` |
| P5 | 59, 35, 25, 05, 48, 15 | 05–35 fora de ordem | `true` |

## Casos negativos

| Caso | Dezenas | Motivo | Esperado |
|---|---|---|---|
| N1 | 01, 12, 23, 34, 45, 56 | Nenhuma sequência vertical | `false` |
| N2 | 10, 25, 38, 45, 51, 59 | Mesma coluna sem linhas subjacentes | `false` |
| N3 | 10, 25, 35, 48, 51, 59 | Maior sequência tem dois | `false` |
| N4 | 07, 17, 27, 34, 45, 56 | Maior sequência tem três | `false` |
| N5 | 05, 15, 25, 32, 42, 59 | Uma tripla e um par não são somados | `false` |

Entradas com quantidade diferente de seis, repetição, valores fora de 01–60
ou tipos não inteiros permanecem inválidas.
