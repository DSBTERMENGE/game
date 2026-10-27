# Plano de etapas, subetapas, autorizações e testes

## Finalidade

Este é o plano operacional para transformar as funcionalidades idealizadas em
um sistema verificável. Ele não autoriza automaticamente nenhuma implementação.

## Regra obrigatória de execução

1. Trabalhar em somente um item autorizado por vez.
2. Antes de iniciar, informar objetivo, arquivos previstos e teste de aceitação.
3. Não iniciar subetapa seguinte por conveniência técnica.
4. Ao concluir, informar alterações, testes, resultados e limitações.
5. Pedir autorização explícita para o item seguinte e aguardar a resposta.
6. Falha em teste encerra o item: corrigir apenas o escopo autorizado e testar
   novamente; não avançar com defeitos conhecidos.
7. Banco remoto, PythonAnywhere, Git commit e publicação exigem autorização
   específica, mesmo quando aparecerem como etapa futura.
8. Concluir e testar todo o sistema no ambiente local antes de preparar qualquer
   alteração no PythonAnywhere.
8. Concluir e testar todo o sistema no ambiente local antes de preparar qualquer
   alteração no PythonAnywhere.

## Estratégia para evitar retrabalho

- implementar em partes pequenas e testáveis;
- começar pelas regras matemáticas puras, sem interface ou banco;
- usar arquivos de teste pequenos antes da planilha real;
- testar DDL em banco isolado antes de qualquer banco com dados;
- integrar uma camada por vez: matemática, Excel, banco, API e interface;
- conservar a fonte original e usar transações nas gravações;
- registrar cada decisão e atualizar `CONTINUIDADE_IA.md` ao final de cada item;
- somente marcar item concluído quando seu teste de aceitação passar.
- manter o PythonAnywhere intocado até a conclusão e aprovação dos testes locais.
- manter o PythonAnywhere intocado até a conclusão e aprovação dos testes locais.

---

## ETAPA 0 — Organização e planejamento

### Item 0.1 — Separar a fonte de dados

Objetivo:

- criar `MSen/dados/fontes`;
- mover a planilha original para essa pasta;
- documentar que a aplicação não pode alterá-la.

Teste de aceitação:

- arquivo existe no novo caminho com mesmo tamanho e hash do original;
- caminho antigo não contém outra cópia por engano;
- documentação aponta para o novo local.

Estado: concluído em 2026-10-26. Integridade confirmada por tamanho e SHA-256.

### Item 0.2 — Criar o plano de execução e testes

Objetivo:

- registrar etapas, subetapas, dependências, autorizações e testes.

Teste de aceitação:

- todas as camadas idealizadas aparecem no plano;
- cada etapa de implementação contém validação antes do avanço.

Estado: concluído em 2026-10-26.

---

## ETAPA 1 — Fechar requisitos e modelo dos dados

### Item 1.1 — Dicionário de dados da tabela `resultados`

Definir nome, finalidade, tipo, nulidade, origem e regra de cada campo:

- `id_resultado`;
- `data_resultado`;
- `numero_ap`;
- `res_01` a `res_06`;
- `soma_res`;
- `media_aritmetica_res`;
- `mediana_res`;
- `desvio_padrao_media`;
- `media_coordenada_x`;
- `media_coordenada_y`;
- eventuais campos técnicos de auditoria.

Decisões obrigatórias:

- significado exato de `numero_ap`;
- tipos e precisão dos valores e cálculos;
- desvio-padrão populacional ou amostral;
- número de casas decimais armazenadas e exibidas.

Teste de aceitação:

- todos os campos possuem definição inequívoca e exemplo;
- nenhuma fórmula ou tipo permanece implícito.

Estado: concluído e aprovado em 2026-10-26. As cinco decisões estão registradas
em `docs/DICIONARIO_DADOS_RESULTADOS.md`.

### Item 1.2 — Contrato dos resultados e cálculos

Definir entradas, saídas, erros e arredondamentos das funções matemáticas.

Teste de aceitação:

- exemplos calculados manualmente possuem resultados esperados registrados;
- casos-limite estão definidos antes do código.

Estado: concluído e aprovado em 2026-10-26. As decisões estão registradas em
`docs/CONTRATO_RESULTADOS_E_CALCULOS.md`.

### Item 1.3 — Revisar o modelo PostgreSQL

Atualizar o desenho da tabela, restrições, índices e controle de migrações.

Teste de aceitação:

- revisão documental confirma correspondência com os itens 1.1 e 1.2;
- nenhuma execução em banco ocorre neste item.

Estado: concluído e aprovado em 2026-10-26. O modelo com `resultados`,
`frequencia_de_resultado` e `schema_migrations` está registrado em
`docs/MODELO_POSTGRESQL.md`.

### Item 1.4 — Revisar o DDL e a migração 001

Alterar os arquivos SQL ainda não executados para refletirem o modelo aprovado.

Testes de aceitação:

- esquema completo e migração têm definições equivalentes;
- SQL passa por validação sintática em PostgreSQL compatível;
- primeira execução cria os objetos;
- segunda execução controlada não destrói nem duplica objetos;
- transação reverte integralmente um erro provocado em banco de teste.

Estado: concluído em 2026-10-26. DDL e migração equivalentes foram testados em
cluster PostgreSQL 16.11 temporário e removido após os testes. Evidências em
`database/TESTE_DDL_ITEM_1_4.md`.

Estado: concluído em 2026-10-26. DDL e migração equivalentes foram testados em
cluster PostgreSQL 16.11 temporário e removido após os testes. Evidências em
`database/TESTE_DDL_ITEM_1_4.md`.

---

## ETAPA 2 — Funções matemáticas puras

### Item 2.1 — Modelo Python de entrada e validação

Criar representação de uma linha e validar data, número da apresentação, seis
inteiros de 01 a 60 e ausência de repetição.

Testes unitários:

- linha válida;
- campos ausentes;
- limites 01 e 60;
- valores 00 e 61;
- resultado repetido;
- tipos inválidos.

Estado: concluído em 2026-10-26. Modelo separado em `MSen/src/msen/modelos` e
15 testes aprovados com `unittest`. Evidências em
`MSen/tests/TESTE_ITEM_2_1.md`.

