# Item 15.11 — preparação do padrão PD_006

Data: 2026-10-27

## Contrato validado

`PD_006` identifica quando a maior sequência vertical possui quatro, cinco ou
seis dezenas na mesma coluna e em linhas imediatamente subsequentes. Diferença
10 entre as dezenas é necessária. A classificação é exclusiva em relação a
PD_004 e PD_005. Casos detalhados: `docs/CASOS_ACEITACAO_PD006.md`.

## Reconciliação histórica

- Resultados avaliados: 3.069.
- Concursos encontrados: 363, 844, 2066 e 2453.
- Intervalos: 481, 1222 e 387.
- Ocorrências: 4.
- Percentual histórico: 0,130336%.
- Intervalo médio: 696,666667.
- Desvio-padrão populacional: 373,443734.

Os três valores estatísticos coincidiram exatamente com o PostgreSQL. A
consulta foi somente de leitura.

## Simulação sombra com tolerância hipotética de 3%

| Semente | Avaliadas | Marcadas | Percentual da amostra | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 5 | 0,10% | 4.995 |
| 42 | 5.000 | 0 | 0,00% | 5.000 |

Todas as 10.000 combinações foram realmente aprovadas. A diferença entre 5 e
0 marcações é compatível com a raridade e reforça que duas amostras pequenas não
estimam sozinhas o universo completo.

## Estado

- Detector existente passou nos casos positivos, negativos e inválidos.
- PD_006 não foi incluído na configuração ativa.
- PD_003 e PD_002 permanecem como as únicas regras ativas.
- O processamento integral permanece bloqueado.
- Nenhuma escrita foi feita no banco.

## Ativação autorizada

O usuário aprovou detector, operador inclusivo `<=`, tolerância de 3% e falha
conservadora. PD_006 foi ativado como terceiro filtro da amostra protegida:

- PD_003: 5.000 avaliações, 11 exclusões, saldo 4.989;
- PD_002: 4.989 avaliações, 162 exclusões, saldo 4.827;
- PD_006: 4.827 avaliações, 5 exclusões, saldo 4.822;
- fechamento: `5.000 = 11 + 162 + 5 + 4.822`.

As cinco marcações sombra da semente principal chegaram ao terceiro filtro e
foram excluídas. Passaram 327 testes Python. O processamento integral continua
bloqueado e nenhuma escrita foi feita no banco.

Resultado: ciclo de PD_006 concluído com ativação somente na amostra protegida.
