# Teste da subetapa 20.10 — adaptadores dos padrões

Data: 30/10/2026

## Estado

**Concluída.** Os nove detectores reais foram executados nas 200 amostras e as
1.800 comparações foram aprovadas.

## Implementação

O executor de padrões:

- exige correspondência integral entre catálogo ativo e registro de produção;
- valida a assinatura atual de cada detector;
- relaciona `PAD_PD_xxx` ao `PD_xxx` pertencente ao grupo do critério;
- recusa referência pendente ou incoerente;
- traduz retorno verdadeiro em `PADRAO_IDENTIFICADO` e no `id_padrao` correto;
- traduz retorno falso em `SEM_CORRESPONDENCIA` e identificador nulo;
- compara estado e identificador sem alterar o esperado;
- marca o critério `APROVADO` somente quando todas as amostras coincidem.

O comparador rejeita detectores que não retornem `bool`. Os testes cobriram
casos positivos, negativos, divergentes e ausência de correspondência.

## Aplicação no banco local

Backup imediatamente anterior à execução final:

- arquivo:
  `MSen/dados/backups/games_pre_execucao_padroes_20_10_20261030_043938.dump`;
- tamanho: 311.743 bytes;
- SHA-256: `7EACB1E1833B805C1C8889D768357DCF3A6740EA8DFC28B4410544BAA9B7F74E`;
- catálogo: 167 itens.

Resultado final:

| Critério | Avaliações | S | N | Estado |
|---|---:|---:|---:|---|
| `PAD_PD_001` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_002` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_003` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_004` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_005` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_006` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_007` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_008` | 200 | 200 | 0 | `APROVADO` |
| `PAD_PD_009` | 200 | 200 | 0 | `APROVADO` |
| **Total** | **1.800** | **1.800** | **0** | — |

As 1.800 assinaturas executadas correspondem às assinaturas atuais. O hash das
referências protegidas foi
`B19954D3BC47CE3F2C75B0F44B422F336358C4F22CC09CFFD7658316D2543A70`
antes e depois.

## Rastreabilidade

A primeira execução concluiu os cálculos, mas a consulta auxiliar de nomes do
relatório tentou usar a tabela histórica inexistente `padroes`. Ela foi
corrigida para dois `JOIN` com `padroes_subgrupo`, usando também `id_grupo`. A
execução integral foi repetida e confirmou os mesmos 1.800 resultados. Backup
da primeira execução: `games_pre_execucao_padroes_20_10_20261030_043925.dump`,
SHA-256 `C45A00B134146E2709B0443427216E1C152A6748CE8445A51B515BEDFA242552`.

## Bloqueio geral

Os 19 critérios atuais estão aprovados, mas o algoritmo permanece
desatualizado com motivo `REFERENCIAS_OU_CALCULOS_PENDENTES`. A 20.10 não libera
antecipadamente o Screener; a reconciliação e a decisão global pertencem às
subetapas seguintes.

## Regressão

Resultado: **549 testes Python aprovados**. Houve somente três
`ResourceWarning` preexistentes sobre arquivos de frontend; nenhuma falha.

## Resultado

A subetapa 20.10 está encerrada. A 20.11 poderá integrar sincronização,
recálculo e comparação em uma única operação, mediante autorização separada.