### Item 2.2 — Soma, média aritmética e mediana

Implementar funções puras, sem banco e sem interface.

Testes unitários:

- exemplos manuais;
- resultado ordenado e fora de ordem;
- precisão e arredondamento conforme contrato.

Estado: concluído em 2026-10-26. Seis testes específicos e 21 testes acumulados
foram aprovados. Evidências em `MSen/tests/TESTE_ITEM_2_2.md`.

### Item 2.3 — Desvio-padrão

Implementar somente depois de aprovada a fórmula do item 1.2.

Testes unitários:

- exemplo manual conhecido;
- função estatística genérica com valores iguais, aplicável a intervalos; uma
  linha de resultado continua proibindo repetições;
- verificação da precisão decimal;
- comparação com biblioteca de referência apenas no teste.

Estado: concluído em 2026-10-26. Nove testes específicos e 30 testes acumulados
foram aprovados. Evidências em `MSen/tests/TESTE_ITEM_2_3.md`.

### Item 2.4 — Coordenadas e média espacial

Implementar:

- `x = (n - 1) % 10`;
- `y = (n - 1) // 10`;
- média independente dos seis valores X e Y.

Testes unitários:

- `01 = (0; 0)`;
- `10 = (9; 0)`;
- `51 = (0; 5)`;
- `60 = (9; 5)`;
- caso com média espacial decimal.

Estado: concluído em 2026-10-26. Dez testes específicos e 40 testes acumulados
foram aprovados. Evidências em `MSen/tests/TESTE_ITEM_2_4.md`.

### Item 2.5 — Frequências e intervalos

Implementar frequência de 01 a 60, intervalos, intervalo médio e desvio-padrão
dos intervalos.

Testes unitários:

- número nunca ocorrido;
- uma única ocorrência;
- ocorrências consecutivas;
- intervalos regulares e irregulares;
- período filtrado.

Estado: concluído em 2026-10-26. Treze testes específicos e 53 testes acumulados
foram aprovados. Evidências em `MSen/tests/TESTE_ITEM_2_5.md`.

### Item 2.6 — Revisão matemática integrada

Executar toda a suíte matemática e conferir exemplos manuais.

Critério para avançar:

- 100% dos testes dos itens 2.1 a 2.5 aprovados;
- nenhuma fórmula pendente ou silenciosamente presumida.

Estado: concluído em 2026-10-26. Quatro testes integrados, 57 testes acumulados,
comparação independente e compilação em memória foram aprovados. Evidências em
`MSen/tests/TESTE_ITEM_2_6.md`.

---

## ETAPA 3 — Leitura e comparação do Excel

### Item 3.1 — Dependência e arquivos de teste

Escolher a biblioteca de leitura e criar planilhas pequenas controladas:

- válida;
- cabeçalho ausente;
- linha inválida;
- linhas repetidas;
- linha existente alterada.

Teste de aceitação:

- dependência registrada no projeto;
- testes nunca modificam a fonte original.

Estado: concluído em 2026-10-26. `openpyxl` e `defusedxml` foram registrados;
seis planilhas controladas foram criadas e abertas em modo somente leitura. A
fonte original preservou seu SHA-256. Evidências em
`MSen/tests/TESTE_ITEM_3_1.md`.

### Item 3.2 — Localização do cabeçalho e leitura

Localizar `Concurso`, `Data` e `bola 1` a `bola 6`, sem depender apenas da linha
7, e produzir registros normalizados.

Testes:

- arquivo atual com cabeçalho na linha 7;
- cabeçalho deslocado em arquivo controlado;
- coluna ausente ou renomeada;
- células vazias e datas inválidas.

Estado: concluído em 2026-10-26. O cabeçalho é localizado dinamicamente, as
linhas são lidas em modo somente leitura e convertidas em `ResultadoEntrada`.
Sete testes específicos e 64 testes acumulados foram aprovados. Evidências em
`MSen/tests/TESTE_ITEM_3_2.md`.

### Item 3.3 — Cálculo de cada linha importada

Passar cada registro pelas mesmas validações e funções da Etapa 2.

Teste de aceitação:

- saída de uma linha importada é igual à saída da inclusão manual equivalente.

Estado: concluído em 2026-10-26. A composição produz um `ResultadoCalculado`
imutável com campos originais, estatísticas, coordenadas e versão do cálculo.
Seis testes específicos e 70 testes acumulados foram aprovados. Evidências em
`MSen/tests/TESTE_ITEM_3_3.md`.

### Item 3.4 — Comparação incremental

Classificar linhas como novas, iguais, alteradas ou inválidas.

Testes:

- reimportar o mesmo arquivo não cria novidades;
- arquivo atualizado retorna somente acréscimos;
- divergências antigas não são sobrescritas silenciosamente.

Estado: concluído em 2026-10-26. Cada linha é classificada como `NOVA`, `IGUAL`,
`ALTERADA` ou `INVALIDA`; concursos duplicados na planilha são inválidos e as
duas versões de uma divergência são preservadas em memória. Oito testes
específicos e 78 testes acumulados foram aprovados. Evidências em
`MSen/tests/TESTE_ITEM_3_4.md`.

### Item 3.5 — Teste somente leitura da planilha real

Ler as mais de 3.000 linhas sem gravar no banco.

Teste de aceitação:

- quantidade, primeiro e último concurso conferidos;
- relatório de linhas válidas e inválidas;
- hash do arquivo permanece idêntico.

Estado: concluído em 2026-10-26. A fonte real contém 3.069 linhas válidas e
nenhuma inválida, cobrindo concursos únicos de 1 a 3069. Primeiro, último,
tamanho e SHA-256 foram conferidos. Cinco testes específicos e 83 testes
acumulados foram aprovados. Evidências em `MSen/tests/TESTE_ITEM_3_5.md`.

Estado da Etapa 3: concluída.

---

## ETAPA 4 — Persistência PostgreSQL

### Item 4.1 — Configuração e conexão local

Configurar variáveis de ambiente sem senhas versionadas.

Testes:

- conexão válida;
- senha ausente;
- banco inexistente;
- mensagem sem exposição de credenciais.

