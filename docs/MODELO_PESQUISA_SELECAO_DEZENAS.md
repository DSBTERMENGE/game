# Modelo relacional — Pesquisas da Seleção de dezenas

Este documento nasceu na subetapa 23.3, foi reconciliado na 23.13 com as
migrações 021 e 022 e atualizado na Etapa 24 para a migração 023.

## 1. Objetivos do modelo

- preservar configurações diferentes para comparação;
- reproduzir cada pesquisa pela configuração e assinatura dos resultados;
- separar backtest da previsão do próximo concurso;
- registrar o que ocorreu em cada concurso-alvo;
- auditar aprovação, ranking e retorno de cada uma das 60 dezenas;
- não copiar as seis dezenas da tabela `resultados`;
- não permitir que a exclusão de uma pesquisa altere resultados ou histórico
  de frequência.

## 2. Relacionamentos

```text
configuracoes_pesquisa_selecao
    1 ─── N execucoes_pesquisa_selecao
                1 ─── N alvos_pesquisa_selecao
                            1 ─── 60 avaliacoes_dezenas_pesquisa

resultados
    1 ─── N alvos_pesquisa_selecao (referência opcional durante pendência)

alvos_pesquisa_selecao
    1 ─── N lotes_jogos_selecao
                1 ─── N jogos_selecao_dezenas
```

Uma execução possui vários concursos-alvo. Cada alvo concluído pelo motor deve
possuir exatamente 60 avaliações de dezenas, inclusive as não aprovadas. Isso
permite verificar o máximo aprovado, o ranking e os motivos de exclusão sem
recalcular a pesquisa.

## 3. `configuracoes_pesquisa_selecao`

Guarda configurações versionadas e reutilizáveis.

| Campo | Tipo lógico | Regra |
|---|---|---|
| `id_configuracao_selecao` | `BIGINT IDENTITY` | chave primária |
| `nome` | `VARCHAR(120)` | obrigatório e não vazio |
| `fator_k` | `NUMERIC(12,6)` | `0 < k <= 1` |
| `fator_j` | `NUMERIC(12,6)` | `-k <= j <= k` |
| `modo_quantidade` | `VARCHAR(10)` | `MAX` ou `FIXA` |
| `quantidade_dezenas` | `SMALLINT` | `NULL` em `MAX`; 6 a 60 em `FIXA` |
| `versao_calculo` | `INTEGER` | maior que zero |
| `versao_assinatura` | `SMALLINT` | `2` para configurações sem horizonte |
| `assinatura_sha256` | `CHAR(64)` | única, hexadecimal minúscula |
| `estado` | `VARCHAR(12)` | `DISPONIVEL` ou `ARQUIVADA` |
| `criada_em` | `TIMESTAMPTZ` | preenchimento automático |
| `arquivada_em` | `TIMESTAMPTZ` | obrigatório somente se arquivada |

A assinatura cobre todos os parâmetros matemáticos e operacionais. Uma
configuração usada por execução torna-se imutável. Alterar parâmetros cria
outra linha e outra assinatura; arquivar apenas impede novas execuções.

A migração 023 remove `horizonte_concursos`. Configurações legadas de assinatura
versão 1 são preservadas e arquivadas; configurações novas usam assinatura
versão 2 e não incluem horizonte.

Não haverá uma única configuração global obrigatória: várias configurações
podem permanecer disponíveis para pesquisa comparativa.

## 4. `execucoes_pesquisa_selecao`

Identifica uma execução reproduzível.

| Campo | Tipo lógico | Regra |
|---|---|---|
| `id_execucao_selecao` | `BIGINT IDENTITY` | chave primária |
| `id_configuracao_selecao` | `BIGINT` | FK para configuração, `RESTRICT` |
| `tipo_execucao` | `VARCHAR(20)` | `PREVISAO_FUTURA` |
| `configuracao_json` | `JSONB` | cópia imutável da configuração |
| `assinatura_configuracao` | `CHAR(64)` | igual à assinatura usada |
| `assinatura_resultados` | `CHAR(64)` | origem completa da pesquisa |
| `versao_calculo` | `INTEGER` | versão efetivamente executada |
| `concurso_corte_origem` | `INTEGER` | último resultado conhecido na origem |
| `concurso_alvo_inicial` | `INTEGER` | primeiro alvo da execução |
| `concurso_alvo_final` | `INTEGER` | último alvo da execução |
| `estado` | `VARCHAR(24)` | ciclo operacional da execução |
| `alvos_concluidos` | `INTEGER` | progresso não negativo |
| `total_alvos` | `INTEGER` | maior que zero |
| `erro_codigo` | `VARCHAR(80)` | somente em falha |
| `erro_mensagem` | `TEXT` | mensagem controlada |
| `criada_em` | `TIMESTAMPTZ` | criação |
| `iniciada_em` | `TIMESTAMPTZ` | início opcional |
| `concluida_em` | `TIMESTAMPTZ` | término opcional |

Estados previstos:

```text
PENDENTE
EXECUTANDO
CANCELAMENTO_SOLICITADO
CONCLUIDA
CANCELADA
FALHA
```

