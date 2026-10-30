# Teste da subetapa 22.4 — motor acumulado de frequência

Data: 2026-10-30.

## Implementação

`MotorFrequenciaAcumulada` processa um concurso por vez, em ordem crescente,
mantendo para cada dezena os eventos simples, 2VS e 3VS já concluídos.

- evento simples: concurso em que a dezena ocorreu;
- 2VS: concluído a partir da segunda ocorrência consecutiva;
- 3VS: concluído a partir da terceira ocorrência consecutiva;
- sequências maiores produzem janelas sobrepostas conforme o contrato 22.0;
- lacuna ou retrocesso de concurso são recusados.

O motor mantém quantidades, intervalos ordenados, soma e soma dos quadrados. A
média e o desvio são calculados sem arredondamento intermediário; somente os
campos finais recebem seis casas com `ROUND_HALF_UP`.

A previsão usa:

```text
último evento + média dos intervalos ± multiplicador × desvio populacional
```

O multiplicador é adimensional. Média, desvio e limites permanecem na unidade
concurso. Os limites operacionais usam `floor` e `ceil` externos e são
inclusivos.

## Testes matemáticos

Foram confirmados:

- primeira fotografia configurável;
- configuração inicial produzindo exatamente 180 linhas no concurso 500;
- repetição determinística do cálculo 1–500;
- sequências sobrepostas de 2VS e 3VS;
- interrupção e reinício de sequência;
- estados sem base usando `NULL`, sem inventar zero;
- média, desvio, previsão e arredondamento externo;
- fotografia do concurso 2 sem conhecer o 3VS concluído somente no concurso 3;
- igualdade entre execução integral e incremental em duas parcelas;
- reconciliação da série simples com `calcular_frequencias` já existente;
- rejeição de lacuna e concurso fora de ordem;
- saída individual por tipo de evento.

## Regressão

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **608 testes aprovados**. Permaneceram somente avisos preexistentes
de arquivos abertos nos testes do Screener.

Nenhum dado foi persistido e o database `games` não foi alterado.