Estado: concluído em 2026-10-26. A configuração `GAME_DB_*`, o driver Psycopg 3
e a verificação segura de conexão foram implementados. Nove testes específicos,
92 testes acumulados e dois cenários reais em PostgreSQL 16.11 temporário foram
aprovados. Evidências em `MSen/tests/TESTE_ITEM_4_1.md`.

### Item 4.2 — Controle de migrações

Criar `schema_migrations`, ordenação, transação e trava contra execução dupla.

Testes:

- banco vazio;
- banco atualizado;
- migração com erro e rollback;
- duas tentativas concorrentes.

Estado: concluído em 2026-10-26. O executor ordena arquivos, valida SHA-256,
controla cada migração e seu registro na mesma transação e serializa execuções
com trava consultiva PostgreSQL. Oito testes específicos, 100 acumulados e os
quatro cenários reais em PostgreSQL 16.11 temporário foram aprovados. Evidências
em `MSen/tests/TESTE_ITEM_4_2.md`.

### Item 4.3 — Repositório de resultados

Implementar busca, inserção, atualização e listagem sem SQL na interface.

Testes de integração em banco exclusivo de teste:

- inserir e ler;
- impedir duplicidade;
- rollback em erro;
- edição recalcula todos os derivados;
- nenhum teste toca banco de produção.

Estado: concluído em 2026-10-26. O repositório oferece inserção, busca,
atualização com recálculo e listagem paginada. Duplicidades e ausências geram
erros identificáveis, e as operações respeitam transações externas. Seis testes
específicos, 106 acumulados e os cenários reais em PostgreSQL 16.11 temporário
foram aprovados. Evidências em `MSen/tests/TESTE_ITEM_4_3.md`.

### Item 4.4 — Importação inicial controlada

Importar a planilha real no banco local somente após backup e confirmação.

Testes de aceitação:

- contagens antes e depois;
- amostragem de cálculos;
- reimportação resulta em zero duplicações;
- relatório preservado.

Estado: concluído em 2026-10-26. O database persistente e exclusivo `games` foi
criado em PostgreSQL 16.11, recebeu a migração `001`, 3.069 resultados e 60
frequências. A reimportação inseriu zero registros. Como o database não existia,
não havia conteúdo anterior para backup; após a importação foi criado e validado
um backup inicial. Três testes específicos e 109 acumulados foram aprovados.
Evidências em `MSen/tests/TESTE_ITEM_4_4.md`.

Estado da Etapa 4: concluída.

---

## ETAPA 5 — API Python

### Item 5.1 — Escolher e configurar o framework

Escolher a tecnologia da API e registrar a decisão antes de adicionar código.

Estado: concluído em 2026-10-26. Flask 3.1.3 foi escolhido e configurado com
fábrica de aplicação, endpoint técnico de saúde e entrada WSGI sem inicialização
automática do servidor. Sete testes específicos e 116 testes acumulados foram
aprovados. Evidências em `MSen/tests/TESTE_ITEM_5_1.md`.

### Item 5.2 — `GET /api/resultados`

Listar resultados em ordem definida e no contrato esperado pelo frontend.

Testes de API:

- lista vazia;
- lista válida;
- ordenação;
- erro do banco sem vazamento de credenciais.

Estado: concluído em 2026-10-26. A rota devolve todos os resultados em ordem de
`numero_ap` crescente, com datas ISO e decimais sem perda de precisão. Seis
testes específicos e 121 testes acumulados foram aprovados. A integração local
real retornou 3.069 resultados sem alterar o banco. Evidências em
`MSen/tests/TESTE_ITEM_5_2.md`.

### Item 5.3 — `POST /api/resultados/importar`

Receber Excel, validar, calcular, comparar e armazenar com relatório.

Testes de API:

- arquivo válido;
- extensão incorreta;
- arquivo corrompido;
- atualização incremental;
- limite de tamanho;
- rollback em falha.

Estado: concluído em 2026-10-26. A rota recebe o campo multipart `arquivo`,
aceita somente `.xlsx`, limita uploads a 10 MiB, remove o arquivo temporário e
devolve o relatório incremental em JSON. Sete testes específicos e 128 testes
acumulados passaram. A homologação local reimportou os 3.069 concursos sem
duplicar registros, e uma falha controlada após a inserção confirmou rollback
integral. Evidências em `MSen/tests/TESTE_ITEM_5_3.md`.

### Item 5.4 — Inclusão e edição individual

Criar rotas somente quando o formulário for implementado.

Testes:

- inclusão válida;
- edição válida;
- todos os cálculos refeitos ao salvar;
- conflito de atualização e entrada inválida.

Estado: concluído em 2026-10-26. `POST /api/resultados` inclui e
`PUT /api/resultados/<numero_ap>` edita um resultado. As duas rotas reutilizam o
modelo validado, recalculam todos os campos derivados e atualizam as 60
frequências na mesma transação. Nove testes específicos e 137 testes acumulados
passaram. A homologação PostgreSQL incluiu e editou temporariamente o concurso
3070, confirmou os recálculos e reverteu integralmente resultado e frequências.
Evidências em `MSen/tests/TESTE_ITEM_5_4.md`.

---

## ETAPA 6 — Interface e desenhos

### Item 6.1 — Testar painel e navegação existentes

Validar seleção, anterior, próximo, mensagens e estados dos botões.

Testes:

- nenhum resultado;
- um resultado;
- primeiro e último resultados;
- navegação circular ou limite conforme decisão aprovada.

Estado: concluído em 2026-10-26. A navegação foi definida como circular para
dois ou mais resultados. Com um resultado, Anterior, Próximo e Voo ficam
desabilitados; com zero, todos os controles dependentes de dados ficam
desabilitados. Cinco testes Node.js validam HTML, mensagens, seleção direta,
primeiro, último e estados dos botões. Os 137 testes Python continuaram
aprovados. Evidências em `MSen/tests/TESTE_ITEM_6_1.md`.

### Item 6.2 — Resultado individual e média espacial

Validar círculos, legibilidade e posição decimal da média.

Testes visuais e geométricos:

- marcas em 01, 10, 51 e 60;
- média em centro inteiro;
- média em ponto decimal conhecido;
- redimensionamento da janela.

