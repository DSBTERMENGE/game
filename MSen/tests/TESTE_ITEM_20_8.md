# Teste da subetapa 20.8 — adaptadores estatísticos

Data: 30/10/2026

## Estado

**Concluída.** As quatro funções estatísticas reais foram executadas nas 200
amostras e as 800 comparações foram aprovadas.

## Implementação

O serviço `executar_criterios_numericos`:

- aceita somente categorias numéricas registradas;
- exige correspondência integral entre catálogo ativo e registro de produção;
- recusa assinatura de função divergente;
- recusa qualquer referência não conferida;
- chama a função real registrada para cada amostra ativa;
- grava somente estado e valor calculados, assinatura executada, diferença,
  aprovação e data de cálculo;
- marca o critério `APROVADO` somente quando todas as amostras coincidem;
- mantém o algoritmo geral desatualizado enquanto restarem outras categorias.

O comparador trata valor presente e ausência legítima, rejeita tipos não
numéricos e produz `S` ou `N` sem recalcular o esperado.

## Aplicação no banco local

Backup anterior à execução:

- arquivo:
  `MSen/dados/backups/games_pre_execucao_estatistica_20_8_20261030_043252.dump`;
- tamanho: 298.945 bytes;
- SHA-256: `41E9DDB9098805F5E868765EE32DD8B666D471B1A4EBAF4DB83E01367689A794`;
- catálogo: 167 itens.

Resultado:

| Critério | Avaliações | S | N | Estado |
|---|---:|---:|---:|---|
| `EST_SOMA` | 200 | 200 | 0 | `APROVADO` |
| `EST_MEDIA` | 200 | 200 | 0 | `APROVADO` |
| `EST_MEDIANA` | 200 | 200 | 0 | `APROVADO` |
| `EST_DESVIO_PADRAO` | 200 | 200 | 0 | `APROVADO` |
| **Total** | **800** | **800** | **0** | — |

As 800 assinaturas executadas correspondem às assinaturas atuais das funções.
O hash dos campos protegidos das referências foi
`8983C2BAB7252C7031F271A60323C41E9664CD3F5AB739BB57E9E5B375844228`
antes e depois da execução.

## Bloqueio geral

O estado geral permaneceu `Algoritmo de seleção de combinações desatualizado`,
com motivo `REFERENCIAS_OU_CALCULOS_PENDENTES`. Isso é esperado: os critérios
geométricos e de padrões ainda não foram executados.

## Regressão

Resultado: **545 testes Python aprovados**. Houve somente três
`ResourceWarning` preexistentes relativos a arquivos de frontend abertos por
testes; nenhuma falha.

## Resultado

A subetapa 20.8 está encerrada. A 20.9 poderá executar as seis funções
geométricas reais contra as 1.200 referências já protegidas, mediante
autorização separada.
