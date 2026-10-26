# Teste de coordenadas e média espacial — Item 2.4

## Data e escopo

- Data: 2026-10-26.
- Python: 3.13.5.
- Código: `src/msen/calculos/coordenadas.py`.
- Testes: `tests/test_coordenadas.py`.
- Banco, Excel, API e interface: não acessados.

## Implementação testada

- `calcular_coordenada`: converte uma dezena inteira em `(x, y)`;
- `calcular_media_espacial`: calcula médias independentes nos dois eixos;
- `MediaEspacial`: ponto decimal imutável;
- seis casas decimais e `ROUND_HALF_UP` no resultado final;
- nenhuma repetição permitida na linha de resultado.

## Fórmulas

```text
x = (n - 1) % 10
y = (n - 1) // 10

media_x = soma(x1 ... x6) / 6
media_y = soma(y1 ... y6) / 6
```

## Teste específico

```text
Ran 10 tests
OK
```

## Teste acumulado dos Itens 2.1 a 2.4

```text
Ran 40 tests
OK
```

## Casos conferidos

- `01 = (0; 0)`;
- `10 = (9; 0)`;
- `51 = (0; 5)`;
- `60 = (9; 5)`;
- início e fim de todas as seis linhas;
- rejeição de 0, 61, `float`, texto e booleano;
- média do exemplo da apresentação 3069: `(4,666667; 2,666667)`;
- exemplo estudado: `(2,000000; 4,333333)`;
- independência da ordem dos seis resultados;
- saída `Decimal` com seis casas;
- modelo de entrada preservado;
- nenhuma regressão nos itens anteriores.

## Repetições

Uma linha de resultado com valores repetidos continua impossível: ela é rejeitada
por `ResultadoEntrada` antes de chegar aos cálculos. Valores iguais aparecem
somente em testes da função estatística genérica para sequências derivadas, como
intervalos `[15, 15]`.

## Conclusão

Os critérios do Item 2.4 foram atendidos. Isso não autoriza implementar
frequências e intervalos do Item 2.5.
