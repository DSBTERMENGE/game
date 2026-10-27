# Item 15.13 — inventário da extensão geométrica aberta

Data: 2026-10-27

A extensão aberta é a soma euclidiana dos cinco segmentos que unem, em ordem
crescente, os centros das seis dezenas na matriz 10 × 6.

## Distribuição histórica — 3.069 resultados

| Medida | Valor |
|---|---:|
| mínimo | 6,414214 |
| percentil 1% | 8,650282 |
| percentil 5% | 10,812559 |
| média | 18,398295 |
| mediana | 17,875351 |
| percentil 95% | 27,611501 |
| percentil 99% | 32,300058 |
| máximo | 39,615072 |
| desvio-padrão | 5,225258 |

## Amostra reproduzível de 5.000

- Média: 18,221663; mediana: 17,754060.
- Mínimo: 6,236068; máximo: 38,370727.
- P01: 8,575513; P99: 31,811413.

## Comparação de regras ainda não aprovadas

A margem de ±20% em torno da média histórica produziria limites 14,718636 e
22,077954, colocando fora 1.523 históricos e 2.454 amostrais. É agressiva.

A faixa candidata P01/P99 é `8,650282` a `32,300058`. Reaplicando exatamente os
limites arredondados a seis casas, 33 históricos ficam abaixo e 31 acima, total
64 (`2,085370%`). Na amostra, 61 ficam abaixo e 45 acima, total 106. A contagem
anterior de 61/102 usava o percentil bruto antes do arredondamento exibido.

## Estado

- Os 3.069 históricos geométricos foram lidos sem escrita.
- A amostra usou a função geométrica de produção e precisão de 12 casas.
- Nenhuma política geométrica foi criada ou ativada.
- Funil e trava integral não foram alterados.

Resultado: inventário concluído; faixa depende de aprovação para modo sombra.
