# Evidência do Item 15.7 — política PD_003 em modo sombra

Data: 2026-10-27.

Foi criada uma política genérica de baixa ocorrência em modo sombra e conectada
ao detector reconciliado de PD_003 por meio do adaptador de padrões históricos.

## Comportamento observado

| Combinação/situação | Detector | Percentual | Hipótese | Marca sombra | Aprova no funil |
|---|---:|---:|---:|---:|---:|
| 01, 02, 03, 04, 20, 40 | Sim | 0,162920% | 3% | Sim | Sim |
| 01, 02, 03, 20, 21, 22 | Não | 0,162920% | 3% | Não | Sim |
| PD_003 presente | Sim | 0,162920% | 0,1% | Não | Sim |
| Evidência não reconciliada | Não avaliado | — | 3% | Não | Sim |

O teste de fronteira confirmou a semântica inclusiva: 3% histórico com
tolerância de 3% seria marcado.

Cada decisão informa código, modo, detector, ocorrências, total, percentual,
operador, tolerância, identificação da reconciliação, marca e motivo. Mesmo
quando `marcaria_exclusao` é verdadeiro, `aprovada` permanece verdadeiro.

## Segurança

- A configuração padrão continua com todos os critérios desabilitados.
- 3% permanece hipótese experimental, não tolerância aprovada.
- O funil de teste recebeu 2, aprovou 2 e excluiu 0.
- Nenhum dado foi gravado no banco.

## Testes

- 6 testes específicos aprovados.
- Regressão Python completa: 305 testes aprovados.
