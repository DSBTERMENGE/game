# Item 15.14 — comparação da ordem dos filtros

Data: 2026-10-27

## Condições

As três ordens usaram a mesma semente, as mesmas 5.000 combinações e os
mesmos oito filtros. Nenhum limite ou regra foi alterado. Uma combinação foi
contabilizada no primeiro filtro que a excluiu.

## Contagem determinística

| Ordem | Avaliações | Evitadas de 40.000 | Aprovadas |
|---|---:|---:|---:|
| Atual | 37.985 | 2.015 | 4.409 |
| Históricos frequentes primeiro | 37.569 | 2.431 | 4.409 |
| Geometria e estatísticas primeiro | 37.315 | 2.685 | 4.409 |

As três ordens preservaram exatamente o mesmo conjunto final de 4.409
combinações, não apenas a mesma quantidade. A atribuição das exclusões por
filtro mudou, como esperado, porque filtros posteriores não recebem itens já
excluídos.

## Tempo observado

Três execuções locais, em segundos:

| Ordem | 1 | 2 | 3 | Mediana |
|---|---:|---:|---:|---:|
| Atual | 0,591636 | 0,670447 | 0,856666 | 0,670447 |
| Históricos frequentes primeiro | 0,554994 | 0,701258 | 0,629925 | 0,629925 |
| Geometria e estatísticas primeiro | 0,638000 | 1,058685 | 0,597263 | 0,638000 |

Menos avaliações não garantiram automaticamente o menor tempo, pois as
funções possuem custos diferentes e o ambiente local variou. A ordem de
históricos frequentes apresentou a menor mediana neste ensaio, mas a ordem
padrão não foi trocada automaticamente.

## Validações

- Ordem incompleta ou com conjunto diferente é rejeitada.
- O modo integral continua bloqueado.
- Nenhum dado foi gravado no PostgreSQL.
- Passaram 372 testes automatizados.

Resultado: mecanismo de comparação pronto; qualquer troca da ordem padrão
depende de decisão posterior.
