# Teste da subetapa 23.6 — motor de backtest e pesquisa comparativa

Data: 03/11/2026.

## Escopo concluído

- execução inclusiva a partir do concurso 500, sempre com corte `alvo - 1`;
- separação entre seleção e leitura do resultado real;
- persistência atômica de cada alvo com suas 60 avaliações;
- classe exclusiva de acertos entre 0 e 6;
- cancelamento seguro e retomada somente dos alvos ausentes;
- resumo de classes, quantidades, cobertura, precisão e custo combinatório;
- detalhamento por concurso para auditoria;
- comparação condicionada à mesma origem, período, versão e cobertura;
- preservação das pesquisas originais, sem recalcular ou sobrescrever.

## Testes unitários

Executado:

```text
python -m unittest tests.test_backtest_selecao_dezenas \
  tests.test_selecao_dezenas -v
```

Resultado: **9 testes aprovados**.

## PostgreSQL efêmero

Executado:

```text
python -m tests.validar_backtest_selecao_dezenas
```

O ensaio copiou os resultados 1 a 505 para um database temporário e validou:

- duas pesquisas concluídas e comparáveis;
- seis alvos em cada pesquisa;
- classes exclusivas cuja soma corresponde aos seis concursos;
- cancelamento de uma terceira pesquisa depois de dois alvos;
- retomada nos quatro alvos restantes, sem duplicar os dois anteriores;
- 18 alvos e exatamente 1.080 avaliações de dezenas;
- consulta detalhada dos concursos 500 a 505.

O database temporário foi removido ao final. Nenhuma pesquisa de backtest foi
gravada no banco local persistente.

## Regressão

Executado:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **653 testes aprovados**. Permaneceram apenas três avisos
preexistentes de arquivos do Screener abertos durante testes.
