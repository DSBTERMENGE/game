# Teste da subetapa 20.9 — adaptadores geométricos

Data: 30/10/2026

## Estado

**Concluída.** As seis funções geométricas reais foram executadas nas 200
amostras e as 1.200 comparações foram aprovadas na precisão declarada.

## Adaptação de entrada

As funções estatísticas recebem `ResultadoEntrada`; as funções geométricas
recebem a tupla das seis dezenas. O executor numérico passou a adaptar a entrada
conforme a categoria registrada, sem duplicar nenhum cálculo geométrico.

## Precisão da comparação

A primeira execução completa, usando igualdade irrestrita do `Decimal` bruto,
registrou 902 divergências microscópicas. A análise mostrou respostas como
`9.72087912087912`, produzida pelo oráculo Shapely em ponto flutuante, contra
`9.720879120879120879...`, produzida pela função exata com frações.

Essas diferenças estavam além das 12 casas declaradas no catálogo e não
representavam divergência matemática. O comparador foi corrigido para:

- preservar e armazenar o valor bruto retornado pela função real;
- arredondar esperado e calculado com `ROUND_HALF_UP` somente para decidir
  igualdade, usando `precisao_decimal` do critério;
- manter comparação exata quando o critério não declara casas decimais;
- continuar registrando `N` para qualquer diferença dentro da precisão
  contratada.

Depois dessa correção, nenhuma divergência permaneceu.

## Aplicação no banco local

Backup imediatamente anterior à execução final:

- arquivo:
  `MSen/dados/backups/games_pre_execucao_geometrica_20_9_20261030_043559.dump`;
- tamanho: 315.441 bytes;
- SHA-256: `5C807FEC715552124DB0683DB16A301FC54858609C0B576F44D55D91468EC8F7`;
- catálogo: 167 itens.

Resultado final:

| Critério | Avaliações | S | N | Estado |
|---|---:|---:|---:|---|
| `GEO_EXTENSAO` | 200 | 200 | 0 | `APROVADO` |
| `GEO_PERIMETRO` | 200 | 200 | 0 | `APROVADO` |
| `GEO_REGIOES` | 200 | 200 | 0 | `APROVADO` |
| `GEO_AREA` | 200 | 200 | 0 | `APROVADO` |
| `GEO_CENTRO_X` | 200 | 200 | 0 | `APROVADO` |
| `GEO_CENTRO_Y` | 200 | 200 | 0 | `APROVADO` |
| **Total** | **1.200** | **1.200** | **0** | — |

As 1.200 assinaturas executadas correspondem às assinaturas atuais. O hash das
referências protegidas foi
`9C5D2D23E917E1579D33F64B58FDD8E7B62AC25132A9BA1BE2CA9DE3E3F3544C`
antes e depois.

## Rastreabilidade das tentativas

- `043511`: execução abortada e revertida ao detectar a diferença de assinatura
  de entrada; backup SHA-256
  `A6AB6B2B46B69EC4DE3527F6D61E956DB6A4815E3B6C4684390175A2F06F842B`.
- `043534`: execução de diagnóstico com igualdade bruta, preservando 902 `N`;
  backup SHA-256
  `C20C18319F4434AD8C14F2CF2D78294C2114E88210EF717DD7F87824E8885EE0`.
- `043559`: execução final com a precisão contratada, 1.200 `S`.

## Bloqueio geral

O algoritmo permanece desatualizado com motivo
`REFERENCIAS_OU_CALCULOS_PENDENTES`, pois os nove critérios de padrões ainda
não foram executados.

## Regressão

Resultado: **547 testes Python aprovados**. Houve somente três
`ResourceWarning` preexistentes sobre arquivos de frontend; nenhuma falha.

## Resultado

A subetapa 20.9 está encerrada. A 20.10 poderá executar os nove detectores de
padrões contra as 1.800 referências protegidas, mediante autorização separada.
