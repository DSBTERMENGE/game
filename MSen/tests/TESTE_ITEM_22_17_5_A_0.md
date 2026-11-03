# Diagnóstico da subetapa 22.17.5-A.0

Data: 02/11/2026

## Resultado

O gráfico não está matematicamente ordenado de forma decrescente. A função usa
ordenação numérica crescente e foram encontradas zero inversões nas dezenas
08, 10 e 17.

## Amostra controlada

Entrada: `4, 1, 2, 2`.

Lista produzida: `1, 2, 2, 4`.

| Ordem | Intervalo real | X atual | Y atual |
|---:|---:|---:|---:|
| 1 | 1 | 25% | 25% |
| 2 | 2 | 50% | 50% |
| 3 | 2 | 75% | 50% |
| 4 | 4 | 100% | 100% |

O espaçamento horizontal atual é uniforme, mas está rotulado como percentual
acumulado. A altura também está normalizada pelo maior intervalo. Isso oculta a
leitura direta esperada: `(1,1)`, `(2,2)`, `(3,2)`, `(4,4)`.

## Dados reais

| Dezena | Intervalos | Primeiros valores | Últimos valores | Inversões |
|---:|---:|---|---|---:|
| 08 | 264 | 1, 1, 1, 1… | 39, 40, 43, 46 | 0 |
| 10 | 314 | 1, 1, 1, 1… | 34, 43, 43, 49 | 0 |
| 17 | 271 | 1, 1, 1, 1… | 40, 42, 42, 60 | 0 |

No SVG, valores maiores possuem coordenada Y numericamente menor porque a
origem vertical da tela fica no alto. Isso é o comportamento normal do SVG e
faz a curva subir visualmente conforme avança para a direita.

## Conclusão

A subetapa 22.17.5-A.1 deverá trocar a semântica dos eixos:

- X: posição ordinal real, de 1 a N, com espaçamento uniforme;
- Y: duração real do intervalo em concursos;
- percentuais: somente informação complementar.

Nenhuma alteração de código foi realizada neste diagnóstico.
