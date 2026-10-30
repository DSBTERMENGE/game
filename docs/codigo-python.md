# Plano do código Python

## Objetivo

O código Python será responsável pela validação, regras de negócio, acesso ao
PostgreSQL, importação dos dados, análises e API. A interface HTML/JavaScript não
deverá conter regras essenciais nem acessar o banco diretamente.

## Estrutura planejada

```text
MSen/src/msen/
├── main.py
├── config.py
├── modelos/
│   └── resultado.py
├── calculos/
│   ├── estatisticas_linha.py
│   ├── coordenadas.py
│   ├── frequencias.py
│   └── resultado_calculado.py
├── database/
│   ├── connection.py
│   ├── migrations.py
│   └── repositories.py
├── importacao/
│   └── excel.py
├── analises/
│   ├── frequencia.py
│   └── historico.py
├── services/
└── api/
```

A estrutura será criada gradualmente. Não devem existir módulos vazios apenas
para imitar esta árvore.

## Responsabilidades

- `config`: ler e validar variáveis de ambiente;
- `modelos`: representar e validar os dados do domínio sem acessar banco,
  planilha ou interface;
- `calculos`: executar funções matemáticas puras sobre modelos já validados;
- `padroes`: contratos, registro e futuras funções puras de detecção e análise
  de padrões;
- `database`: conexões, transações, migrações e persistência;
- `importacao`: interpretar a planilha e transformar linhas em dados válidos;
- `analises`: cálculos puros, preferencialmente independentes da API;
- `services`: coordenar casos de uso;
- `api`: traduzir requisições HTTP e respostas, sem SQL;
- `main`: iniciar o modo de execução escolhido.

## Qualidade e testes

- testes unitários para validação e cálculos;
- testes de importação com arquivos pequenos controlados;
- testes de integração em banco de teste separado;
- nenhum teste deverá usar ou apagar o banco de produção;
- mensagens de erro deverão informar a operação, sem revelar senha ou string de
  conexão;
- conexões e cursores deverão sempre ser fechados corretamente.

## Decisões ainda pendentes

- estratégia de pool de conexões para a futura API;
- forma de autenticação, caso seja necessária;
- origem oficial e processo de atualização de novos resultados.

Essas escolhas devem ser registradas em `notas/decisoes.md` antes de orientar
grandes alterações no código.

## Leitura de Excel implementada

O módulo `importacao/excel.py` abre exclusivamente arquivos `.xlsx` em modo
somente leitura. Ele procura `Concurso`, `Data` e `bola 1` a `bola 6` em qualquer
linha da primeira aba, aceita mudanças de ordem, caixa e espaços nos nomes e
converte cada linha em `ResultadoEntrada`. Linhas totalmente vazias são
ignoradas; estrutura incompleta ou conteúdo inválido gera `ErroLeituraExcel`
com código, número da linha e campo, quando disponíveis.

`calculos/resultado_calculado.py` compõe as funções puras da Etapa 2 e devolve
todos os campos originais e derivados em um objeto imutável, identificado pela
`versao_calculo`. `importacao/processamento.py` conecta essa composição ao
leitor, sem acessar o banco de dados.

`importacao/comparacao.py` recebe os resultados existentes e classifica cada
linha lida como nova, igual, alterada ou inválida. A igualdade considera os
campos originais do concurso; diferenças em campos calculados ou na versão do
cálculo podem ser recalculadas futuramente sem serem confundidas com alteração
da fonte. Uma divergência preserva lado a lado os valores importado e existente.

## Persistência implementada

`database/migrations.py` controla versões, checksum, transações e concorrência.
`database/repositories.py` concentra todo o SQL da tabela `resultados`: inserção,
busca por concurso, atualização e listagem paginada. A atualização aceita um
`ResultadoEntrada`, executa novamente todas as funções matemáticas e somente
então envia os campos originais e derivados ao PostgreSQL.

`services/importacao_banco.py` coordena comparação, inserção das novidades,
recálculo integral das 60 frequências e geração do relatório. Todas as gravações
de uma importação pertencem à mesma transação; linhas iguais são ignoradas e
divergências não são sobrescritas.

## Infraestrutura de padrões

O pacote `padroes` associa cada `padrao_cod` a uma função detectora por meio de
`RegistroDetectores`. Códigos fora do formato `PD_001`, substituições silenciosas
e consultas a detectores ainda não implementados produzem erros diferentes e
explícitos. O registro começa vazio: os detectores iniciais somente serão
adicionados depois que suas regras forem aprovadas.

Todo elemento público exportado pelo pacote possui docstring em português. Os
testes também verificam essa documentação, além do registro, recuperação e
tratamento de funções pendentes.

