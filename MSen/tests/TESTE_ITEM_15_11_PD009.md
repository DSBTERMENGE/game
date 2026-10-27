# Item 15.11 — avaliação do padrão PD_009

Data: 2026-10-27

## Contrato e histórico

`PD_009` identifica quatro, cinco ou seis dezenas na mesma linha, sem exigir
sequencialidade. A classificação é exclusiva em relação a PD_007 e PD_008.
Casos: `docs/CASOS_ACEITACAO_PD009.md`.

- Resultados históricos: 3.069.
- Ocorrências: 93.
- Percentual histórico: 3,030303%.
- Primeira ocorrência: concurso 9.
- Última ocorrência: concurso 3.058.
- Intervalo médio: 33,141304.
- Desvio-padrão populacional: 35,099728.

Quantidade, média e desvio coincidiram exatamente com o PostgreSQL, em consulta
somente de leitura.

## Simulação sombra com tolerância de 3%

| Semente | Detectadas pelo detector | Marcadas pela política | Exclusões reais |
|---:|---:|---:|---:|
| 20261027 | 177 | 0 | 0 |
| 42 | 154 | 0 | 0 |

O detector funcionou nas duas amostras, mas a política não marcou nenhuma
combinação porque `3,030303% > 3%`. Isso confirma que a comparação utiliza o
percentual histórico do padrão, não o percentual encontrado na amostra.

## Estado

- PD_009 não foi incluído na configuração ativa.
- Não há justificativa para ativá-lo com a tolerância atual de 3%.
- As regras ativas permanecem PD_003, PD_002, PD_006 e PD_005.
- Processamento integral continua bloqueado; banco não foi escrito.

Resultado: ciclo encerrado sem proposta de ativação de PD_009.
