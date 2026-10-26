# Teste de frequências e intervalos — Item 2.5

## Data e escopo

- Data: 2026-10-26.
- Python: 3.13.5.
- Código: `src/msen/calculos/frequencias.py`.
- Testes: `tests/test_frequencias.py`.
- Banco, Excel, API e interface: não acessados.

## Implementação testada

- ordenação por `numero_ap` crescente;
- conferência da coerência cronológica das datas;
- 60 resumos imutáveis, inclusive para dezenas sem ocorrência;
- lista de apresentações em que cada dezena ocorreu;
- intervalos pela diferença entre números de apresentação;
- primeira e última ocorrência;
- quantidade de ocorrências;
- média, mediana e desvio-padrão populacional dos intervalos;
- período opcional com limites inclusivos.

## Teste específico

```text
Ran 13 tests
OK
```

## Teste acumulado dos Itens 2.1 a 2.5

```text
Ran 53 tests
OK
```

## Casos conferidos

- histórico vazio retorna 60 dezenas zeradas;
- ocorrências da dezena 02 nas apresentações 35 e 50 geram intervalo 15;
- intervalos `[10, 15, 15]` geram média `13,333333`, mediana `15,000000`
  e desvio `2,357023`;
- intervalos `[10, 20]` geram média e mediana `15,000000` e desvio `5,000000`;
- uma ocorrência não inventa intervalo ou estatísticas;
- entrada fora de ordem é ordenada sem ser modificada;
- total de ocorrências é seis vezes a quantidade de resultados;
- período inicial e final é inclusivo;
- períodos inválidos são rejeitados;
- apresentações duplicadas são rejeitadas;
- divergência entre ordem de apresentação e data é rejeitada;
- objetos não validados são rejeitados;
- nenhuma regressão nos itens anteriores.

## Conclusão

Os critérios do Item 2.5 foram atendidos. Isso não autoriza iniciar a revisão
matemática integrada do Item 2.6.
