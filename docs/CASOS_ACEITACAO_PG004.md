# Casos de aceitação — PG_004 Arranjos diagonais

Estes casos preparam a homologação independente do analisador categórico
`PAD_PG_004`. Eles não classificam raridade: conferem somente a resposta
geométrica canônica que depois será comparada com a fotografia histórica.

| Caso | Dezenas | Resposta esperada |
|---|---|---|
| Uma assinatura E com lacunas nulas | 04, 15, 26, 37, 48, 59 | `0D5E` |
| Nenhuma referência longa | 01, 02, 03, 08, 09, 10 | `SEM_REFERENCIA_LONGA` |
| Quatro assinaturas no mesmo resultado | 01, 07, 25, 29, 44, 49 | `0D0E\|0D1E\|1D0E\|1D1E` |
| Assinatura cruzada 2D2E | 15, 17, 26, 35, 37, 60 | `0D2E\|2D0E\|2D2E` |

Regras da resposta:

- as dezenas de entrada são ordenadas antes da análise;
- cada assinatura aparece no máximo uma vez;
- várias assinaturas são ordenadas e separadas por `|`;
- ausência de assinatura usa somente `SEM_REFERENCIA_LONGA`;
- percentual, limite e decisão de exclusão não fazem parte deste critério.

O critério possui tipo futuro `CATEGORICO`. Ele permanecerá fora do registro
de produção até que uma migração autorizada amplie o esquema de validação e
grave referências independentes para as amostras ativas. Assim, a trava atual
do Screener não será contornada.
