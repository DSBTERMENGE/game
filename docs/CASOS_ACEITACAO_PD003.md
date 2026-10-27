# Casos de aceitação do piloto PD_003

Piloto: `PD_003 — Mais de três dezenas sequenciais`.

Regra proposta para validação: o detector retorna `true` quando o maior bloco
de dezenas numericamente consecutivas possui tamanho quatro, cinco ou seis. O
resultado pertence exclusivamente a PD_003, sem ser contado novamente em
PD_001 ou PD_002.

## Casos que devem detectar PD_003

| Caso | Dezenas | Maior bloco | Resposta esperada | Motivo |
|---|---|---|---|---|
| A1 | 01, 02, 03, 04, 20, 40 | 01–04 (4) | `true` | Bloco de quatro. |
| A2 | 10, 11, 12, 13, 14, 60 | 10–14 (5) | `true` | Bloco de cinco. |
| A3 | 25, 26, 27, 28, 29, 30 | 25–30 (6) | `true` | As seis são consecutivas. |
| A4 | 40, 04, 02, 20, 03, 01 | 01–04 (4) | `true` | A ordem de entrada não interfere. |
| A5 | 09, 10, 11, 12, 30, 50 | 09–12 (4) | `true` | Sequência numérica atravessa 10/11; linhas da matriz não interferem. |
| A6 | 10, 20, 21, 22, 23, 24 | 20–24 (5) | `true` | O bloco pode estar no meio do resultado. |
| A7 | 01, 02, 03, 04, 50, 51 | 01–04 (4) | `true` | Um par adicional não muda o maior bloco. |
| A8 | 20, 40, 57, 58, 59, 60 | 57–60 (4) | `true` | Bloco válido no limite superior. |

## Casos que não devem detectar PD_003

| Caso | Dezenas | Maior bloco | Resposta esperada | Motivo |
|---|---|---|---|---|
| N1 | 10, 25, 26, 27, 50, 58 | 25–27 (3) | `false` | Exatamente três pertence a PD_002. |
| N2 | 01, 02, 03, 20, 21, 22 | dois blocos de 3 | `false` | Blocos separados não são somados. |
| N3 | 01, 02, 10, 11, 30, 50 | dois blocos de 2 | `false` | Nenhum bloco supera três. |
| N4 | 01, 02, 03, 10, 11, 30 | 01–03 (3) | `false` | Um bloco de três mais um par continua fora de PD_003. |
| N5 | 01, 10, 20, 30, 40, 60 | 1 | `false` | Não há dezenas consecutivas. |
| N6 | 01, 02, 03, 58, 59, 60 | dois blocos de 3 | `false` | 60 e 01 não formam sequência circular. |

## Entradas que devem produzir erro

| Caso | Entrada | Erro esperado | Motivo |
|---|---|---|---|
| E1 | 01, 02, 03, 04, 04, 20 | `ValueError` | Dezena repetida não é permitida. |
| E2 | 00, 01, 02, 03, 04, 05 | `ValueError` | Dezena abaixo de 01. |
| E3 | 01, 02, 03, 04, 05, 61 | `ValueError` | Dezena acima de 60. |
| E4 | 01, 02, 03, 04, 05 | `ValueError` | A entrada não possui seis dezenas. |
| E5 | 01, 02, 03, 04, 05, `"06"` | `TypeError` | Todas as dezenas devem ser inteiras. |
| E6 | `true`, 02, 03, 04, 05, 06 | `TypeError` | Booleano não deve ser aceito como inteiro. |

## Regras confirmadas pelo usuário

1. A sequência é estritamente numérica; `09, 10, 11, 12` é válida mesmo
   atravessando duas linhas visuais da matriz.
2. Não existe continuidade circular entre 60 e 01.
3. Dois blocos menores não são somados.
4. Um bloco de quatro ou mais pertence somente a PD_003, embora contenha pares
   e trincas internamente.

As quatro regras foram aprovadas em 2026-10-27. O usuário reforçou que a
classificação usa o maior bloco de dezenas consecutivas. Assim,
`58, 59, 60, 01, 02, 03` possui dois blocos separados de três, e
`01, 02, 03, 04, 20, 40` pertence somente a PD_003 pelo bloco de quatro.

Nenhum desses casos define tolerância ou autoriza exclusão.
