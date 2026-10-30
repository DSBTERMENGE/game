# Teste da subetapa 22.3 — estrutura histórica materializada

Data: 2026-10-30.

## Estrutura criada

`geracoes_frequencia_dezenas` identifica uma construção isolada da série e
preserva assinatura, JSON canônico da configuração, versão, estado, concursos
inicial/final e datas. Um índice parcial impede duas gerações ativas.

Em `historico_frequencia_dezenas`, uma linha representa:

```text
geração + número do concurso + dezena + tipo de evento
```

São armazenados quantidades, mínimo, máximo, média, mediana, desvio-padrão,
previsão central, limites decimais exatos e limites inteiros operacionais. Não
existem colunas `res_01` a `res_06` nem resultado futuro copiado.

Com zero intervalos, todos os campos estatísticos são obrigatoriamente nulos.
Com intervalos, todos devem estar presentes e coerentes. A cascata existe
somente entre uma geração e suas fotografias, nunca sobre `resultados`.
Os limites operacionais precisam ser positivos, mas podem estar antes do corte
da fotografia quando a faixa prevista já tiver passado sem novo evento.

## Volume esperado

Do concurso 500 ao 3.090 são 2.591 cortes: 155.460 linhas por tipo de evento ou
466.380 para `SIMPLES`, `2VS` e `3VS`.

## PostgreSQL efêmero

```text
python -m tests.validar_historico_frequencia
```

Foram confirmados: idempotência da 019, estados com e sem base, rejeição de
estatística parcial, unicidade, uma única geração ativa, índice do gráfico no
plano de consulta e cascata limitada à geração. O database efêmero foi removido
e o `games` persistente não foi alterado.

## Regressão

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **597 testes aprovados**. Permaneceram somente avisos preexistentes
de arquivos abertos nos testes do Screener.
