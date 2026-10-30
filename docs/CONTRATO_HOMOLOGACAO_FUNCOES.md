# Contrato de homologação das funções

Data: 29/10/2026  
Subetapa: 20.0  
Estado: implementado pelas subetapas 20.1 a 20.16 e reconciliado na 20.17.

A homologação matemática das funções é independente da atualização dos perfis
operacionais. A chegada de novos resultados não invalida as 200 avaliações de
uma função cuja assinatura, regra e precisão não mudaram; ela exige recalcular
os perfis atuais usados na seleção.

## 1. Finalidade

Certificar que cada função estatística, geométrica ou classificadora de padrões
devolve o resultado correto em todas as amostras ativas antes de ser utilizada
pelo Screener.

O módulo compara dois resultados independentes:

- `esperado`: calculado pela IA ou pelo usuário e conferido sem usar a função
  que está sendo testada;
- `calculado`: produzido pela função real registrada no sistema.

A comparação gera `S` quando ambos coincidem e `N` quando divergem. Referência
pendente ou função ainda não executada mantém a avaliação pendente.

Na carga inicial, as referências geométricas foram calculadas com Shapely/GEOS
como oráculo independente de teste. Essa biblioteca não integra a execução de
produção nem o Screener e não substitui as funções reais que serão aferidas.

## 2. Conjunto de amostras

Nome aprovado: `amostras_validacao`.

Campos conceituais:

| Campo | Tipo proposto | Regra |
|---|---|---|
| `id_resultado` | `BIGINT` | PK e FK para `resultados(id_resultado)` |
| `ordem` | `SMALLINT` | positiva e única entre amostras ativas |
| `ativo` | `BOOLEAN` | `TRUE` por padrão |
| `incluido_em` | `TIMESTAMPTZ` | preenchimento automático |

Regras:

- a tabela não repete `res_01` a `res_06`;
- as dezenas são lidas por `INNER JOIN` com `resultados`;
- a FK usa `ON DELETE CASCADE`;
- a carga inicial relaciona os primeiros 200 registros por `numero_ap`;
- outras combinações poderão ser incluídas depois;
- a amostra é uma base de teste, não um arquivo histórico independente.

## 3. Catálogo dos critérios

Nome aprovado: `criterios_validacao`.

Campos conceituais:

| Campo | Tipo proposto | Regra |
|---|---|---|
| `id_criterio` | `BIGINT` | PK |
| `codigo` | `VARCHAR(80)` | estável e único |
| `nome` | `VARCHAR(200)` | nome legível para o usuário |
| `categoria` | `VARCHAR(20)` | `ESTATISTICA`, `GEOMETRIA` ou `PADRAO` |
| `funcao_python` | `VARCHAR(300)` | identificador registrado da função real |
| `tipo_resultado` | `VARCHAR(20)` | `INTEIRO`, `DECIMAL` ou `PADRAO` |
| `precisao_decimal` | `SMALLINT` | obrigatória somente para `DECIMAL` |
| `id_grupo` | `BIGINT` | FK opcional, obrigatória para `PADRAO` |
| `assinatura_funcao` | `CHAR(64)` | SHA-256 automático da implementação registrada |
| `assinatura_regra` | `CHAR(64)` | SHA-256 automático da definição matemática e semântica |
| `estado` | `VARCHAR(20)` | `PENDENTE`, `APROVADO` ou `REPROVADO` |
| `ativo` | `BOOLEAN` | estado cadastral |

O usuário não administrará números de versão manualmente. A assinatura deverá
mudar quando a implementação registrada ou uma dependência declarada da função
mudar. Falha ao produzir ou conferir a assinatura bloqueará o critério.

A assinatura da regra será independente da implementação. Mudança apenas da
implementação preservará a referência esperada; mudança de fórmula, precisão,
tipo, grupo ou significado invalidará também a referência. Categoria, tipo,
precisão ou grupo não poderão mudar silenciosamente sob o mesmo código estável.

Cadastro textual de grupo ou padrão sem função Python registrada não cria um
critério executável.

## 4. Avaliações por amostra e critério

Nome aprovado: `avaliacoes_validacao`.

Chave primária composta: `id_resultado, id_criterio`.