Os detectores sequenciais classificam cada resultado exclusivamente pelo maior
bloco consecutivo: exatamente dois (`PD_001`), exatamente três (`PD_002`) ou
mais de três (`PD_003`). `padroes/estatisticas.py` aplica qualquer detector ao
histórico e calcula concursos correspondentes, intervalos, média e desvio-padrão
populacional. `padroes/iniciais.py` registra os três códigos sem manter estado
global mutável.

Os detectores de `padroes/mesma_coluna.py` usam a maior sequência vertical em
linhas imediatamente subjacentes: exatamente duas, exatamente três ou mais de
três dezenas. Estar na mesma coluna sem continuidade vertical não é suficiente.
Eles são funções públicas puras e testadas. `padroes/colunas.py` associa os
códigos `PD_004`–`PD_006` e calcula em memória as ocorrências, intervalos,
média e desvio-padrão dos três padrões.

`database/padroes_repository.py` preserva o cadastro e permite que somente um
objeto `EstatisticaPadrao` atualize os campos calculados. O serviço
`services/padroes.py` recalcula os nove códigos aprovados dentro de uma única
transação, sem recriar cadastros excluídos nem sobrescrever nome ou descrição
editados pelo usuário. Importação, inclusão e edição de resultados chamam esse
serviço na mesma transação que atualiza as frequências. O catálogo unificado em
`padroes/catalogo.py` também permite que a API identifique os nove detectores.

Os detectores puros de `padroes/mesma_linha.py` classificam pela maior ocupação
entre as seis linhas, sem exigir dezenas sequenciais: exatamente duas,
exatamente três ou mais de três. `padroes/linhas.py` associa `PD_007`–`PD_009`
e calcula suas estatísticas históricas. O serviço transacional inclui os nove
padrões aprovados no mesmo recálculo.

`api/padroes.py` expõe o CRUD HTTP. A API aceita do usuário somente
`padrao_nome` e `padrao_descr`; código, identificador e estatísticas são
protegidos no servidor. O retorno informa ainda `detector_implementado`, valor
calculado pelo registro Python e não armazenado como coluna.

## API Flask

A API usa Flask 3.1 com fábrica de aplicação em `api/app.py`. A fábrica não abre
conexão com o banco durante a importação do módulo, permitindo testes isolados e
carregamento seguro pelo WSGI. `MSen/wsgi.py` expõe a variável `application`
esperada pelo servidor de produção. `GET /api/saude` confirma somente que o
processo HTTP está respondendo; ele não consulta o PostgreSQL.

## Frequência histórica das dezenas

`services/configuracao_frequencia.py` valida e assina a configuração.
`services/frequencia_historica.py` mantém o motor acumulado sem conhecimento do
banco. `services/carga_historico_frequencia.py` coordena carga integral,
incremental, simulação, troca de geração, progresso e cancelamento transacional.

`api/frequencias.py` expõe estado, fotografias atuais, séries, prévia e tarefas
assíncronas. A série também cruza as fotografias com ocorrências reais obtidas
de `resultados` e calcula a assertividade sem modificar o histórico. O frontend
mantém em módulos separados os controles, gráficos atuais e escalas históricas.

# Geometria dos resultados

O pacote `msen.geometria` mantém separados caminho, regiões e medidas. A
topologia e as áreas trabalham com `fractions.Fraction`; extensão e perímetro
usam `Decimal`. O arredondamento para doze casas acontece apenas no
`RepositorioAnaliseGeometrica`, no momento de persistir.

O repositório grava uma única análise por resultado com operação idempotente.
O serviço `analise_geometrica.py` coordena o cálculo individual e o recálculo
do histórico. Inclusão, edição e importação chamam esse serviço dentro de suas
transações, mantendo resultado e medidas derivados consistentes.

## Validação, perfis e trava do Screener

`validacao/registro.py` é o registro único dos 19 critérios e calcula
assinaturas da implementação e da regra. `services/execucao_validacao.py`
resolve os cálculos exclusivamente por esse registro.

`services/sincronizacao_validacao.py`, `referencias_validacao.py`,
`motor_validacao.py` e `perfis_operacionais.py` cuidam, respectivamente, do
catálogo incremental, dos esperados independentes, da execução integrada e dos
dez perfis atuais. `services/homologacao_screener.py` bloqueia o Screener quando
estado, assinaturas, aprovações, perfis ou cobertura não reconciliam.

`api/validacao.py` expõe quadro, relatório e exportação;
`api/execucoes_validacao.py` gerencia a tarefa assíncrona e seu progresso.