Estado: concluído em 2026-10-26. Cinco testes geométricos adicionais, dez de
frontend acumulados, confirmaram seis marcas por resultado, centros de 01, 10,
51 e 60, média inteira, ponto decimal `(2; 4,33)`, legibilidade e recálculo de
posições após redimensionamento. Os 137 testes Python permaneceram aprovados.
Evidências em `MSen/tests/TESTE_ITEM_6_2.md`.

### Item 6.3 — Voo dos pássaros

Validar iniciar, pausar, reiniciar e alterar intervalo de 0,1 a 30 segundos.

Testes com relógio controlado:

- intervalo padrão de 0,5 segundo;
- troca ordenada;
- pausa sem temporizador órfão;
- alteração de tempo;
- redimensionamento durante o voo.

Estado: concluído em 2026-10-26. Cinco testes com relógio controlado, quinze de
frontend acumulados, confirmaram intervalo padrão de 0,5 segundo, ordem,
navegação circular, pausa sem temporizador órfão, mudança de tempo, rejeição
fora de 0,1 a 30 segundos e redimensionamento durante o voo. Evidências em
`MSen/tests/TESTE_ITEM_6_3.md`.

### Item 6.4 — Mancha de resultados e médias

Validar pequenos círculos, acúmulo e desempenho.

Testes:

- conjunto pequeno com posições previsíveis;
- mais marcas do que a capacidade visual de uma célula;
- aproximadamente 3.000 resultados;
- tempo de desenho e consumo de memória aceitáveis;
- limpeza completa da camada.

Estado: concluído em 2026-10-26. Quatro testes específicos, dezenove de
frontend acumulados, confirmaram posições previsíveis, uma marca de média por
resultado, reinício da ocupação ao exceder a capacidade da célula, 3.000
resultados abaixo dos limites de 2 segundos e 128 MiB adicionais e limpeza
integral. Evidências em `MSen/tests/TESTE_ITEM_6_4.md`.

### Item 6.5 — Testes de interface automatizados

Escolher ferramenta somente com autorização e cobrir os principais fluxos no
navegador.

Estado: concluído em 2026-10-26. Playwright 1.64.1 reutiliza o Google Chrome
instalado e executa em modo invisível. Três fluxos reais de navegador cobrem
carregamento/navegação, voo e seleção de Excel/importação simulada/mancha/
limpeza. A API é simulada para impedir alterações no banco nessa camada. Os três
testes de navegador, dezenove testes unitários de frontend e 137 testes Python
passaram. Evidências em `MSen/tests/TESTE_ITEM_6_5.md`.

Estado da Etapa 6: concluída.

---

## ETAPA 7 — Integração completa local

### Item 7.1 — Fluxo Excel até PostgreSQL

Selecionar arquivo, importar, calcular, armazenar e apresentar relatório.

Estado: concluído em 2026-10-26. Um teste Playwright no Google Chrome criou um
database PostgreSQL efêmero e migrado, selecionou uma planilha controlada,
enviou-a pela API, inseriu dois resultados com campos calculados, atualizou 60
frequências com 12 ocorrências e exibiu o relatório na interface. A reimportação
inseriu zero duplicidades. O database e os servidores temporários foram removidos
ao final. Os dois testes integrados 7.1/7.2 passaram em 8,1 segundos, além de 19
testes de frontend, 3 testes Chrome isolados e 140 testes Python. Evidências em
`MSen/tests/TESTE_ITEM_7_1.md`.

### Item 7.2 — Fluxo PostgreSQL até gráficos

Carregar dados, navegar, animar e desenhar mancha.

Estado: concluído em 2026-10-26. O Flask passou a servir frontend e API na
mesma origem. Um teste Playwright no Google Chrome carregou os 3.069 resultados
reais do PostgreSQL, navegou entre primeiro e último, executou o voo, desenhou
18.414 marcas de dezenas e 3.069 marcas de média e limpou a camada. A contagem
permaneceu em 3.069 antes e depois. O teste integrado passou em 4,3 segundos;
19 testes de frontend, 3 testes de navegador isolados e 138 testes Python também
passaram. Evidências em `MSen/tests/TESTE_ITEM_7_2.md`.

### Item 7.3 — Teste de regressão

Executar testes Python, SQL, API e frontend em conjunto.

Critério para avançar:

- todos os testes aprovados;
- backup e restauração local ensaiados;
- nenhuma pendência crítica conhecida.

Estado: concluído em 2026-10-26. Passaram 140 testes Python, 19 testes
unitários de frontend, 3 fluxos isolados no Google Chrome e 2 fluxos integrados
Chrome/PostgreSQL. O backup local foi restaurado em database efêmero e conferiu
3.069 resultados, 60 registros de frequência e 18.414 ocorrências. O database
temporário foi removido e nenhuma pendência crítica foi encontrada no escopo
implementado. Evidências em `MSen/tests/TESTE_ITEM_7_3.md`.

---

## ETAPA 8 — Preparação do PythonAnywhere

Estado: adiada por decisão do usuário até todo o desenvolvimento local estar
concluído, testado e aprovado.

### Item 8.1 — Inventário somente leitura

Conferir versões, banco, usuário, WSGI, caminhos e limitações sem alterar o
ambiente remoto.

### Item 8.2 — Plano de publicação e reversão

Definir backup, migrações, validação, recarga e retorno à versão anterior.

### Item 8.3 — Publicação autorizada

Executar somente com autorização específica para banco e aplicação remotos.

### Item 8.4 — Validação pós-publicação

Testar conexão, importação controlada, consultas, navegação e gráficos; registrar
resultado e preservar evidências sem credenciais.

---

## ETAPA 9 — Cadastro e análise de padrões

Esta etapa será desenvolvida inteiramente no ambiente local. Cada item exige
autorização expressa e será testado antes do seguinte.

### Item 9.1 — Contrato dos padrões

Definir e documentar antes da migração:

- significado exato de padrão, ocorrência e intervalo;
- campos e tipos definitivos da tabela `padroes`;
- vínculo estável entre cada registro e sua função Python detectora;
- regra para inclusão e exclusão de registros cujo detector ainda não exista;
- ordem de aplicação dos padrões no funil;
- distinção entre detecção binária de uma combinação e análise estatística do
  histórico.

