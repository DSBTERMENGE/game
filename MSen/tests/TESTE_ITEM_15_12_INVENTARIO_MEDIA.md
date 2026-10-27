# Item 15.12 — inventário do piloto de média aritmética

Data: 2026-10-27

## Separação conceitual

A média aritmética é um critério estatístico da própria combinação. Ela não é
um padrão cadastrado em `padroes_subgrupo` e não utilizará os contadores de
ocorrência dos padrões históricos.

## Distribuição histórica — 3.069 resultados

| Medida | Valor |
|---|---:|
| mínimo | 10,500000 |
| percentil 1% | 15,000000 |
| percentil 5% | 19,666667 |
| média das médias | 30,515749 |
| mediana das médias | 30,666667 |
| percentil 95% | 41,333333 |
| percentil 99% | 45,886666 |
| máximo | 55,166667 |
| desvio-padrão populacional | 6,659667 |

## Distribuição da amostra reproduzível de 5.000

- Média das médias: 30,554067.
- Mediana: 30,666667.
- Desvio-padrão populacional: 6,870927.
- Mínimo: 9,333333; máximo: 52,666667.

## Comparação de regras ainda não aprovadas

A margem exemplificativa de ±20% em torno de 30,515749 produziria limites
24,412599 e 36,618899. Ela colocaria fora da faixa 1.151 resultados históricos
e 1.910 combinações da amostra, sendo agressiva demais para um primeiro piloto.

Como alternativa para discussão, os limites históricos P01/P99 seriam
15,000000 e 45,886666. Usando comparação estrita fora da faixa (`< P01` ou
`> P99`), 59 resultados históricos ficariam fora, equivalentes a 1,922450%, e
108 combinações da amostra seriam marcadas.

## Estado

- O levantamento foi somente de leitura.
- Nenhuma política estatística foi implementada ou conectada ao funil.
- Nenhuma tolerância foi aprovada.
- As quatro regras históricas ativas e a trava integral não foram alteradas.
- Passaram 338 testes antes do acréscimo documental.

Resultado: inventário concluído; o contrato do piloto depende da decisão do
usuário sobre a faixa e os limites inclusivos ou exclusivos.
