# Auditoria da formação de jogos — etapa 26.1

Data da auditoria: 10/11/2026.

## 1. Conclusão executiva

O projeto já possui as peças centrais, mas o fluxo atual não deve ser usado
diretamente para o novo processo:

- o gerador das dezenas registradas já usa `itertools.combinations` e produz
  combinações de seis em ordem lexicográfica, de forma preguiçosa;
- o fluxo atual de jogos grava todas as combinações brutas, sem filtragem,
  classificação ou limite financeiro;
- o Screener oficial possui três famílias e contabilidade reconciliada, mas sua
  entrada está acoplada à amostra aleatória de 5.000 combinações;
- o motor extensível materializa toda a entrada e todas as aprovadas em memória;
- o Screener está atualmente bloqueado pelo estado de homologação global e esse
  bloqueio não pode ser contornado pela formação de jogos;
- não existe hoje uma pontuação de probabilidade para ordenar as aprovadas.

A integração é viável. Ela exige separar a preparação do plano/fotografia da
origem das combinações e criar uma execução em fluxo, cancelável, que mantenha
somente a contabilidade e as melhores combinações necessárias ao relatório.

## 2. Gerador e fluxo de jogos existentes

O serviço `combinacoes_selecao_dezenas.py` já oferece:

- normalização e validação das dezenas;
- cálculo de `C(N,6)` sem materialização;
- `itertools.combinations` para geração preguiçosa e determinística;
- exportação CSV;
- persistência em lotes de 2.000 linhas.

O comportamento que precisa ser substituído é `persistir_combinacoes_alvo`:
ele cria um lote novo a cada chamada e grava todas as combinações brutas antes
de qualquer Screener. Não há idempotência por configuração, classificação,
valor unitário, quantidade solicitada ou fotografia das regras.

As únicas chamadas operacionais são as duas rotas da página Seleção de dezenas:

- `GET /api/selecao-dezenas/alvos/{id}/jogos/previa`;
- `POST /api/selecao-dezenas/alvos/{id}/jogos`.

Além delas, existem testes e documentos. Nenhuma outra área consome os lotes ou
os jogos gravados atualmente.

## 3. Estrutura atual do banco

`lotes_jogos_selecao` registra apenas alvo, quantidade de dezenas, quantidade
total de combinações, estado e datas. `jogos_selecao_dezenas` guarda ordem e as
seis dezenas.

Faltam ao modelo atual:

- número solicitado e número disponibilizado;
- valor unitário, valor previsto e valor efetivo;
- totais examinado, reprovado e aprovado;
- fotografia/assinatura do Screener e versão do classificador;
- pontuação e posição classificada de cada jogo;
- chave idempotente da operação;
- estados adequados para análise, confirmação, cancelamento e falha.

No banco Games auditado existem:

- 1 registro de dezenas, para o concurso 3.070, contendo 16 dezenas;
- 0 lotes de jogos;
- 0 jogos gravados.

Assim, uma futura migração pode evoluir ou substituir as tabelas sem converter
dados de jogos existentes, mas as chaves estrangeiras e os consumidores de
código ainda deverão ser preservados até a substituição validada.

## 4. Screener existente

O serviço oficial prepara dados históricos, seleciona padrões raros, valida a
homologação, monta as famílias, cria uma fotografia assinada e só então executa
o funil.

Com o limite atual de raridade de 10%, o plano resultante possui:

- 3 filtros estatísticos: soma/média, mediana e desvio-padrão;
- 5 filtros geométricos: extensão, perímetro, área, regiões e centro de gravidade;
- 5 padrões raros elegíveis: PD_002, PD_003, PD_005, PD_006 e PD_009.

Os nove padrões cadastrados possuem perfil histórico. Há 19 critérios ativos e
os 19 constam como aprovados. Entretanto, `estado_algoritmo_selecao.atualizado`
está falso, com motivo `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`. Portanto, a
trava global impede corretamente a execução e deverá impedir também a formação
final de jogos até que o processo próprio de homologação a libere.

