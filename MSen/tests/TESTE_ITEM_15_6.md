# Evidência do Item 15.6 — reconciliação histórica do PD_003

Data: 2026-10-27.

O script somente de leitura `reconciliar_pd003_historico.py` submeteu os 3.069
resultados ao detector aprovado de PD_003.

## Ocorrências recalculadas

| Concurso | Data | Dezenas armazenadas | Bloco consecutivo de PD_003 |
|---:|---|---|---|
| 186 | 1999-09-25 | 24, 26, 51, 25, 14, 23 | 23, 24, 25, 26 |
| 509 | 2003-10-29 | 32, 55, 34, 35, 28, 33 | 32, 33, 34, 35 |
| 2052 | 2018-06-23 | 57, 50, 56, 51, 58, 59 | 56, 57, 58, 59 |
| 2789 | 2024-10-24 | 19, 03, 17, 55, 20, 18 | 17, 18, 19, 20 |
| 2908 | 2025-08-30 | 37, 38, 20, 36, 50, 35 | 35, 36, 37, 38 |

Todas as cinco ocorrências históricas possuem maior bloco de exatamente quatro
dezenas. Não houve ocorrência de bloco de cinco ou seis no histórico atual.

## Intervalos e resumo

- Intervalos entre concursos: 323, 1.543, 737 e 119.
- Quantidade recalculada/persistida: 5 / 5.
- Intervalo médio recalculado/persistido: 680,500000 / 680,500000.
- Desvio-padrão populacional recalculado/persistido:
  545,478460 / 545,478460.

As três medidas persistidas coincidem exatamente. Mediana dos resultados não
faz parte do padrão PD_003: ela pertence à categoria separada de critérios
estatísticos. Nenhuma coluna de mediana é necessária em `padroes_subgrupo`.

Resultado: PD_003 reconciliado. Nenhum dado foi escrito ou recalculado no banco.
