# Item 15.12 — inventário do desvio-padrão das seis dezenas

Data: 2026-10-27

O piloto mede o desvio-padrão populacional das seis dezenas de cada resultado,
já armazenado em `resultados.desvio_padrao_media`.

## Distribuição histórica — 3.069 resultados

| Medida | Valor |
|---|---:|
| mínimo | 3,265986 |
| percentil 1% | 7,145546 |
| percentil 5% | 9,488000 |
| média dos desvios | 15,556645 |
| mediana dos desvios | 15,807874 |
| percentil 95% | 21,062340 |
| percentil 99% | 22,774694 |
| máximo | 25,959370 |
| desvio-padrão da distribuição | 3,492012 |

## Amostra reproduzível de 5.000

- Média dos desvios: 15,532399.
- Mediana: 15,767847.
- Mínimo: 3,349959; máximo: 25,538642.
- P01: 6,420128; P99: 22,808387.

## Comparação de regras ainda não aprovadas

A margem exemplificativa de ±20% em torno de 15,556645 produziria limites
12,445316 e 18,667974. Ela colocaria fora 1.197 resultados históricos e 1.996
combinações da amostra, sendo agressiva demais.

Como candidato para discussão, a faixa histórica P01/P99 é `7,145546` a
`22,774694`. Com comparação estrita, 31 históricos ficam abaixo e 31 acima,
totalizando 62 (`2,020202%`). Na amostra, 78 ficam abaixo e 54 acima, total 132.

## Estado

- Levantamento somente de leitura.
- Nenhuma política de desvio-padrão foi criada ou ativada.
- O funil atual e a trava integral não foram alterados.

Resultado: inventário concluído; a faixa precisa de aprovação antes do modo
sombra.
