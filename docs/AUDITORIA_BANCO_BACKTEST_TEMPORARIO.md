# Auditoria do banco para o backtest temporário

Auditoria somente leitura realizada na Etapa 25.2 em 09/11/2026. Seu objetivo
foi identificar as fontes, consultas e índices necessários ao novo backtest,
sem criar ou remover estruturas.

## 1. Conclusão

O novo backtest não necessita de tabela, índice ou migração adicional.

As estruturas existentes fornecem todos os dados básicos necessários:

- `resultados`: concursos e seis dezenas sorteadas;
- `configuracoes_pesquisa_selecao`: configurações salvas e imutáveis;
- `geracoes_frequencia_dezenas`: identifica a geração ativa;
- `historico_frequencia_dezenas`: fotografias estatísticas por concurso e
  dezena.

As tabelas persistentes do backtest legado serão preservadas, mas o motor novo
não escreverá nelas.

## 2. Estado observado no banco `games`

| Informação | Valor |
|---|---:|
| Resultados | 3.069 |
| Primeiro resultado | 1 |
| Último resultado | 3.069 |
| Configurações disponíveis | 2 |
| Fotografias simples ativas | 154.200 |
| Concursos fotografados | 2.570 |
| Período fotografado | 500 a 3.069 |
| Concursos com fotografia diferente de 60 dezenas | 0 |
| Execuções legadas | 0 |
| Alvos legados | 0 |
| Avaliações individuais legadas | 0 |

As 154.200 fotografias são dados do módulo de frequências já existente:
`2.570 concursos × 60 dezenas`. Elas não foram criadas pelo backtest.

## 3. Índices suficientes

### Resultados

`uk_resultados_numero_ap` é um índice único B-tree sobre `numero_ap`. Ele
atende:

- busca de um concurso;
- leitura de intervalo;
- ordenação por concurso;
- obtenção do primeiro e do último concurso.

### Configurações

- chave primária por `id_configuracao_selecao`;
- índice por `estado, criada_em`;
- índice único por assinatura.

Esses índices atendem a busca da configuração salva e disponível.

### Fotografias de frequência

Os índices existentes por geração, concurso, dezena e tipo de evento atendem a
leitura das fotografias `SIMPLES` da geração ativa. A leitura completa medida
não justifica criar índice adicional neste momento.

## 4. Medições de leitura

Medições obtidas com `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` no banco local:

| Leitura | Linhas | Tempo observado |
|---|---:|---:|
| Todos os resultados até 3.069 | 3.069 | 0,446 ms |
| Resultados-alvo de 500 a 3.069 | 2.570 | 0,364 ms |
| Ocorrências das seis dezenas em todos os resultados | 18.414 | 12,954 ms |
| Fotografias dos cortes 500 a 3.068 | 154.140 | 121,598 ms |

Os tempos são evidência local, não garantia fixa para outros equipamentos.
Mesmo assim, mostram que o custo de leitura do banco é pequeno diante do
processamento completo.

## 5. Consultas contratadas para o motor

### 5.1. Configuração

Buscar por chave primária e exigir `estado = 'DISPONIVEL'`. O motor recebe o
identificador da configuração salva; não cria configuração implicitamente.

### 5.2. Validação do período

Consultar quantidade, primeiro e último `numero_ap`. O período solicitado deve
ser inclusivo, começar em 500 ou depois e terminar no último resultado ou
antes. A sequência histórica necessária não pode possuir lacunas.

### 5.3. Resultados-alvo

Carregar em uma consulta ordenada os concursos do período e suas seis dezenas.
Esses dados serão usados somente depois que a seleção correspondente tiver sido
calculada.

### 5.4. Fotografias estatísticas

Ler em fluxo as fotografias `SIMPLES` da geração ativa para os cortes entre
`concurso_inicial - 1` e `concurso_final - 1`, ordenadas por concurso e dezena.

O repositório deve entregar um grupo de 60 dezenas por corte. O motor processa
um grupo, produz o trio temporário do relatório e libera os detalhes antes de
avançar.

Não se deve materializar simultaneamente em objetos Python todo o conjunto de
154.140 fotografias quando uma iteração em fluxo for suficiente.

### 5.5. Corte anterior à primeira fotografia

No período padrão iniciado no concurso 500, o primeiro corte é 499, enquanto o
histórico persistido começa no concurso 500. Somente esse corte precisa ser
reconstruído a partir dos resultados 1 a 499, usando a lógica já existente.

Se qualquer fotografia intermediária estiver ausente ou incompleta, o motor
deve informar inconsistência da base. Ele não deve misturar silenciosamente
fontes diferentes dentro do mesmo relatório.

## 6. Estratégia de memória

O banco envia fotografias ordenadas, mas o motor mantém simultaneamente apenas:

- a configuração escolhida;
- as 60 estatísticas do corte em processamento;
- as seis dezenas do resultado-alvo;
- os trios já produzidos para os gráficos;
- os acumuladores do quadro-resumo.

Ao final de cada concurso, os detalhes das 60 dezenas são descartados.

## 7. Imutabilidade dos resultados

O esquema impede concursos duplicados, mas o repositório atual ainda contém
uma operação administrativa de atualização de resultado. Para o novo backtest,
a regra operacional permanece: resultados validados são imutáveis e novas
importações apenas acrescentam concursos.

Não será criada nesta etapa uma restrição que impeça correções administrativas.
Se essa proteção física for desejada, deverá ser planejada separadamente para
não comprometer recuperação de erro de cadastro.

## 8. Estrutura legada

Continuam preservadas:

- `execucoes_pesquisa_selecao`;
- `alvos_pesquisa_selecao`;
- `avaliacoes_dezenas_pesquisa`.

O banco real não possuía registros nessas três tabelas durante a auditoria. A
remoção continua fora do escopo e dependerá da validação completa do novo
processo e de autorização específica.

## 9. Evidência reproduzível

O script `MSen/tests/auditar_backtest_temporario.py` repete as consultas de
cardinalidade, índices, tamanhos e planos sem mostrar host, usuário ou senha e
sem alterar dados.

## 10. Critérios atendidos

- nenhuma escrita foi realizada;
- nenhuma tabela ou índice foi criado;
- fontes básicas identificadas;
- integridade das fotografias confirmada;
- índices existentes considerados suficientes;
- consultas de leitura contratadas;
- estratégia de fluxo definida;
- primeiro corte sem fotografia tratado explicitamente;
- legado mantido intacto.
