# Item 15.12 — inventário da mediana das seis dezenas

Data: 2026-10-27

O piloto considera a mediana das seis dezenas, calculada pela média entre a
terceira e a quarta dezena após ordenação. O valor possui uma casa decimal.

## Distribuição histórica — 3.069 resultados

| Medida | Valor |
|---|---:|
| mínimo | 5,0 |
| percentil 1% | 10,5 |
| percentil 5% | 15,5 |
| média das medianas | 30,677908 |
| mediana das medianas | 31,0 |
| percentil 95% | 45,5 |
| percentil 99% | 50,5 |
| máximo | 56,5 |
| desvio-padrão da distribuição | 9,284300 |

## Amostra reproduzível de 5.000

- Média das medianas: 30,543000.
- Mediana das medianas: 30,5.
- Mínimo: 4,5; máximo: 57,0.
- P01: 10,5; P99: 50,5.

## Comparação de regras ainda não aprovadas

A margem exemplificativa de ±20% em torno de 30,677908 produziria limites
24,542326 e 36,813490. Colocaria fora 1.678 históricos e 2.765 combinações da
amostra, sendo inadequada para o piloto.

A faixa candidata P01/P99 é `10,5` a `50,5`. Com comparação estrita, 28
históricos ficam abaixo e 29 acima, total 57 (`1,857283%`). Na amostra, 43
ficam abaixo e 49 acima, total 92.

## Estado

- Levantamento somente de leitura.
- Cálculo amostral testado, inclusive com entrada fora de ordem.
- Passaram 355 testes.
- Nenhuma política de mediana foi criada ou ativada.
- Funil, banco e trava integral não foram alterados.

Resultado: inventário concluído; faixa depende de aprovação antes do modo
sombra.