Teste: exemplos escritos e casos-limite aprovados pelo usuário, sem alterar o
banco.

Estado: concluído em 2026-10-26. O contrato separa detecção binária de uma
combinação e análise estatística do histórico; define código estável, nome,
descrição e campos calculados; protege as estatísticas no frontend e na API; e
torna obrigatórias docstrings em português no futuro módulo Python. A semântica
matemática de cada detector será aprovada antes do Item 9.4. Documento em
`docs/CONTRATO_PADROES.md`.

### Item 9.2 — Migração PostgreSQL da tabela `padroes`

Criar uma migração incremental, sem alterar ou recriar as tabelas existentes.
Incluir chave primária, descrição e os campos estatísticos aprovados no Item
9.1.

Teste: aplicar a migração em database temporário, conferir estrutura,
restrições e compatibilidade com database vazio e já preenchido.

Estado: concluído em 2026-10-26. A migração `002` criou as sete colunas e
restrições contratadas. Foi validada em database temporário e aplicada ao
`games` local preenchido, preservando 3.069 resultados e 60 frequências. A nova
tabela ficou vazia, as migrações `001` e `002` estão registradas, 140 testes
Python e 2 fluxos integrados Chrome/PostgreSQL passaram. Evidências em
`MSen/tests/TESTE_ITEM_9_2.md`.

### Item 9.3 — Módulo Python de padrões

Criar um pacote separado em `MSen/src/msen/padroes/`, destinado aos detectores
e cálculos estatísticos dos padrões. Toda função pública deverá possuir uma
docstring em português explicando:

- o que a função faz;
- parâmetros recebidos;
- valor retornado;
- regra aplicada e casos relevantes.

Os nomes deverão indicar claramente a finalidade. Funções diferentes não
deverão misturar detecção, estatística, persistência ou execução do funil.

Teste: verificar importação do módulo, documentação obrigatória e contratos
básicos sem implementar antecipadamente padrões ainda não aprovados.

Estado: concluído em 2026-10-26. Foi criado o pacote `msen.padroes` com contrato
de detector e registro explícito por `padrao_cod`. Códigos inválidos,
substituição e detector pendente possuem erros próprios. O pacote começa vazio,
sem antecipar funções do Item 9.4. Sete testes específicos exigem inclusive a
documentação dos elementos públicos; os 147 testes Python passaram. Evidências
em `MSen/tests/TESTE_ITEM_9_3.md`.

### Item 9.4 — Detectores e estatísticas iniciais

Implementar, somente após aprovação individual das definições, as funções para
duas dezenas sequenciais, três dezenas sequenciais e mais de três dezenas
sequenciais. Reutilizar a detecção binária para analisar os resultados
históricos e calcular quantidade de resultados, intervalos, intervalo médio e
desvio-padrão.

Teste: cobrir ocorrências, não ocorrências, limites 01/60, resultados com mais
de um grupo e histórico insuficiente para calcular intervalos.

Estado: concluído em 2026-10-26. Por aprovação do usuário, cada resultado é
classificado exclusivamente pelo maior bloco: dois, três ou mais de três. Foram
implementados detectores puros, registro dos três códigos e estatística
reutilizável. Passaram 19 testes específicos e 159 testes Python acumulados. A
leitura dos 3.069 resultados encontrou 1.192 ocorrências de `PD_001`, 92 de
`PD_002` e 5 de `PD_003`; nada foi gravado no banco. Evidências em
`MSen/tests/TESTE_ITEM_9_4.md`.

### Item 9.5 — Persistência e recálculo dos padrões

Criar repositório e serviço para consultar o cadastro, salvar alterações
permitidas e recalcular estatísticas a partir de `resultados` sem aceitar
estatísticas digitadas como valores confiáveis.

Teste: CRUD e recálculo em database temporário, preservando resultados e demais
tabelas.

Estado: concluído em 2026-10-26. Foram criados repositório e serviço transacional
para cadastrar e recalcular os três padrões, preservando textos editáveis. O
recálculo foi integrado a importação, inclusão e edição de resultados. O teste
temporário confirmou valores, idempotência e preservação do nome. No `games`,
foram persistidas as estatísticas de 3.069 resultados. Passaram 164 testes Python
e 2 fluxos Chrome/PostgreSQL. Evidências em `MSen/tests/TESTE_ITEM_9_5.md`.

### Item 9.6 — API CRUD de padrões

Criar endpoints locais para listar, inserir, editar e excluir padrões conforme
as regras aprovadas no contrato. Validar todas as entradas e não expor detalhes
do banco em respostas de erro.

Teste: respostas válidas, dados inválidos, duplicidades, registros ausentes e
falhas simuladas do banco.

Estado: concluído em 2026-10-26. A API oferece listagem, criação, edição dos
textos e exclusão, protegendo código, identificador e estatísticas. A migração
`003` inicializa os três padrões e garante códigos não reutilizáveis. O teste
temporário confirmou CRUD, exclusão respeitada e detector pendente; a consulta
real ao `games` retornou os três padrões. Passaram 10 testes específicos, 174
testes Python e 2 fluxos Chrome/PostgreSQL. Evidências em
`MSen/tests/TESTE_ITEM_9_6.md`.

### Item 9.7 — Grade de Cadastro de Padrões

Criar no `frontend` uma tela em formato de tabela, com cabeçalho fixo, rolagem
vertical e rolagem horizontal quando necessária. Permitir as operações CRUD
aprovadas e exibir os campos estatísticos calculados como somente leitura.
Manter HTML, CSS e JavaScript em suas pastas separadas.

Teste: operações na grade, rolagem, validações, mensagens de erro e visualização
no Google Chrome.

Estado: concluído em 2026-10-26. Foi criada uma grade com cabeçalho fixo,
rolagem, inclusão, edição direta dos textos, campos calculados somente para
leitura e exclusão confirmada. HTML, CSS e JavaScript permanecem separados. A
interface passou em 20 testes de frontend, 4 fluxos Chrome simulados, 174 testes
Python e 2 fluxos Chrome/PostgreSQL; a integração real foi somente leitura.
Evidências em `MSen/tests/TESTE_ITEM_9_7.md`.