Campos conceituais:

| Campo | Tipo proposto | Regra |
|---|---|---|
| `id_resultado` | `BIGINT` | FK para `amostras_validacao`, cascata |
| `id_criterio` | `BIGINT` | FK para `criterios_validacao`, cascata |
| `referencia_conferida` | `BOOLEAN` | `FALSE` até revisão independente |
| `estado_valor_esperado` | `VARCHAR(30)` | `VALOR_IDENTIFICADO` ou `SEM_VALOR` |
| `valor_esperado` | `NUMERIC` | critérios `INTEIRO` ou `DECIMAL` |
| `estado_valor_calculado` | `VARCHAR(30)` | estado numérico devolvido pela função |
| `valor_calculado` | `NUMERIC` | critérios `INTEIRO` ou `DECIMAL` |
| `estado_padrao_esperado` | `VARCHAR(30)` | `PADRAO_IDENTIFICADO` ou `SEM_CORRESPONDENCIA` |
| `id_padrao_esperado` | `BIGINT` | FK opcional para `padroes_subgrupo` |
| `estado_padrao_calculado` | `VARCHAR(30)` | estado devolvido pelo classificador |
| `id_padrao_calculado` | `BIGINT` | FK opcional para `padroes_subgrupo` |
| `executado` | `BOOLEAN` | `FALSE` até a função real terminar |
| `assinatura_executada` | `CHAR(64)` | assinatura usada no cálculo |
| `aprovado` | `CHAR(1)` | `NULL`, `S` ou `N` |
| `diferenca` | `NUMERIC` | somente para valores numéricos |
| `calculado_em` | `TIMESTAMPTZ` | nulo enquanto pendente |
| `referencia_origem` | `VARCHAR(30)` | `HUMANO`, `IA` ou `TESTE_AUTOMATIZADO` |
| `referencia_revisor` | `VARCHAR(200)` | identificação obrigatória do conferente |
| `referencia_observacao` | `TEXT` | justificativa opcional |
| `referencia_conferida_em` | `TIMESTAMPTZ` | data da aprovação independente |

`NULL` em `aprovado` significa pendente. O estado explícito
`SEM_CORRESPONDENCIA` representa um resultado válido do classificador e não será
confundido com referência ausente.

Para valores numéricos, `SEM_VALOR` representa ausência matemática legítima,
como centro de gravidade inexistente quando não há área. Esse estado não será
confundido com referência ainda não produzida.

Para padrões:

- `id_grupo` vem do critério;
- `id_padrao_esperado` e `id_padrao_calculado`, quando preenchidos, devem
  pertencer ao mesmo grupo do critério;
- código e nome de grupo/subgrupo são obtidos por `JOIN`, sem repetição textual.

## 5. Regras de comparação

- `INTEIRO`: igualdade exata.
- `DECIMAL`: comparar depois de ajustar ambos à `precisao_decimal` aprovada,
  usando a mesma regra de arredondamento do contrato matemático.
- `PADRAO`: igualdade entre estado e, quando houver padrão identificado, entre
  os dois `id_padrao`.
- referência não conferida: `aprovado = NULL`;
- função não executada ou assinatura divergente da atual: `aprovado = NULL`;
- igualdade válida: `aprovado = 'S'`;
- diferença válida: `aprovado = 'N'`.

O frontend não realizará a comparação decisiva. O serviço Python calculará e
persistirá o estado dentro da mesma operação que grava o resultado calculado.

## 6. Sincronização incremental

### Nova amostra

- inserir a relação com `resultados`;
- criar uma avaliação pendente para cada critério ativo;
- não alterar avaliações das demais amostras.

### Novo critério

- inserir no catálogo como `PENDENTE`;
- criar uma avaliação pendente para cada amostra ativa;
- bloquear seu uso no Screener.

### Alteração somente da implementação

- manter os resultados esperados e sua conferência;
- atualizar a assinatura do critério;
- limpar calculados, assinatura executada, diferença, data e aprovação;
- bloquear o critério até nova execução integral.

### Alteração da regra matemática ou do significado

- executar as ações da alteração de implementação;
- marcar todas as referências do critério como não conferidas;
- limpar também os resultados esperados;
- exigir novo cálculo independente e nova conferência.

