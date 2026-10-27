# Item 15.11 — padrões restantes acima da tolerância

Data: 2026-10-27

Foram avaliados em conjunto, com contadores separados, os quatro padrões ainda
não revisados: PD_001, PD_004, PD_007 e PD_008.

## Reconciliação histórica

| Código | Ocorrências | Percentual | Intervalo médio | Desvio-padrão | Reconciliado |
|---|---:|---:|---:|---:|---|
| PD_001 | 1.192 | 38,840013% | 2,575147 | 1,995592 | sim |
| PD_004 | 1.037 | 33,789508% | 2,960425 | 2,387099 | sim |
| PD_007 | 2.053 | 66,894754% | 1,495127 | 0,852399 | sim |
| PD_008 | 863 | 28,119909% | 3,554524 | 2,902303 | sim |

Todos os valores recalculados coincidiram exatamente com o PostgreSQL. A
consulta foi somente de leitura.

## Detecção bruta e decisão da política de 3%

| Código | Detectadas — semente 20261027 | Detectadas — semente 42 | Marcadas em cada amostra |
|---|---:|---:|---:|
| PD_001 | 1.937 | 1.963 | 0 |
| PD_004 | 1.708 | 1.721 | 0 |
| PD_007 | 3.305 | 3.393 | 0 |
| PD_008 | 1.431 | 1.361 | 0 |

Os detectores funcionaram, mas a política marcou zero porque todos os
percentuais históricos estão acima da tolerância de 3%.

## Fechamento dos padrões históricos

- Ativos na amostra protegida: PD_003, PD_002, PD_006 e PD_005.
- Avaliados e não ativos por estarem acima de 3%: PD_009, PD_001, PD_004,
  PD_007 e PD_008.
- Nenhuma regra além das quatro autorizadas foi inserida na configuração.
- Processamento integral continua bloqueado e o banco não foi escrito.

Resultado: os nove padrões históricos cadastrados concluíram o ciclo de
detecção, reconciliação e decisão sob a tolerância atual.