### Item 9.8 — Integração e regressão local

Validar o fluxo completo cadastro → função Python → histórico → estatísticas →
PostgreSQL → grade. Confirmar que nenhuma regressão foi introduzida nas funções
existentes.

Teste: todas as suítes Python, API, PostgreSQL, frontend e Chrome aprovadas,
com evidência registrada antes de qualquer commit ou publicação.

Estado: concluído em 2026-10-26. Um fluxo real em database temporário percorreu
histórico, detectores, estatísticas, PostgreSQL, API e grade CRUD, incluindo
edição preservada, código não reutilizado e exclusão respeitada. O backup antigo
foi restaurado, recebeu as migrações `002/003` e reproduziu as estatísticas. A
regressão aprovou 174 testes Python, 20 de frontend, 4 fluxos Chrome isolados e
3 fluxos Chrome/PostgreSQL. Evidências em `MSen/tests/TESTE_ITEM_9_8.md`.

Estado da Etapa 9: concluída localmente.

### Funcionalidade futura — funil do screener

O screener será planejado em etapa própria depois que os padrões iniciais
estiverem definidos e validados. Ele gerará as 50.063.860 combinações de forma
progressiva. Ao primeiro padrão correspondente, contabilizará a exclusão e
saltará imediatamente para a próxima combinação. O relatório mostrará entradas,
exclusões e saldo em cada nível do funil. Nenhum código do screener faz parte da
Etapa 9.

---

## ETAPA 10 — Grupos de padrões e navegação compacta

Esta etapa reorganiza os padrões em grupos conceituais e separa o Painel dos
cadastros. Os itens serão curtos, usarão testes direcionados e dependerão de
autorização expressa. A regressão completa ficará reservada aos marcos finais.

### Item 10.1 — Contrato da reorganização

Definir tabelas, relação, duplicidades, exclusões, migração dos registros
existentes, menu horizontal, botão Voltar e regras de aproveitamento de espaço.

Estado: concluído em 2026-10-27, sem alterar banco ou aplicação. Foi definida
a relação de um grupo para muitos padrões; exclusão protegida de grupos com
padrões; unicidade normalizada dos nomes; migração preservando `PD_001` a
`PD_003`; e navegação em uma única barra horizontal. Documento em
`docs/CONTRATO_GRUPOS_E_NAVEGACAO.md`.

### Item 10.2 — Migração isolada da estrutura

Criar `padroes_grupo`, transformar `padroes` em `padroes_subgrupo`, adicionar a
chave estrangeira e classificar os padrões nos grupos iniciais aprovados.
Validar em PostgreSQL temporário, sem alterar o `games`.

Estado: concluído em 2026-10-27. A migração `004` e o esquema canônico foram
criados. O ensaio partiu das versões `001`–`003`, preservou os padrões e
estatísticas previamente preenchidas, e rejeitou duplicidades, grupo inexistente
e exclusão de grupo ocupado. O database temporário foi removido; `games` e
PythonAnywhere não foram alterados. Evidências em
`MSen/tests/TESTE_ITEM_10_2.md`.

### Item 10.3 — Validação e aplicação local

Validar a migração sobre estrutura anterior preenchida, conferir preservação e
aplicá-la ao PostgreSQL local `games`, com evidência.

Estado: concluído em 2026-10-27, depois dos Itens 10.4–10.10 para manter todas
as camadas compatíveis. Foi gerado backup com SHA-256, a migração foi ampliada
para classificar corretamente os seis padrões reais e novamente ensaiada. O
`games` recebeu somente a versão `004`, preservando 3.069 resultados, 60
frequências, seis padrões e suas estatísticas. Uma instância antiga que
compartilhava a porta 5050 foi encerrada e o servidor atualizado respondeu HTTP
200 nas APIs e páginas. Evidências em `MSen/tests/TESTE_ITEM_10_3.md`.

### Item 10.4 — Repositório Python de grupos

Implementar CRUD e proteção de exclusão, com docstrings e testes em banco
temporário.

Estado: concluído em 2026-10-27. O repositório separado lista, cria, edita,
consulta vínculos e exclui somente grupos vazios. Os códigos não são
reutilizados e os erros de duplicidade, grupo ocupado e grupo inexistente são
seguros. Passaram 5 testes unitários e o CRUD PostgreSQL temporário; o database
efêmero foi removido. Evidências em `MSen/tests/TESTE_ITEM_10_4.md`.

### Item 10.5 — Adaptação do repositório de padrões

Usar `padroes_subgrupo`, exigir grupo válido e preservar detectores e cálculos.

Estado: concluído em 2026-10-27. O repositório passou a retornar o grupo, exigir
grupo válido na criação, permitir transferência na edição e filtrar a listagem.
Recálculo, estatísticas, exclusões e códigos não reutilizáveis foram preservados.
Passaram 27 testes direcionados e um fluxo PostgreSQL temporário. Evidências em
`MSen/tests/TESTE_ITEM_10_5.md`.

### Item 10.6 — API de grupos

Implementar e testar listagem, inclusão, edição e exclusão protegida.

Estado: concluído em 2026-10-27. A API `/api/grupos-padroes` oferece CRUD,
protege código e identificador, rejeita duplicidade e distingue grupo ocupado e
ausente. Passaram 28 testes direcionados da API e da fábrica Flask, sem acessar
o database `games`. Contrato em `docs/API_GRUPOS_PADROES.md` e evidências em
`MSen/tests/TESTE_ITEM_10_6.md`.

### Item 10.7 — Adaptação da API de padrões

Incluir o grupo no contrato da API e preservar a proteção das estatísticas.

Estado: concluído em 2026-10-27. A API exige e retorna o grupo, aceita filtro e
transferência, protege campos derivados e diferencia grupo inválido de ausente.
Passaram 36 testes direcionados e um fluxo HTTP/PostgreSQL temporário completo.
Evidências em `MSen/tests/TESTE_ITEM_10_7.md`.

### Item 10.8 — Páginas e menu horizontal

Separar Painel e Cadastros e criar a navegação compacta com submenu e Voltar.

