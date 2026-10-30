# Teste da subetapa 22.12 — fechamento da Etapa 22

Data: 2026-10-30.

## PostgreSQL temporário

Foram executados:

```text
python -m tests.validar_carga_historico_frequencia
python -m tests.validar_operacao_historico_frequencia
python -m tests.validar_api_frequencias
python -m tests.benchmark_carga_historico_frequencia
```

Os validadores confirmaram carga completa, repetição idempotente, incremento,
equivalência matemática integral/parcelada, troca de configuração, rollback,
simulação, cancelamento, API, três tipos de evento, gráficos e assertividade.

Todos os databases temporários foram removidos. O `games` foi somente lido para
copiar os resultados do benchmark e não foi alterado.

## Benchmark local

Base: 3.069 resultados, primeiro corte 500, três tipos de evento.

| Medida | Resultado |
|---|---:|
| Cortes históricos | 2.570 |
| Fotografias gravadas | 462.600 |
| Carga completa | 146,761 s |
| Acréscimo de um concurso / 180 linhas | 0,189 s |
| Três fotografias atuais | 0,003 s |
| Série de 2.571 pontos com assertividade | 0,057 s |
| Tabela e índices | 127.811.584 bytes |
| Somente índices | 71.688.192 bytes |

Os tempos são referência deste equipamento e não garantia para outro ambiente.

## Regressão final

- Python: **629 testes aprovados**.
- JavaScript: **50 testes aprovados**.
- Google Chrome: **27 fluxos aprovados**.

Permaneceram somente avisos preexistentes de arquivos abertos em testes do
Screener, de módulos JavaScript sem `type: module` e de `NO_COLOR` no Playwright.

## Documentação reconciliada

Foram atualizados plano, funcionamento, visão do projeto, modelo PostgreSQL,
código Python, API, índice documental, decisões, funcionalidades e continuidade.
Nenhum commit ou push foi executado.
