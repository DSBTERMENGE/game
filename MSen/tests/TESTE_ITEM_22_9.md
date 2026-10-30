# Teste da subetapa 22.9 — gráficos da fotografia atual

Data: 2026-10-30.

## Contrato implementado

`GET /api/frequencias/fotografia-atual` aceita `tipo_evento` igual a `SIMPLES`,
`2VS` ou `3VS`. A resposta usa a última fotografia da geração ativa e devolve as
60 dezenas em uma consulta, com:

- número de ocorrências e de intervalos;
- intervalo mínimo e máximo;
- média, mediana e desvio-padrão dos intervalos;
- concurso inicial/final, unidade e data da atualização.

Tipo desconhecido é recusado com HTTP 400. Simples, 2VS e 3VS usam o mesmo corte
temporal. O desvio permanece na unidade concurso e nunca é rotulado como
percentual.

## Interface

A página apresenta seis gráficos de colunas, um para cada medida contratada.
Cada gráfico possui 60 barras, unidade explícita e tooltip com dezena, valor e
quantidade de intervalos. Valores sem amostra suficiente permanecem nulos e são
descritos como `Sem intervalo suficiente`.

O seletor troca a fotografia completa entre ocorrência simples, 2VS e 3VS. O
cabeçalho informa período, soma dos intervalos contabilizados, unidade e data da
atualização. A grade possui rolagem própria em larguras normal e estreita.

## PostgreSQL efêmero

```text
python -m tests.validar_api_frequencias
```

Foram confirmadas 60 dezenas para cada tipo de evento no mesmo concurso final.
O database temporário foi removido e o `games` não foi alterado.

## Regressão

- Python: **627 testes aprovados**.
- JavaScript: **47 testes aprovados**.
- Google Chrome: **27 fluxos aprovados**.

No Chrome, foram conferidos seis cartões, 360 barras, troca para 2VS e layout em
1280 px e 520 px. Permaneceram somente avisos preexistentes de arquivos abertos
em testes do Screener e de módulos JavaScript sem `type: module`.