Estado: concluído em 2026-10-27. O Painel e três páginas de cadastro foram
separados e ligados por barra horizontal de 2,8 rem, submenu flutuante e botão
Voltar. Passaram 20 testes de frontend, 4 fluxos no Google Chrome e a entrega
HTTP 200 das quatro páginas pelo Flask. Evidências em
`MSen/tests/TESTE_ITEM_10_8.md`.

### Item 10.9 — Página de grupos

Criar grade CRUD compacta, com cabeçalho fixo e rolagem interna.

Estado: concluído em 2026-10-27. A página possui barra de inclusão em uma linha,
grade com rolagem interna, cabeçalho fixo, colunas compactas e CRUD completo. A
interface preserva grupo ocupado e mostra o erro da API. Passaram 21 testes de
frontend e o fluxo CRUD no Google Chrome. Evidências em
`MSen/tests/TESTE_ITEM_10_9.md`.

### Item 10.10 — Página de padrões

Transferir o cadastro atual para página própria, com grupo obrigatório e filtro.

Estado: concluído em 2026-10-27. A grade permite inclusão, edição, transferência,
filtro e exclusão, mantendo estatísticas somente para leitura. A disposição
compacta preserva as larguras aprovadas para ocorrência, nome e descrição.
Passaram 22 testes de frontend e 6 fluxos no Google Chrome. Evidências em
`MSen/tests/TESTE_ITEM_10_10.md`.

### Item 10.11 — Integração com PostgreSQL

Validar o fluxo real completo em banco temporário e fazer leitura final do
`games`.

Estado: concluído em 2026-10-27. Passaram três fluxos Chrome/PostgreSQL cobrindo
Excel, cálculos, grupos, padrões, transferência, exclusões, navegação, voo e
mancha. Os bancos mutáveis foram temporários e removidos; a leitura final do
`games` confirmou 3.069 resultados, 60 frequências, dois grupos e seis padrões,
com estatísticas preservadas. Evidências em `MSen/tests/TESTE_ITEM_10_11.md`.

### Item 10.12 — Teste de compactação visual

Conferir consumo vertical, larguras, rolagens, cabeçalhos e telas menores no
Google Chrome.

Estado: concluído em 2026-10-27. Com 30 grupos e 45 padrões simulados, o Chrome
confirmou barra de até 46 px, submenu sem deslocamento, grades contidas, rolagens
internas e cabeçalhos fixos em 1280 × 720 e 700 × 600. Passaram 22 testes de
frontend e 8 fluxos Chrome. Evidências em `MSen/tests/TESTE_ITEM_10_12.md`.

### Item 10.13 — Regressão e documentação

Executar todas as suítes, validar migrações e atualizar os documentos de
continuidade.

Estado: concluído em 2026-10-27. Passaram 193 testes Python, 22 testes de
frontend, 8 fluxos no Google Chrome e 3 fluxos Chrome/PostgreSQL. A migração
004 foi validada no caminho normal, na interrupção segura e reversão diante de
padrão não classificado e na criação do esquema canônico do zero. O database
`games` permaneceu íntegro e o servidor local saudável. Evidências em
`MSen/tests/TESTE_ITEM_10_13.md`.

Estado da Etapa 10: concluída em 2026-10-27 e publicada em `origin/developer`
no commit `022331c`. PythonAnywhere permanece adiado.

---

## ETAPA 11 — Padrões de dezenas na mesma coluna

### Item 11.1 — Contrato e casos de teste

Formalizar a matriz, a identificação das colunas, a classificação exclusiva de
`PD_004`–`PD_006` e os casos obrigatórios para os testes.

Estado: concluído em 2026-10-27 e corrigido no Item 11.6 após esclarecimento do
usuário. A classificação usa a maior sequência vertical em linhas subjacentes:
exatamente duas, exatamente três ou mais de três dezenas. Cada resultado conta
no máximo uma ocorrência e pertence a apenas um dos três padrões. Contrato em
`docs/CONTRATO_PADROES_MESMA_COLUNA.md` e evidência em
`MSen/tests/TESTE_ITEM_11_1.md`.

### Item 11.2 — Detectores Python

Implementar e testar os três detectores puros, com docstrings em português,
sem persistência ou alteração do PostgreSQL.

Estado: concluído em 2026-10-27 e corrigido no Item 11.6. Os detectores usam a
maior sequência vertical subjacente, validam a entrada e estão documentados em
português. Nenhum banco foi acessado neste item. Evidência em
`MSen/tests/TESTE_ITEM_11_2.md`.

### Item 11.3 — Registro e estatísticas históricas

Associar os detectores a `PD_004`–`PD_006`, reutilizar o cálculo estatístico e
testar ocorrências e intervalos conhecidos, ainda sem gravar no PostgreSQL.

Estado: concluído em 2026-10-27. Um registro independente associa os três
códigos aos detectores, e o cálculo conjunto em memória reutiliza a estatística
aprovada. Passaram 29 testes direcionados, incluindo ocorrências, intervalos,
média, desvio, históricos insuficientes, iterador e regressões. Nenhum banco foi
acessado. Evidência em `MSen/tests/TESTE_ITEM_11_3.md`.

### Item 11.4 — Integração do serviço e persistência

Integrar os seis padrões ao recálculo transacional, persistir as estatísticas de
`PD_004`–`PD_006` e validar tudo primeiro em PostgreSQL temporário.

Estado: concluído em 2026-10-27. Serviço e API usam o catálogo dos seis
detectores. Passaram 204 testes Python. Um PostgreSQL temporário confirmou duas
execuções idempotentes e os intervalos esperados de `PD_004`–`PD_006`; ele foi
removido e o `games` não foi acessado. Evidência em
`MSen/tests/TESTE_ITEM_11_4.md`.

### Item 11.5 — Aplicação controlada no banco local

Criar backup de segurança, recalcular os seis padrões no `games` e conferir os
valores persistidos por leitura, sem alterar esquema ou PythonAnywhere.

Estado: concluído em 2026-10-27. Um backup custom validado foi criado antes da
transação. O primeiro recálculo foi posteriormente invalidado pelo esclarecimento
da regra no Item 11.6; seu backup e sua evidência foram preservados para
rastreabilidade. Evidência em `MSen/tests/TESTE_ITEM_11_5.md`.

### Item 11.6 — Revisão textual e integração visual