O motor extensível interrompe cada combinação no primeiro filtro que reprovar e
reconcilia `examinadas = reprovadas + aprovadas`. Porém, antes de processar ele
executa `tuple(combinacoes)` e ao final mantém outra coleção com as aprovadas.
Esse desenho é adequado à amostra de 5.000, mas não aos maiores conjuntos de
dezenas retornados pelo primeiro Screener.

## 5. Volumes observados

| Dezenas | Combinações C(N,6) |
|---:|---:|
| 6 | 1 |
| 16 — registro atual | 8.008 |
| 19 — mínimo observado no Backtest | 27.132 |
| 26 — exemplo já analisado | 230.230 |
| 38 — máximo observado no Backtest | 2.760.681 |
| 60 — universo integral | 50.063.860 |

A materialização isolada das 8.008 combinações atuais levou aproximadamente
0,008 segundo e atingiu pico aproximado de 784 KB na máquina de desenvolvimento.
Esse número não inclui o custo dos filtros, evidências, listas de aprovadas ou
gravação. A progressão combinatória impede extrapolar o modelo materializado
para 38 ou 60 dezenas.

## 6. Arquitetura recomendada

1. Separar do serviço oficial uma função que prepare e valide o plano completo,
   a fotografia e seu checksum, independentemente da origem das combinações.
2. Manter a rota experimental de 5.000 intacta enquanto a nova integração é
   construída e comparada.
3. Criar um executor em fluxo que receba o iterador produzido pelas dezenas
   registradas, sem convertê-lo em tupla.
4. Acumular somente contadores do funil e, depois da definição da classificação,
   um conjunto limitado das melhores aprovadas. Um heap limitado ao número
   solicitado é a alternativa inicial, desde que a pontuação possa ser calculada
   por combinação.
5. Reutilizar o padrão de gerenciador em segundo plano do Backtest para progresso,
   cancelamento e descarte seguro do resultado ainda não confirmado.
6. Não gravar combinações reprovadas. Não gravar combinações brutas. Persistir,
   após confirmação, a configuração, a fotografia, os totais e somente a lista
   final disponibilizada.
7. Manter a trava de homologação como pré-condição obrigatória.
8. Usar `C(N,6)` como total conhecido para progresso e reconciliação.

## 7. Classificação ainda inexistente

O Screener atual produz aprovação/reprovação, motivo e evidências. Ele não produz
probabilidade nem pontuação comparável entre aprovadas. A ordem lexicográfica do
gerador não representa probabilidade.

Antes da etapa 26.6 será necessário definir:

- quais medidas históricas podem compor a pontuação;
- sentido e peso de cada medida;
- normalização entre escalas diferentes;
- desempate determinístico;
- versão e fotografia da fórmula;
- validação histórica sem vazamento do resultado avaliado.

Nenhuma implementação deverá chamar essa pontuação de probabilidade garantida.

## 8. Limites e cancelamento propostos

- Não liberar a origem de 60 dezenas como consequência automática deste fluxo.
- Calcular e mostrar `C(N,6)` antes da execução.
- Executar em segundo plano com progresso por quantidade examinada.
- Verificar cancelamento entre combinações, antes de qualquer gravação final.
- Manter resultado transitório até a confirmação do usuário.
- Definir limites definitivos de tempo e volume somente depois de medir o funil
  real em 8.008, 27.132 e 230.230 combinações.
- Tratar 2.760.681 como ensaio de capacidade separado antes de autorizá-lo na
  interface normal.

## 9. Decisões para as próximas autorizações

1. Na etapa 26.2, a interface pode ser criada, mas o processamento deverá ficar
   bloqueado enquanto o algoritmo global estiver desatualizado.
2. Na etapa 26.3, recomenda-se evoluir o modelo para salvar somente jogos finais,
   fotografia e totais, em vez de reaproveitar semanticamente o lote bruto.
3. Na etapa 26.4, o motor precisa ser streaming e cancelável antes da integração.
4. Na etapa 26.5, a rota de amostra de 5.000 deve continuar disponível para
   comparação até a nova execução estar validada.
5. A etapa 26.6 exige uma decisão funcional específica sobre a classificação.

## 10. Resultado

A etapa 26.1 não modificou interface, rotas, regras, tabelas ou dados. Produziu
somente esta auditoria e um script de consultas e medição reproduzível.