`configuracao_json` preserva a configuração mesmo que seu nome ou estado
administrativo mude. A combinação de tipo, assinaturas, versão e período deve
possuir restrição de unicidade para tornar a execução idempotente.
Instantâneos legados podem conter `horizonte_concursos`; os instantâneos atuais,
de assinatura versão 2, não contêm esse campo.

## 5. `alvos_pesquisa_selecao`

Guarda o resultado de cada concurso-alvo.

| Campo | Tipo lógico | Regra |
|---|---|---|
| `id_alvo_selecao` | `BIGINT IDENTITY` | chave primária |
| `id_execucao_selecao` | `BIGINT` | FK para execução, `CASCADE` |
| `numero_concurso_alvo` | `INTEGER` | positivo e único na execução |
| `numero_concurso_corte` | `INTEGER` | menor que o alvo |
| `id_resultado` | `BIGINT` | FK opcional para `resultados`, `RESTRICT` |
| `situacao` | `VARCHAR(20)` | `AVALIADO`, `PENDENTE` ou `NAO_AVALIAVEL` |
| `quantidade_configurada` | `SMALLINT` | `NULL` para `MAX`; 6 a 60 para `FIXA` |
| `quantidade_aprovada` | `SMALLINT` | 0 a 60 |
| `quantidade_retornada` | `SMALLINT` | 0 até a aprovada |
| `limite_nao_atingido` | `BOOLEAN` | verdadeiro quando `M < N` em `FIXA` |
| `quantidade_acertos` | `SMALLINT` | `NULL` ou 0 a 6 |
| `classe_acerto` | `SMALLINT` | igual à quantidade de acertos |
| `quantidade_combinacoes_brutas` | `BIGINT` | `C(R,6)` ou zero |
| `motivo` | `VARCHAR(160)` | estado ou aviso controlado |
| `selecionado_em` | `TIMESTAMPTZ` | congelamento da seleção |
| `conferido_em` | `TIMESTAMPTZ` | preenchido após resultado |

No backtest, o corte é `alvo - 1`. Na previsão do próximo concurso, a execução
possui um único alvo, igual a `corte + 1`. O par execução/alvo é único. O valor
interno `PREVISAO_FUTURA` permanece no banco por compatibilidade do modelo; na
interface ele é apresentado como previsão do concurso-alvo.

Coerência por situação:

- `AVALIADO`: exige `id_resultado`, 60 avaliações, acertos, classe e
  `conferido_em`;
- `PENDENTE`: não possui resultado, acertos, classe nem conferência;
- `NAO_AVALIAVEL`: não possui classe; exige motivo;
- `quantidade_retornada <= quantidade_aprovada <= 60`;
- em `MAX`, retornada é igual à aprovada;
- em `FIXA`, retornada é `min(aprovada, configurada)`.

As seis dezenas reais continuam somente em `resultados`. A pesquisa referencia
`id_resultado`; não cria colunas `res_01` a `res_06` duplicadas.

## 6. `avaliacoes_dezenas_pesquisa`

Registra as 60 avaliações de cada alvo.

| Campo | Tipo lógico | Regra |
|---|---|---|
| `id_alvo_selecao` | `BIGINT` | FK para alvo, `CASCADE` |
| `dezena` | `SMALLINT` | 1 a 60; parte da PK |
| `estado_avaliacao` | `VARCHAR(28)` | estado da dezena |
| `ultima_ocorrencia` | `INTEGER` | `NULL` somente sem base |
| `quantidade_intervalos` | `INTEGER` | não negativa |
| `media_intervalos` | `NUMERIC(18,6)` | unidade concurso |
| `desvio_padrao` | `NUMERIC(18,6)` | não negativo |
| `centro_original` | `NUMERIC(18,6)` | `U + média` |
| `centro_ajustado` | `NUMERIC(18,6)` | centro mais `j × desvio` |
| `limite_inferior_exato` | `NUMERIC(18,6)` | anterior ou igual ao superior |
| `limite_superior_exato` | `NUMERIC(18,6)` | posterior ou igual ao inferior |
| `limite_inferior` | `INTEGER` | limite operacional externo |
| `limite_superior` | `INTEGER` | limite operacional externo |
| `distancia_normalizada` | `NUMERIC(24,12)` | usada no ranking |
| `distancia_absoluta` | `NUMERIC(18,6)` | desempate |
| `posicao_ranking` | `SMALLINT` | 1 a 60 quando há base |
| `aprovada` | `BOOLEAN` | alvo dentro da faixa |
| `retornada` | `BOOLEAN` | pertence ao conjunto final |

Chave primária composta: `(id_alvo_selecao, dezena)`.

Estados previstos:

```text
SEM_BASE
FORA_FAIXA
APROVADA_RETORNADA
APROVADA_NAO_RETORNADA
```

`retornada` implica `aprovada`. A soma de `retornada` deve coincidir com
`quantidade_retornada`, e a soma de `aprovada`, com `quantidade_aprovada`. A
interseção com o resultado é obtida pela FK do alvo para `resultados`; não se
repete nas 60 avaliações quais dezenas foram sorteadas. A quantidade de acertos
será reconciliada transacionalmente com essa interseção e coberta por testes.

