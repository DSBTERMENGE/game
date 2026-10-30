# Teste da subetapa 22.11 — avaliação da assertividade

Data: 2026-10-30.

## Regra aprovada

Cada fotografia histórica é comparada com o primeiro evento real estritamente
posterior ao seu concurso de corte.

- acerto: ocorrência dentro dos limites inteiros inclusivos;
- erro abaixo: ocorrência anterior ao limite inferior;
- erro acima: ocorrência posterior ao limite superior;
- erro absoluto: distância entre ocorrência real e previsão central;
- erro percentual: erro absoluto dividido pelo intervalo real entre o último
  evento conhecido e o próximo, multiplicado por 100;
- censurado: falta evento anterior, estatística completa ou próximo evento
  conhecido; não entra no denominador de acertos e erros.

O número absoluto do concurso não é denominador do erro percentual. A avaliação
não altera nem recria as fotografias históricas.

## Relatório da página

A série selecionada apresenta:

- quantidade avaliável, acertos, erros e censurados;
- percentual de acerto;
- erro absoluto médio em concursos;
- erro percentual médio;
- tabela das previsões abaixo ou acima da faixa, com corte, evento anterior,
  faixa, ocorrência real e erros.

Os censurados permanecem no resumo, mas não são falsamente tratados como erro.

## PostgreSQL efêmero

```text
python -m tests.validar_api_frequencias
```

Foram confirmadas a cobertura dos cortes, as ocorrências simples, 2VS e 3VS e a
censura do último corte sem futuro conhecido. O database temporário foi removido
e o `games` não foi alterado.

## Regressão

- Python: **629 testes aprovados**.
- JavaScript: **50 testes aprovados**.
- Google Chrome: **27 fluxos aprovados**.

Os testes unitários também confirmaram limites inclusivos, acerto, erro acima,
erro percentual e censura. O Chrome confirmou resumo e relatório de falhas em
1280 px e 520 px. Permaneceram somente avisos preexistentes de arquivos abertos
em testes do Screener e de módulos JavaScript sem `type: module`.
