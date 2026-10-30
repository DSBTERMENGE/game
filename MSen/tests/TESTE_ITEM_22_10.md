# Teste da subetapa 22.10 — gráfico histórico por dezena

Data: 2026-10-30.

## Visualização implementada

A página permite selecionar:

- uma dezena de 01 a 60;
- ocorrência simples, 2VS ou 3VS;
- concurso inicial e final, com limite de 5.000 concursos por consulta.

O eixo horizontal é `numero_do_concurso`. Duas visualizações evitam misturar
grandezas diferentes:

1. evolução do intervalo mínimo, médio e máximo, em concursos;
2. faixa prevista inferior, previsão central, faixa superior e ocorrências
   reais, na escala dos números dos concursos.

Ausências estatísticas permanecem nulas e interrompem a linha até existir
amostra suficiente. A faixa é desenhada somente onde os dois limites existem.

## Ocorrências reais

Os pontos são consultados diretamente de `resultados`, sem copiar as seis
dezenas e sem alterar as fotografias históricas:

- `SIMPLES`: a dezena está presente no concurso;
- `2VS`: também está presente no concurso imediatamente anterior;
- `3VS`: também está presente nos dois concursos imediatamente anteriores.

Portanto, uma sequência longa produz eventos sobrepostos conforme a regra já
aprovada para o motor. Os pontos reais são apenas sobreposição visual; a
avaliação formal de acertos e erros permanece na subetapa 22.11.

## PostgreSQL efêmero

```text
python -m tests.validar_api_frequencias
```

Foram confirmadas série filtrada, ocorrências reais simples, 2VS e 3VS e
ausência de cópia das dezenas dos resultados. O database temporário foi
removido e o `games` não foi alterado.

## Regressão

- Python: **627 testes aprovados**.
- JavaScript: **50 testes aprovados**.
- Google Chrome: **27 fluxos aprovados**.

O Chrome confirmou os dois cartões históricos, pontos reais, filtros e layout
em 1280 px e 520 px. Permaneceram somente avisos preexistentes de arquivos
abertos em testes do Screener e de módulos JavaScript sem `type: module`.