### Exclusão de critério ou amostra

- pedir confirmação para exclusão deliberada de critério;
- usar `ON DELETE CASCADE` para remover suas avaliações;
- não manter histórico de elemento deliberadamente excluído.

Toda sincronização será transacional e incremental. Ela não apagará e recriará o
conjunto completo.

## 7. Homologação e trava do Screener

Um critério somente terá estado `APROVADO` quando, para todas as amostras ativas:

1. a referência estiver conferida;
2. a função tiver sido executada com sua assinatura atual;
3. `aprovado = 'S'`.

Uma única pendência, assinatura antiga, falha de execução ou linha com `N` torna
o critério indisponível para o Screener. A consulta de homologação falhando ou
não retornando registro também bloqueia o critério; nunca haverá aprovação por
omissão.

O Screener verifica a homologação antes de construir seus adaptadores. A trava
vale para funções estatísticas, geométricas e classificadoras de padrões.

## 7.1 Estado global e perfis operacionais atuais

A interface apresentará somente um dos estados:

- `Algoritmo de seleção de combinações atualizado`;
- `Algoritmo de seleção de combinações desatualizado`.

O estado ficará desatualizado quando houver mudança de função, regra, precisão,
grupo, subgrupo ou configuração de seleção, ou quando novos resultados ainda
não tiverem sido incorporados aos perfis operacionais atuais.

Os perfis estatísticos, geométricos e de padrões usarão todos os resultados
válidos disponíveis no momento e substituirão o resumo operacional anterior.
Se as assinaturas das funções permanecerem iguais, a importação preservará as
avaliações de validação já aprovadas. Somente o backtest reconstruirá perfis com
corte por concurso ou data.

Os resumos numéricos atuais serão persistidos em
`perfis_operacionais_atuais`, identificados pelo código da grandeza e sem coluna
de versão histórica. Quantidade total, valores presentes/ausentes, média,
desvio-padrão, mínimo e máximo deverão corresponder ao mesmo conjunto cuja
quantidade e assinatura SHA-256 estiverem no estado global.

## 7.2 Cobertura obrigatória do Screener

O conjunto esperado de filtros conterá todos os filtros estatísticos e
geométricos aprovados e somente os filtros de padrões aprovados selecionados
pela consulta de incidência abaixo do limite configurado.

Antes da execução, o Screener exigirá igualdade exata entre esse conjunto e os
adaptadores carregados. Filtro ausente, extra, não homologado ou perfil baseado
em quantidade antiga de resultados bloqueará a API. A interrupção do funil após
uma combinação ser excluída não reduz o conjunto carregado: todos os filtros
esperados precisam integrar o plano de execução.

## 8. Relatório obrigatório

Resumo por função:

| Função | Categoria | Exigidas | Executadas | S | N | Pendentes | Estado |
|---|---|---:|---:|---:|---:|---:|---|
| Soma das dezenas | Estatística | 200 | 200 | 200 | 0 | 0 | APROVADO |
| Perímetro | Geometria | 200 | 200 | 199 | 1 | 0 | REPROVADO |

Detalhe numérico divergente:

| Combinação | Função | Esperado | Calculado | Aprovado |
|---|---|---:|---:|:---:|
| 04 09 10 13 39 52 | Perímetro | 27,849321 | 27,849319 | N |

Detalhe de padrão divergente:

| Combinação | Função | Grupo | Subgrupo esperado | Subgrupo calculado | Aprovado |
|---|---|---|---|---|:---:|
| 04 09 10 11 39 52 | Classificador sequencial | Dezenas sequenciais | Três sequenciais | Duas sequenciais | N |

Cada divergência exibirá combinação, função/filtro, grupo/subgrupos quando
aplicáveis, esperado, calculado, diferença e assinatura executada.

A IA poderá analisar a combinação, a regra e a função e apresentar uma hipótese
diagnóstica. Essa análise não altera automaticamente referência, código ou
aprovação.

## 9. Implementação vigente

As tabelas estão nas migrações 011 a 016. O motor, a API, a página, o
relatório, a exportação e a trava do Screener estão implementados. A descrição
operacional completa e o estado real do banco ficam em `docs/funcionamento.md`.
