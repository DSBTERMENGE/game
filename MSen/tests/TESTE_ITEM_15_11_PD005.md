# Item 15.11 — preparação do padrão PD_005

Data: 2026-10-27

## Contrato validado

`PD_005` identifica quando a maior sequência vertical possui exatamente três
dezenas na mesma coluna e em linhas imediatamente subsequentes. Diferença 10 é
necessária. A classificação é exclusiva em relação a PD_004 e PD_006. Casos:
`docs/CASOS_ACEITACAO_PD005.md`.

## Reconciliação histórica

- Resultados avaliados: 3.069.
- Primeira ocorrência: concurso 57.
- Última ocorrência: concurso 3.045.
- Ocorrências: 66.
- Percentual histórico: 2,150538%.
- Intervalo médio: 45,969231.
- Desvio-padrão populacional: 42,006948.

Quantidade, média e desvio coincidiram exatamente com o PostgreSQL. A consulta
foi somente de leitura.

## Simulação sombra com tolerância hipotética de 3%

| Semente | Avaliadas | Marcadas | Percentual da amostra | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 113 | 2,26% | 4.887 |
| 42 | 5.000 | 97 | 1,94% | 4.903 |

Todas as 10.000 combinações foram realmente aprovadas e nenhuma foi excluída.

## Estado

- Detector passou nos casos positivos, negativos e inválidos.
- PD_005 não foi incluído na configuração ativa.
- PD_003, PD_002 e PD_006 permanecem como únicas regras ativas.
- Processamento integral continua bloqueado; banco não foi escrito.

## Ativação autorizada

O usuário aprovou os quatro critérios. PD_005 foi ativado como quarto filtro:

- PD_003: 5.000 avaliações, 11 exclusões, saldo 4.989;
- PD_002: 4.989 avaliações, 162 exclusões, saldo 4.827;
- PD_006: 4.827 avaliações, 5 exclusões, saldo 4.822;
- PD_005: 4.822 avaliações, 110 exclusões, saldo 4.712;
- fechamento: `5.000 = 11 + 162 + 5 + 110 + 4.712`.

Das 113 marcações sombra de PD_005, três já tinham sido excluídas por filtros
anteriores. O contador do funil atribuiu corretamente somente as 110 exclusões
líquidas ao quarto filtro. Passaram 331 testes; o processamento integral segue
bloqueado e o banco não foi escrito.

Resultado: ciclo de PD_005 concluído com ativação somente na amostra protegida.
