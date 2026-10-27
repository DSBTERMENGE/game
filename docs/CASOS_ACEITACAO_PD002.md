# Casos de aceitação do padrão PD_002

Padrão: `PD_002 — Três dezenas sequenciais`.

O detector classifica pelo maior bloco consecutivo em ordem numérica. O padrão
é exclusivo: blocos de dois pertencem a PD_001 e blocos de quatro ou mais a
PD_003. `60` e `01` não formam continuidade circular.

## Casos positivos

| Caso | Dezenas | Maior bloco | Esperado |
|---|---|---|---|
| P1 | 10, 25, 26, 27, 50, 58 | 25–27 | `true` |
| P2 | 01, 02, 03, 10, 20, 60 | 01–03 | `true` |
| P3 | 01, 10, 20, 58, 59, 60 | 58–60 | `true` |
| P4 | 01, 02, 03, 20, 21, 40 | 01–03 | `true` |
| P5 | 30, 10, 12, 11, 50, 60 | 10–12 | `true` |

## Casos negativos

| Caso | Dezenas | Motivo | Esperado |
|---|---|---|---|
| N1 | 01, 03, 05, 07, 09, 11 | Nenhum bloco | `false` |
| N2 | 10, 25, 26, 38, 50, 58 | Maior bloco tem dois | `false` |
| N3 | 01, 02, 03, 04, 20, 40 | Maior bloco tem quatro | `false` |
| N4 | 01, 02, 10, 11, 30, 40 | Dois blocos de dois não são somados | `false` |
| N5 | 01, 02, 20, 30, 59, 60 | 60/01 não fecha bloco circular | `false` |

Entradas com quantidade diferente de seis, repetição, valores fora de 01–60
ou tipos não inteiros continuam inválidas pelo contrato comum dos detectores.
