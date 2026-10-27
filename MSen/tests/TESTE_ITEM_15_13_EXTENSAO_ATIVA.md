# Item 15.13 — extensão aberta ativa na amostra

Data: 2026-10-27

## Escopo autorizado

A faixa experimental de `8,650282` a `32,300058` foi conectada como oitavo
filtro somente ao ensaio protegido de 5.000 combinações. A comparação é
estrita: valores iguais aos limites são aceitos.

## Resultado do funil

| Estágio | Avaliadas | Excluídas | Saldo |
|---|---:|---:|---:|
| Extensão aberta | 4.484 | 75 | 4.409 |

No modo sombra, 106 das 5.000 combinações haviam sido marcadas. No funil,
31 delas já tinham sido excluídas pelos sete estágios anteriores. Cada
combinação continua contabilizada somente no primeiro filtro que a exclui.

Contabilidade integral da amostra:

`5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 44 + 75 + 4.409`

## Validações

- A política ativa reaproveita exatamente a medição validada no modo sombra.
- A ordem termina em `GEO_EXTENSAO_P01_P99`.
- Passaram 369 testes automatizados.
- O processamento integral permanece bloqueado.
- Nenhum dado foi gravado no PostgreSQL.

Resultado: oitavo filtro experimental ativado e contabilizado na amostra.