## 7. Índices

- configuração por assinatura única e por estado;
- execução por configuração/data e por estado;
- comparação por assinatura de resultados, versão e período;
- alvo único por execução/concurso e índice por situação;
- avaliações por alvo/retornada, alvo/aprovada e dezena/estado.

O volume esperado de 60 avaliações por alvo é deliberado. Por exemplo, 2.570
alvos produzem 154.200 avaliações por configuração, volume normal para
PostgreSQL e necessário à auditoria do ranking.

## 8. Exclusões e cascatas

- configuração com execução: `ON DELETE RESTRICT`;
- execução para alvos: `ON DELETE CASCADE`;
- alvo para avaliações: `ON DELETE CASCADE`;
- alvo para `resultados`: `ON DELETE RESTRICT` quando houver resultado;
- nenhuma FK da pesquisa pode apagar ou alterar `resultados`,
  `historico_frequencia_dezenas` ou `frequencia_de_resultado`.

Não haverá exclusão pela interface na primeira implementação. Se uma execução
for removida por manutenção autorizada, somente seus alvos e avaliações serão
removidos.

## 9. `lotes_jogos_selecao`

Registra uma materialização autorizada das combinações de um alvo.

| Campo | Tipo | Regra |
|---|---|---|
| `id_lote_jogos` | `BIGINT IDENTITY` | chave primária |
| `id_alvo_selecao` | `BIGINT` | FK para alvo, `CASCADE` |
| `quantidade_dezenas` | `SMALLINT` | 6 a 60 |
| `quantidade_combinacoes` | `BIGINT` | maior que zero |
| `estado` | `VARCHAR(16)` | `GERANDO`, `CONCLUIDO` ou `CANCELADO` |
| `criado_em` | `TIMESTAMPTZ` | automático |
| `concluido_em` | `TIMESTAMPTZ` | exigido no estado terminal |

Cada solicitação autorizada cria um lote próprio. Antes disso, a prévia calcula
`C(N,6)` sem inserir registros. Volumes elevados exigem confirmação adicional.

## 10. `jogos_selecao_dezenas`

Guarda somente jogos cuja materialização foi autorizada.

| Campo | Tipo | Regra |
|---|---|---|
| `id_lote_jogos` | `BIGINT` | FK para lote, parte da PK, `CASCADE` |
| `ordem` | `BIGINT` | positiva, parte da PK |
| `dezena_1` a `dezena_6` | `SMALLINT` | 1 a 60, estritamente crescentes |

A restrição única sobre lote e seis dezenas impede repetição. A ordem de geração
é lexicográfica e determinística. O vínculo do lote ao alvo conduz à execução,
configuração, concurso-alvo e eventual resultado real.

Esses jogos ainda não representam aprovação pelo segundo Screener. Eles são as
combinações brutas formadas pelas dezenas do primeiro Screener.

As tabelas 9 e 10 pertencem ao fluxo inicial e foram preservadas temporariamente
para não interromper consumidores existentes. A interface nova não cria mais
esses lotes. Sua retirada somente ocorrerá depois da validação integral do novo
processo.

## 11. `formacoes_jogos_selecao`

Registra a configuração imutável e a contabilidade de uma formação final:

- alvo e quantidade de dezenas de origem;
- quantidade bruta `C(N,6)` e número máximo solicitado;
- valor unitário, valor máximo previsto e valor efetivo;
- fotografia e assinatura do Screener;
- versão e assinatura do classificador;
- chave SHA-256 de idempotência;
- totais examinado, reprovado, aprovado e disponibilizado;
- estado, datas e eventual erro operacional.

Os valores calculados usam `NUMERIC(24,2)`. A configuração não pode ser alterada
depois da criação. Os totais obedecem a
`examinadas = reprovadas + aprovadas`, e a quantidade disponibilizada nunca
supera a aprovada nem a solicitada. Nenhuma combinação bruta ou reprovada é
armazenada nessa tabela.

## 12. `jogos_finais_selecao`

Guarda somente a lista final autorizada. Cada linha contém posição classificada,
seis dezenas crescentes, pontuação e evidências da classificação. Uma combinação
não pode se repetir dentro da formação e um jogo final não pode ser alterado.

As tabelas 11 e 12 foram criadas pelas migrações 026 e 027. Ainda não recebem
dados porque geração, Screener, classificação e confirmação pertencem às etapas
seguintes.

## 13. Implementação vigente

- migração 021: configurações, execuções, alvos e avaliações;
- migração 022: lotes e jogos autorizados;
- migração 023: remoção do horizonte e assinatura de configuração versão 2;
- migração 026: configuração imutável e jogos finais;
- migração 027: capacidade monetária das colunas calculadas;
- repositório: `msen.database.pesquisa_selecao_repository`;
- serviços: seleção, backtest, previsão e combinações;
- API: `/api/selecao-dezenas`;
- página: `/selecao-dezenas.html`.