Após confirmação do usuário, alinhar nomes e descrições de `PD_004`–`PD_006` ao
contrato aprovado, reiniciar o servidor e validar API e grade no Chrome.

Estado: concluído em 2026-10-27. O usuário esclareceu a exigência de linhas
imediatamente subjacentes. Contrato, detectores e testes foram corrigidos; o
PostgreSQL temporário passou e foi removido. Após novo backup, o `games` foi
recalculado com `PD_004=1037`, `PD_005=66` e `PD_006=4`. Passaram 205 testes
Python, 22 de frontend, 8 fluxos Chrome e uma validação Chrome real da grade.
Servidor reiniciado no PID 8556. Evidência em `MSen/tests/TESTE_ITEM_11_6.md`.

### Item 11.7 — Regressão integrada e fechamento

Executar os fluxos Chrome/PostgreSQL completos, auditar o banco local por
leitura, finalizar a documentação e preparar a Etapa 11 para versionamento.

Estado: concluído em 2026-10-27. A regressão revelou que instalações novas não
reservavam `PD_004`–`PD_006`; a migração `005` e o esquema canônico corrigiram
o problema, deixando `PD_007` como primeiro código livre. Passaram 205 testes
Python, 22 de frontend, 8 fluxos Chrome e 3 fluxos Chrome/PostgreSQL. Migrações,
esquema do zero, banco local, API e grade real foram auditados. Evidência em
`MSen/tests/TESTE_ITEM_11_7.md`.

Estado da Etapa 11: concluída em 2026-10-27 e publicada em `origin/developer`
no commit `e24ba66`. PythonAnywhere permanece adiado.

---

## ETAPA 12 — Padrões de dezenas na mesma linha

### Item 12.1 — Leitura do cadastro, contrato e casos de teste

Interpretar `PG_003` e `PD_007`–`PD_009`, formalizar a classificação exclusiva
e preparar os casos obrigatórios antes de criar funções.

Estado: concluído em 2026-10-27. Os três padrões estão corretamente associados
a `PG_003`. A classificação usará a maior ocupação entre as seis linhas, sem
exigir sequencialidade. Nenhum código ou dado foi alterado. Contrato em
`docs/CONTRATO_PADROES_MESMA_LINHA.md` e evidência em
`MSen/tests/TESTE_ITEM_12_1.md`.

### Item 12.2 — Detectores Python

Implementar e testar os três detectores puros, com docstrings em português,
sem registro no catálogo ou acesso ao PostgreSQL.

Estado: concluído em 2026-10-27. Os detectores classificam exclusivamente pela
maior ocupação de linha, sem exigir sequencialidade, validam a entrada e possuem
docstrings em português. Passaram 38 testes direcionados. Nenhum banco foi
acessado. Evidência em `MSen/tests/TESTE_ITEM_12_2.md`.

### Item 12.3 — Registro e estatísticas históricas

Associar os detectores a `PD_007`–`PD_009`, reutilizar o cálculo estatístico e
testar ocorrências e intervalos conhecidos em memória.

Estado: concluído em 2026-10-27. O registro associa os três códigos, o catálogo
unificado contém nove detectores e o cálculo em memória reutiliza a estatística
aprovada. Passaram 55 testes direcionados; nenhum banco foi acessado. Evidência
em `MSen/tests/TESTE_ITEM_12_3.md`.

### Item 12.4 — Integração e persistência temporária

Integrar `PD_007`–`PD_009` ao serviço de recálculo e validar suas estatísticas
em PostgreSQL temporário, sem alterar o `games`.

Estado: concluído em 2026-10-27. O serviço calcula nove padrões. A migração
`006` e o esquema canônico reservam `PG_003` e `PD_007`–`PD_009`. A persistência
idempotente foi validada com intervalos conhecidos, as migrações `001`–`006`
foram ensaiadas e passaram 216 testes Python. Nenhum database temporário
permaneceu e o `games` não foi acessado. Evidência em
`MSen/tests/TESTE_ITEM_12_4.md`.

### Item 12.5 — Aplicação controlada no banco local

Criar backup, aplicar a migração `006`, recalcular os nove padrões no `games` e
conferir `PD_007`–`PD_009` por leitura.

Estado: concluído em 2026-10-27. Um backup custom validado foi criado antes da
migração e da transação. O `games` passou à versão `006`, preservou 3.069
resultados e calculou `PD_007=2053`, `PD_008=863` e `PD_009=93`, mantendo
cadastros e textos. A API retornou os valores; o processo ainda será reiniciado.
Evidência em `MSen/tests/TESTE_ITEM_12_5.md`.

### Item 12.6 — Reinício e integração visual

Reiniciar o servidor local, confirmar os nove detectores na API e validar a
grade real no Google Chrome.

Estado: concluído em 2026-10-27. O servidor foi reiniciado no PID 12888. A API
retornou nove padrões implementados e a grade real no Chrome confirmou nomes,
estatísticas e estado de `PD_004`–`PD_009`. Nenhum dado foi modificado pelo
teste. Evidência em `MSen/tests/TESTE_ITEM_12_6.md`.

### Item 12.7 — Regressão integrada e fechamento

Executar todas as suítes, adaptar os fluxos Chrome/PostgreSQL ao catálogo de
nove padrões, auditar o `games` e finalizar a documentação da Etapa 12.

Estado: concluído em 2026-10-27. Passaram 216 testes Python, 22 testes de
frontend, 8 fluxos Chrome e 3 fluxos Chrome/PostgreSQL. Os testes integrados
foram atualizados para o catálogo de nove padrões e para os próximos códigos
livres `PG_004`, `PD_010` e `PD_011`. O banco `games` foi auditado na versão
`006`, sem migrações pendentes, com 3.069 resultados, nove padrões
implementados e nenhum database temporário remanescente. Evidência em
`MSen/tests/TESTE_ITEM_12_7.md`.

Estado da Etapa 12: concluída em 2026-10-27. As alterações ainda não foram
commitadas. PythonAnywhere permanece adiado.

---

## Próximo item proposto

Commit de segurança da Etapa 12. Não executar sem autorização expressa. O push
será solicitado separadamente. A Etapa 8/PythonAnywhere permanece adiada.
