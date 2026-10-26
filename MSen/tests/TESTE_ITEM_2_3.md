# Teste do desvio-padrão — Item 2.3

## Data e escopo

- Data: 2026-10-26.
- Python: 3.13.5.
- Código: `src/msen/calculos/estatisticas_linha.py`.
- Testes: `tests/test_desvio_padrao.py`.
- Banco, Excel, API e interface: não acessados.

## Implementação testada

- `calcular_desvio_padrao_populacional`: função matemática genérica para uma
  sequência não vazia de `int` ou `Decimal`;
- `calcular_desvio_padrao_media`: aplica a função aos seis valores de um
  `ResultadoEntrada` validado;
- divisor populacional igual à quantidade de valores;
- precisão interna de 50 algarismos decimais;
- arredondamento `ROUND_HALF_UP` somente no resultado final;
- saída com seis casas decimais.

## Teste específico

```text
Ran 9 tests
OK
```

## Teste acumulado dos Itens 2.1, 2.2 e 2.3

```text
Ran 30 tests
OK
```

## Casos conferidos

- exemplo da apresentação 3069: `18.217818`;
- exemplo populacional clássico com resultado exato 2;
- valores iguais na função estatística genérica com resultado zero; esse caso é
  aplicável a intervalos e não representa uma linha de resultado válida;
- um único intervalo com resultado zero;
- independência da ordem de entrada;
- entrada em `Decimal` e precisão de seis casas;
- rejeição de sequência vazia;
- rejeição de `float`, texto e booleano;
- modelo original não alterado;
- nenhuma regressão nos Itens 2.1 e 2.2.

## Observação

O modelo de resultados rejeita dezenas repetidas. O caso matemático de valores
iguais foi testado na função populacional genérica, que também poderá atender aos
intervalos históricos, nos quais valores repetidos são legítimos.

## Conclusão

Os critérios do Item 2.3 foram atendidos. Isso não autoriza implementar as
coordenadas e a média espacial do Item 2.4.
