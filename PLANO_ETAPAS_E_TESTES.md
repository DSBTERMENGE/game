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

Estado da Etapa 12: concluída em 2026-10-27 e publicada em `origin/developer`
no commit `a299404`. PythonAnywhere permanece adiado.

---

## ETAPA 13 — Análise geométrica dos resultados

Objetivo: desenhar e medir a figura determinada pelas seis dezenas em ordem
crescente, validar os cálculos contra o histórico e somente depois estudar
critérios de exclusão. Nesta etapa nenhuma combinação será excluída.

### Item 13.1 — Contrato geométrico e exemplos de referência

Formalizar coordenadas, ordenação crescente, linha aberta, fechamento, regras
de interseção, soma das regiões fechadas, centro de gravidade único e casos
degenerados. Preparar exemplos manuais com resultados esperados antes do código.

Estado: concluído em 2026-10-27. O contrato definiu a rede planar formada pelo
percurso crescente, área total sem cancelamentos, centro de gravidade ponderado,
coordenadas exatas para a topologia e quatro exemplos numéricos de referência.
Nenhum código de cálculo ou banco foi alterado. Contrato em
`docs/CONTRATO_ANALISE_GEOMETRICA.md` e evidência em
`MSen/tests/TESTE_ITEM_13_1.md`.

### Item 13.2 — Caminho aberto e medidas básicas

Criar funções Python puras e documentadas para converter dezenas em pontos,
ordenar os vértices, montar segmentos e calcular a extensão da linha aberta e o
perímetro fechado. Executar somente testes unitários.

Estado: concluído em 2026-10-27. O novo pacote `msen.geometria` usa pontos
exatos, ordena as dezenas sem alterar a entrada e calcula extensão e perímetro
em `Decimal`. Passaram 11 testes direcionados e 227 testes Python no total.
Nenhum banco foi acessado. Evidência em `MSen/tests/TESTE_ITEM_13_2.md`.

### Item 13.3 — Interseções e regiões fechadas

Detectar cruzamentos, dividir os segmentos nos pontos de interseção e identificar
todas as regiões fechadas. Testar separadamente figuras sem cruzamento, com um
cruzamento, com vários cruzamentos e casos degenerados.

Estado: concluído em 2026-10-27. A rede planar usa aritmética exata, normaliza
sobreposições e identifica apenas faces limitadas. Passaram 12 testes
direcionados, uma varredura de estabilidade com 5.000 combinações e 239 testes
Python acumulados. Nenhum banco foi acessado. Evidência em
`MSen/tests/TESTE_ITEM_13_3.md`.

### Item 13.4 — Área total e centro de gravidade

Calcular a área de cada região, somá-las numa única área e obter um único centro
de gravidade pela ponderação das áreas. Comparar os cálculos com exemplos
manuais e garantir que a ordem original do sorteio não afete o resultado.

Estado: concluído em 2026-10-27. Áreas, centroides e centro de gravidade global
são calculados exatamente, sem cancelamento entre regiões. Os três exemplos do
contrato, orientação, concavidade e ponderação foram confirmados. Passaram 10
testes direcionados, uma varredura de 5.000 combinações e 249 testes Python
acumulados. Nenhum banco foi acessado. Evidência em
`MSen/tests/TESTE_ITEM_13_4.md`.

### Item 13.5 — Persistência e migração temporária

Definir uma tabela de análise geométrica relacionada individualmente a cada
resultado, contendo extensão aberta, perímetro, área total, coordenadas do
centro de gravidade e versão do cálculo. Criar migração e validar em PostgreSQL
temporário, sem alterar o `games`.

Estado: concluído em 2026-10-27. A migração `007`, o esquema canônico e o
repositório foram validados em PostgreSQL temporário, incluindo idempotência,
restrições e cascata. O database efêmero foi removido, passaram 249 testes
Python e o `games` permaneceu inalterado. Evidência em
`MSen/tests/TESTE_ITEM_13_5.md`.

### Item 13.6 — Serviço de cálculo histórico

Integrar o cálculo ao cadastro, edição e importação de resultados. Recalcular
uma amostra controlada em banco temporário, validar idempotência e conferir que
os 3.069 resultados existentes permanecem inalterados.

Estado: concluído em 2026-10-27. Inclusão, edição e importação passaram a
persistir a geometria na mesma transação. Um PostgreSQL temporário confirmou
áreas 36, 4,5 e zero, relação individual e recálculo idempotente. Passaram 249
testes Python, o temporário foi removido e o `games` não foi conectado nem
alterado. Evidência em `MSen/tests/TESTE_ITEM_13_6.md`.

### Item 13.7 — Desenho no painel

Desenhar círculos de cerca de 2 mm nos seis centros, linha aberta, fechamento,
ponto da média e centro de gravidade. Exibir extensão, perímetro e área. Manter
HTML, CSS e JavaScript separados e testar redimensionamento e legibilidade.

Estado: concluído em 2026-10-27. A API fornece a geometria exata e o painel
desenha regiões, percurso, fechamento, vértices, média e CG, além de um resumo
compacto. Passaram 250 testes Python, 23 testes de frontend e 8 fluxos Chrome.
O `games` não recebeu a migração `007`. Evidência em
`MSen/tests/TESTE_ITEM_13_7.md`.

### Item 13.8 — Configuração visual persistente

Criar painel compacto para cores, espessuras, tamanhos, transparência e
visibilidade das entidades gráficas. Persistir as preferências e validar sua
restauração após reiniciar a página.

Estado: concluído em 2026-10-27. O diálogo `Aparência` configura sete cores,
medidas, transparência e visibilidade sem ocupar altura permanente. As escolhas
validadas persistem no navegador e podem ser restauradas. Passaram 250 testes
Python, 24 de frontend e 9 fluxos Chrome. Nenhum banco foi alterado. Evidência
em `MSen/tests/TESTE_ITEM_13_8.md`.

### Item 13.9 — Aplicação controlada no histórico local

Criar backup, aplicar a migração no `games`, calcular as medidas dos 3.069
resultados e validar visualmente uma amostra no Chrome. Ainda não criar limites
de aprovação ou exclusão.

Estado: concluído em 2026-10-27. Um backup custom validado foi criado, somente a
migração `007` foi aplicada e 3.069 análises foram associadas aos 3.069
resultados. O servidor foi reiniciado no PID 37548 e o Chrome real confirmou
desenho e medidas. A carga integral da API levou cerca de 8,1 segundos e será
revista no fechamento. Evidência em `MSen/tests/TESTE_ITEM_13_9.md`.

### Item 13.10 — Distribuições históricas e fechamento

Apresentar mínimo, máximo, média, mediana, desvio-padrão e distribuição das
medidas geométricas. Executar regressão completa, documentar os resultados e
preparar um commit de segurança mediante autorização.

Estado: concluído em 2026-10-27. Foram apuradas as distribuições das cinco
medidas e da quantidade de regiões. O carregamento inicial foi reduzido em
aproximadamente 71,3% com geometria sob demanda. Passaram 254 testes Python,
24 JavaScript, 9 fluxos Chrome, 3 integrações Chrome/PostgreSQL e a validação
visual real. Evidência em `MSen/tests/TESTE_ITEM_13_10.md`. Etapa 13 concluída;
aguardar autorização para o commit de segurança.

---

## ETAPA 14 — Gerador de combinações e screener experimental

Objetivo: fazer o fluxo completo funcionar com uma amostra repetível, sem
autorizar ainda a execução das 50.063.860 combinações possíveis.

### Item 14.1 — Contrato e arquivo de configuração

Definir a ordem dos filtros, tolerâncias, semente aleatória, limite de teste e
modo de execução. Criar configuração padrão versionada e configuração local
ignorada pelo Git. O limite inicial obrigatório será 5.000 combinações.

Estado: concluído em 2026-10-27. O contrato, o TOML padrão, a substituição
local ignorada e as travas de validação foram criados. Todos os critérios
continuam inativos e nenhum gerador foi executado. Passaram 260 testes Python.
Evidência em `MSen/tests/TESTE_ITEM_14_1.md`.

### Item 14.2 — Gerador amostral repetível

Gerar 5.000 combinações aleatórias distintas, sempre ordenadas, usando uma
semente registrada. Impedir duplicidades e provar por teste que a mesma semente
reproduz a mesma amostra.

Estado: concluído em 2026-10-27. O gerador isolado produz exatamente 5.000
combinações distintas, ordenadas e válidas; a mesma semente reproduz a mesma
lista. Ele rejeita modo integral e não altera o estado aleatório global.
Passaram 267 testes Python. Evidência em `MSen/tests/TESTE_ITEM_14_2.md`.

### Item 14.3 — Gerador integral protegido

Preparar o iterador definitivo com `itertools.combinations(range(1, 61), 6)`.
No modo de teste, interromper o laço quando `processadas >= 5000`. O modo
integral deverá exigir configuração e confirmação explícitas; retirar o limite
somente quando todo o fluxo estiver validado e houver autorização específica.

Estado: concluído em 2026-10-27. O iterador lexicográfico usa
`itertools.combinations`; no modo amostral, `islice` o encerra em 5.000. O modo
integral possui duas confirmações independentes e continua sem ser executado.
Passaram 274 testes Python. Evidência em `MSen/tests/TESTE_ITEM_14_3.md`.

### Item 14.4 — Estrutura do funil e contadores

Criar o encadeamento configurável de critérios. Quando uma combinação for
reprovada, contabilizar o filtro responsável e avançar imediatamente para a
próxima. Nenhum critério real será ativado antes de sua regra ser aprovada.

Estado: concluído em 2026-10-27. O funil executa critérios em ordem, atribui a
exclusão apenas ao primeiro que reprovar e salta imediatamente para a próxima
combinação. O relatório consolida entradas, avaliações, exclusões, saldos e
aprovadas. Nenhum critério real foi ativado. Passaram 279 testes Python.
Evidência em `MSen/tests/TESTE_ITEM_14_4.md`.

### Item 14.5 — Adaptadores dos critérios

Preparar interfaces separadas para padrões históricos, medidas estatísticas e
medidas geométricas. Cada decisão deverá informar aprovação/reprovação, código
do critério e valores que justificaram a decisão.

Estado: concluído em 2026-10-27. Foram criados adaptadores separados para
padrões históricos, estatísticas e geometria. Todos produzem a decisão comum
com código e valores justificadores; desabilitados, não chamam funções. Nenhuma
regra real foi ativada. Passaram 284 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_14_5.md`.

### Item 14.6 — Quadro de avaliação

Mostrar total recebido, exclusões por critério, saldo após cada filtro, tempo e
ordem de execução. Registrar também a configuração e a semente do ensaio para
que os resultados possam ser reproduzidos.

Estado: concluído em 2026-10-27. O quadro registra configuração, semente,
tempo, totais e, por filtro, ordem, avaliações, exclusões e saldo. A saída pode
ser serializada para JSON e futura tela. Um ensaio sem filtros recebeu e aprovou
as 5.000 combinações. Passaram 289 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_14_6.md`.

### Item 14.7 — Ensaio integrado de 5.000 combinações

Executar o fluxo completo sem filtros e depois com critérios aprovados,
conferindo que a contabilidade fecha. Comparar ordens de filtros sem interpretar
a amostra como prova estatística do universo completo.

Estado: concluído em 2026-10-27 dentro das regras atualmente aprovadas. O fluxo
configuração/geração/funil/quadro recebeu e aprovou 5.000 sem filtros. Como não
há regra real de exclusão aprovada, a execução filtrada e a comparação de ordens
foram classificadas como não aplicáveis e permanecem bloqueadas. Passaram 294
testes Python. Evidência em `MSen/tests/TESTE_ITEM_14_7.md`.

### Item 14.8 — Revisão antes do processamento integral

Medir desempenho, estimar tempo e armazenamento para 50.063.860 combinações e
decidir se o processamento integral será sequencial, paralelo ou particionado.
Somente após esta revisão poderá ser proposta a retirada do limite de 5.000.

Estado: concluído em 2026-10-27. A geometria das 5.000 levou 2,8978 s e sua
extrapolação linear ficou em aproximadamente 8,1 h para o universo, sem outros
filtros ou I/O. Materializar as combinações como tuplas Python projetou 4,81 GB.
Foi escolhido processamento sequencial, particionado e em fluxo; paralelismo
somente após medir regras reais. O limite de 5.000 permanece. Passaram 297
testes Python. Evidência em `MSen/tests/TESTE_ITEM_14_8.md`. Etapa 14 concluída.

---

## ETAPA 15 — Critérios reais e ativação controlada

Objetivo: transformar informações históricas em critérios auditáveis, um de
cada vez, sem confundir detecção de padrão com autorização para excluir uma
combinação. Nenhum critério será ativado automaticamente.

As subetapas devem produzir uma entrega verificável e aguardar autorização para
a seguinte. Varreduras históricas não serão agrupadas com implementação ou
alteração de configuração, mantendo ciclos de trabalho pequenos.

### Item 15.1 — Inventário dos critérios disponíveis

Ler grupos, padrões cadastrados, funções Python e estatísticas atuais. Apresentar
código, nome, grupo, função, ocorrências, percentual e estado de implementação.
Apenas leitura; não corrigir nem ativar nada.

Estado: concluído em 2026-10-27. Foram encontrados 3 grupos, 9 padrões e 9
detectores, sem cadastro ou função órfã. Os percentuais foram calculados sobre
3.069 resultados. Duas divergências textuais foram apenas registradas, sem
correção. Evidência em `MSen/tests/TESTE_ITEM_15_1.md`.

### Item 15.2 — Contrato de detecção e exclusão

Separar formalmente a função que detecta o padrão da política que decide se ele
pode excluir. Fixar denominador histórico, arredondamento, significado de `menor
ou igual`, dados insuficientes e comportamento quando a estatística estiver
ausente.

Estado: concluído em 2026-10-27. Detector, política e modo foram separados; o
denominador, precisão, operador inclusivo, modos e falha conservadora foram
definidos. Nenhuma tolerância ou exclusão foi aprovada. Evidência em
`MSen/tests/TESTE_ITEM_15_2.md` e contrato em
`docs/CONTRATO_DETECCAO_EXCLUSAO.md`.

### Item 15.3 — Escolha do critério piloto

Apresentar candidatos do inventário e escolher somente um com autorização do
usuário. Registrar código, explicação, função e motivo. O exemplo de 3% não
constitui aprovação automática.

Estado: concluído em 2026-10-27. O usuário aprovou PD_003 como piloto de teste,
por combinar baixa ocorrência, regra simples, exclusividade e testes existentes.
A escolha não aprova tolerância nem exclusão. Análise em
`docs/SELECAO_CRITERIO_PILOTO.md` e evidência em
`MSen/tests/TESTE_ITEM_15_3.md`.

### Item 15.4 — Casos de aceitação do piloto

Montar tabela curta com combinações que detectam, não detectam e representam
limites ou ambiguidades. Obter aprovação antes de alterar código.

Estado: concluído em 2026-10-27. O usuário aprovou 8 casos positivos, 6
negativos e 6 entradas inválidas. A classificação usa o maior bloco consecutivo,
não une 60/01, não soma blocos separados e é exclusiva. Documento em
`docs/CASOS_ACEITACAO_PD003.md` e evidência em
`MSen/tests/TESTE_ITEM_15_4.md`.

### Item 15.5 — Implementação isolada do detector piloto

Reutilizar a função existente se corresponder ao contrato; caso contrário,
corrigi-la com docstring em português. Criar testes dos casos aprovados. O
detector continuará desconectado do funil.

Estado: concluído em 2026-10-27. O detector existente passou nos 20 casos
aprovados, sem divergências, e os positivos foram exclusivos de PD_003. Não foi
necessário alterar o código de produção. Foi criada saída auditável por caso e
registrado o requisito de validação visual final. Passaram 299 testes Python.
Evidência em `MSen/tests/TESTE_ITEM_15_5.md`.

### Item 15.6 — Reconciliação com o histórico

Executar o detector nos 3.069 resultados e comparar ocorrências, intervalos,
intervalo médio e desvio-padrão dos intervalos com o banco. Mediana dos
resultados pertence aos critérios estatísticos, não aos padrões. Investigar
divergências sem atualizar estatísticas silenciosamente.

Estado: concluído em 2026-10-27. O detector encontrou os concursos 186, 509,
2052, 2789 e 2908. Quantidade 5, média 680,500000 e desvio populacional
545,478460 coincidiram exatamente com o banco. Mediana foi corretamente mantida
fora desta categoria. Nenhuma escrita foi feita.
Evidência em `MSen/tests/TESTE_ITEM_15_6.md`.

### Item 15.7 — Política piloto em modo sombra

Conectar o detector ao adaptador apenas para informar o que seria excluído, sem
remover combinações. Registrar ocorrência histórica, tolerância proposta, valor
observado e justificativa.

Estado: concluído em 2026-10-27. A política sombra de PD_003 registra detector,
histórico, percentual, operador, hipótese e motivo, mas sempre aprova no funil.
Com a hipótese não aprovada de 3%, PD_003 é apenas marcado; evidência inválida
falha sem excluir. Passaram 305 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_15_7.md`.

### Item 15.8 — Simulação sombra com 5.000 combinações

Apresentar quantidade e percentual marcados, saldo hipotético e tempo. Repetir
com segunda semente apenas para verificar sensibilidade, sem tratar a amostra
como prova do universo.

Estado: concluído em 2026-10-27. Com a hipótese não aprovada de 3%, a semente
20261027 marcou 11/5.000 (0,22%) e a semente 42 marcou 5/5.000 (0,10%). Todas as
10.000 combinações foram realmente aprovadas e nenhuma foi excluída. A variação
foi registrada como sensibilidade amostral, não conclusão sobre o universo.
Passaram 309 testes Python. Evidência em `MSen/tests/TESTE_ITEM_15_8.md`.

### Item 15.9 — Autorização da regra de exclusão

Apresentar histórico e simulação. O usuário deverá aprovar explicitamente
detector, operador, tolerância e comportamento quando o dado estiver ausente.
Sem isso, o critério permanecerá em modo sombra.

Estado: concluído em 2026-10-27. O usuário aprovou detector PD_003, operador
inclusivo `<=`, tolerância de 3% e falha conservadora que não exclui com dado
ausente ou inconsistente. A autorização vale somente para a ativação protegida
de 5.000 no Item 15.10. Documento em `docs/DECISAO_REGRA_PD003.md` e evidência
em `MSen/tests/TESTE_ITEM_15_9.md`.

### Item 15.10 — Ativação controlada do piloto

Após o Item 15.9, permitir o critério na configuração, executar as mesmas 5.000
e comprovar que recebido = excluído + aprovado. A trava integral permanece.

Estado: concluído em 2026-10-27. Somente PD_003 foi ativado na amostra com
semente 20261027. Foram recebidas e avaliadas 5.000 combinações, 11 foram
excluídas e 4.989 aprovadas, fechando `5.000 = 11 + 4.989`. O processamento
integral permanece bloqueado e passaram 316 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_15_10.md`.

### Item 15.11 — Ciclo dos demais padrões históricos

Repetir os Itens 15.3 a 15.10 para cada padrão, um por vez. Padrões relacionados
aparecerão agrupados no relatório, mas manterão códigos e contadores separados.
Cada ativação exigirá autorização própria.

Estado parcial em 2026-10-27: PD_002 foi selecionado e preparado como próximo
padrão. Seus casos exclusivos passaram, e o histórico reconciliou 92 ocorrências
em 3.069 resultados (`2,997719%`), intervalo médio `33,527473` e desvio-padrão
`33,637806`. Em sombra, marcou 162/5.000 na semente principal e 142/5.000 na
alternativa. O usuário aprovou os quatro critérios e a ativação amostral passou
a excluir 11 combinações por PD_003 e 162 por PD_002, aprovando 4.827. O
fechamento é `5.000 = 11 + 162 + 4.827`; passaram 323 testes e a trava integral
permanece. Evidência em `MSen/tests/TESTE_ITEM_15_11.md`.

Segundo ciclo concluído em 2026-10-27: PD_006 reconciliou 4 ocorrências em
3.069 resultados (`0,130336%`), nos concursos 363, 844, 2066 e 2453. Em sombra,
marcou 5/5.000 na semente principal e 0/5.000 na alternativa, sem exclusões
reais. Após autorização dos quatro critérios, PD_006 foi ativado como terceiro
filtro e excluiu as 5 marcações, deixando saldo 4.822. O fechamento passou a
ser `5.000 = 11 + 162 + 5 + 4.822`; 327 testes passaram e a trava integral
permanece. Evidência em `MSen/tests/TESTE_ITEM_15_11_PD006.md`.

Terceiro ciclo concluído em 2026-10-27: PD_005 reconciliou 66 ocorrências em
3.069 resultados (`2,150538%`), intervalo médio `45,969231` e desvio-padrão
`42,006948`. Em sombra, marcou 113/5.000 na semente principal e 97/5.000 na
alternativa. Após autorização, foi ativado como quarto filtro: três marcações
já tinham sido excluídas antes, portanto PD_005 registrou 110 exclusões líquidas
e saldo 4.712. O fechamento é `5.000 = 11 + 162 + 5 + 110 + 4.712`; passaram
331 testes e a trava integral permanece. Evidência em
`MSen/tests/TESTE_ITEM_15_11_PD005.md`.

Quarto ciclo avaliado em 2026-10-27: PD_009 reconciliou 93 ocorrências em 3.069
resultados (`3,030303%`), intervalo médio `33,141304` e desvio-padrão
`35,099728`. O detector encontrou 177 e 154 combinações nas duas amostras, mas
a política marcou zero porque o percentual histórico é maior que a tolerância
de 3%. PD_009 não foi ativado. Evidência em
`MSen/tests/TESTE_ITEM_15_11_PD009.md`.

Fechamento em 2026-10-27: PD_001, PD_004, PD_007 e PD_008 foram recalculados e
coincidiram exatamente com o banco. Embora os detectores tenham encontrado
entre 1.361 e 3.393 combinações nas amostras, a política marcou zero porque os
quatro percentuais históricos excedem 3%. Com isso, os nove padrões concluíram
o ciclo: PD_003, PD_002, PD_006 e PD_005 ativos somente na amostra; os outros
cinco avaliados e não ativos. Evidência em
`MSen/tests/TESTE_ITEM_15_11_RESTANTES.md`.

### Item 15.12 — Critérios estatísticos

Tratar separadamente média, mediana, desvio-padrão e medidas futuras, repetindo
contrato, casos, histórico, sombra, simulação e autorização. A margem de 20%
continua apenas exemplificativa.

Estado parcial em 2026-10-27: média aritmética escolhida como primeiro piloto.
O histórico possui média das médias `30,515749` e desvio `6,659667`. A margem
exemplificativa de ±20% colocaria 1.151/3.069 resultados fora da faixa e foi
considerada agressiva demais. Como candidato ainda não aprovado, a faixa
histórica P01/P99 (`15,000000` a `45,886666`) deixaria 59 resultados históricos
fora (`1,922450%`) e marcaria 108/5.000 na amostra. Nenhuma política foi criada
ou ativada. Evidência em `MSen/tests/TESTE_ITEM_15_12_INVENTARIO_MEDIA.md`.

Após aprovação experimental, a faixa P01/P99 foi implementada somente em modo
sombra, com comparação estrita. Marcou 108/5.000 (`2,16%`) na semente principal
e 96/5.000 (`1,92%`) na alternativa, mantendo todas realmente aprovadas. Os
limites e suas vizinhanças foram testados. Evidência em
`MSen/tests/TESTE_ITEM_15_12_MEDIA_SOMBRA.md`.

O usuário autorizou a opção 3, ativação somente na amostra protegida. Como
quinto filtro, a média avaliou 4.712 combinações e excluiu 89; 19 das 108
marcações sombra já tinham sido removidas pelos padrões. O saldo final passou
a 4.623 e a contabilidade fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 4.623`. Passaram 346 testes e a trava
integral permanece.

Segundo piloto iniciado em 2026-10-27: desvio-padrão populacional das seis
dezenas. O histórico tem média `15,556645`; ±20% atingiria 1.197/3.069 e não é
recomendado. A faixa candidata P01/P99 é `7,145546` a `22,774694`, deixando 62
históricos fora (`2,020202%`) e marcando 132/5.000 na amostra. Nenhuma política
foi criada. Evidência em `MSen/tests/TESTE_ITEM_15_12_INVENTARIO_DESVIO.md`.

Após aprovação experimental, a faixa do desvio foi implementada somente em
sombra. Marcou 132/5.000 (`2,64%`) na semente principal e 122/5.000 (`2,44%`)
na alternativa, sem exclusões reais. Fronteiras e cálculo populacional foram
testados. Evidência em `MSen/tests/TESTE_ITEM_15_12_DESVIO_SOMBRA.md`.

O usuário autorizou a ativação apenas para testar a engrenagem. Como sexto
filtro, o desvio recebeu 4.623 combinações e excluiu 95; 37 das 132 marcações
sombra já haviam sido removidas antes. O saldo final passou a 4.528 e a
contabilidade fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 4.528`. Passaram 353 testes. Os limites
continuam experimentais e o processamento integral permanece bloqueado.

Terceiro piloto estatístico iniciado em 2026-10-27: mediana das seis dezenas.
O histórico possui média das medianas `30,677908`; ±20% atingiria 1.678/3.069 e
foi descartado como agressivo. A faixa candidata P01/P99 é `10,5` a `50,5`,
deixando 57 históricos fora (`1,857283%`) e marcando 92/5.000 na amostra.
Nenhuma política foi criada. Evidência em
`MSen/tests/TESTE_ITEM_15_12_INVENTARIO_MEDIANA.md`.

Após aprovação experimental, a mediana foi implementada somente em sombra.
Marcou 92/5.000 (`1,84%`) na semente principal e 91/5.000 (`1,82%`) na
alternativa, sem exclusões reais. Fronteiras e cálculo foram testados.
Evidência em `MSen/tests/TESTE_ITEM_15_12_MEDIANA_SOMBRA.md`.

O usuário autorizou a ativação apenas para teste. Como sétimo filtro, a mediana
recebeu 4.528 combinações e excluiu 44; 48 das 92 marcações sombra já tinham
sido removidas antes. O saldo final passou a 4.484 e a contabilidade fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 44 + 4.484`. Passaram 362 testes; os
limites permanecem experimentais e a trava integral continua.

### Item 15.13 — Critérios geométricos

Propor faixas para extensão, perímetro, área, regiões e centro de gravidade com
base nas distribuições históricas. Validar desenho e cálculo antes da sombra;
cada medida seguirá autorização individual.

Estado parcial em 2026-10-27: extensão aberta escolhida como primeiro piloto.
O histórico tem média `18,398295`; ±20% atingiria 1.523/3.069 e foi considerado
agressivo. A faixa candidata P01/P99 é `8,650282` a `32,300058`. Reaplicando os
limites efetivamente aprovados, arredondados a seis casas, ficam 64 históricos
fora (`2,085370%`) e 106/5.000 na amostra. A correção substitui a estimativa
bruta anterior de 61/102. Evidência em
`MSen/tests/TESTE_ITEM_15_13_INVENTARIO_EXTENSAO.md`.

Após aprovação, a extensão foi implementada somente em sombra. Marcou
106/5.000 (`2,12%`) na semente principal e 115/5.000 (`2,30%`) na alternativa,
sem exclusões reais. Evidência em
`MSen/tests/TESTE_ITEM_15_13_EXTENSAO_SOMBRA.md`.

Depois de autorização específica, a extensão foi ativada como oitavo filtro
somente na amostra protegida. Recebeu 4.484 combinações, excluiu 75 e deixou
4.409 aprovadas; 31 das 106 marcações sombra já haviam sido removidas pelos
sete filtros anteriores. A contabilidade fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 44 + 75 + 4.409`. Passaram 369 testes;
o modo integral continua bloqueado e o banco não foi escrito. Evidência em
`MSen/tests/TESTE_ITEM_15_13_EXTENSAO_ATIVA.md`.

### Item 15.14 — Comparação da ordem dos filtros

Quando houver pelo menos dois critérios aprovados, usar a mesma amostra e
semente em ordens diferentes. Comparar exclusões atribuídas, avaliações evitadas
e tempo, contando cada combinação no primeiro critério que a excluir.

Concluído em 2026-10-27 com três ordens. Todas preservaram exatamente as mesmas
4.409 combinações aprovadas. A ordem atual realizou 37.985 avaliações; a de
históricos frequentes primeiro, 37.569; e a de geometria/estatísticas primeiro,
37.315. Como o custo das funções difere, a menor contagem não foi sempre a mais
rápida. A ordem padrão foi mantida. Evidência em
`MSen/tests/TESTE_ITEM_15_14_COMPARACAO_ORDENS.md`.

### Item 15.15 — Quadro visual do ensaio

Expor o quadro por API e criar página compacta com total inicial, uma linha por
critério, exclusões, saldo, percentual e tempo. Usar rolagem interna e evitar
consumo vertical permanente no menu.

Incluir uma saída de validação das funções, mostrando por caso a combinação,
resultado esperado, resultado obtido, motivo e conformidade. O usuário deverá
conseguir conferir aprovações e reprovações antes de autorizar filtros reais.

Concluído em 2026-10-27. A página compacta `/screener.html` apresenta o funil
de oito filtros e 30 casos reproduzíveis para validação humana. A escolha do
resultado esperado calcula conformidade ou divergência somente no navegador,
sem persistir ou alterar regras. HTML, CSS e JavaScript estão separados; as
tabelas usam rolagem interna. Evidência em
`MSen/tests/TESTE_ITEM_15_15_QUADRO_VISUAL.md`.

### Item 15.16 — Regressão e fechamento

Executar testes Python, API, frontend, Chrome e PostgreSQL proporcionais ao que
foi ativado. Confirmar a trava integral, documentar aprovados e pendentes e
preparar commit somente mediante autorização.

Concluído em 2026-10-27: 379 testes Python, 24 JavaScript e 11 fluxos no Google
Chrome passaram. O fluxo Chrome real confirmou 5.000 recebidas, 591 excluídas,
4.409 aprovadas, oito filtros e 30 casos de validação. Não houve acesso ao
banco; o processamento integral permanece bloqueado e nenhum servidor ficou
aberto. Evidência em `MSen/tests/TESTE_ITEM_15_16_FECHAMENTO.md`.

---

## Próximo item proposto

Iniciar a Etapa 16 pela definição formal do contrato de classificação por grupo.
A Etapa 8/PythonAnywhere permanece adiada.

---

## Etapas 16 a 21 — perfis, screener, backtests e auditoria

As subetapas abaixo foram planejadas para sessões curtas, preferencialmente de
4 a 8 minutos. Cada subetapa deverá terminar com teste proporcional, atualização
da continuidade e pedido de autorização para a seguinte. Nenhuma etapa autoriza
automaticamente a próxima.

### Etapa 16 — classificação dos resultados por grupos de padrões

Objetivo: registrar, para cada resultado real e grupo, o subgrupo identificado
pela função classificadora e produzir os percentuais históricos.

#### 16.1 — Contrato da classificação

- Confirmar o nome `resultado_classificacao_padrao`.
- Definir se cada grupo terá classes mutuamente exclusivas.
- Definir o estado `SEM_CORRESPONDENCIA` para a diferença até 100%, sem criar
  automaticamente um novo padrão.
- Definir o denominador oficial dos percentuais e a exibição de denominadores
  alternativos.
- Documentar exemplos de entrada, classificação e casos ambíguos.
- Teste: revisar o contrato com casos manuais antes de criar DDL.

Executado em 28/10/2026. O levantamento confirmou exclusividade nos nove
padrões atuais e identificou a diferença `SEM_CORRESPONDENCIA` em cada grupo.
Contrato proposto em `docs/CONTRATO_CLASSIFICACAO_GRUPOS.md` e evidência em
`MSen/tests/TESTE_ITEM_16_1.md`. Após os esclarecimentos, o contrato conceitual
foi aprovado com seleção de padrões raros por limite configurável. Nenhum DDL
foi criado.

#### 16.2 — DDL e migração isolada

- Criar migração versionada da nova tabela.
- Incluir chaves estrangeiras para `resultados`, `padroes_grupo` e
  `padroes_subgrupo`.
- Incluir unicidade, versão de cálculo, data de cálculo e índices de consulta.
- Atualizar o esquema consolidado sem executar ainda no banco local principal.
- Teste: validar sintaxe e ordem da migração em estrutura temporária.

Executado em 28/10/2026. Foi criada a migração versionada `008` com uma
classificação por resultado e grupo, estados mutuamente coerentes, referências
ao resultado, grupo e padrão pertencente ao grupo, versão, data e índice de
contagem. O esquema consolidado foi atualizado; passaram 13 testes direcionados
e 384 testes na regressão Python. O database `games` não recebeu a migração.
Evidência em `MSen/tests/TESTE_ITEM_16_2.md`.

#### 16.3 — Teste PostgreSQL da migração

- Aplicar a migração em database temporário.
- Confirmar primeira execução, segunda execução idempotente, restrições e
  rollback em falha.
- Confirmar remoção do database temporário.

Executado em 28/10/2026 no database efêmero `games_test_7_1_163`. A versão
`008` foi a única aplicada sobre a estrutura `001`–`007`; a segunda execução
reconheceu todas as versões sem reaplicá-las. Os dois estados válidos foram
aceitos, cinco violações foram rejeitadas, a cascata do resultado funcionou e
uma migração defeituosa sofreu rollback completo. O database temporário foi
removido e a auditoria final retornou `[]`. O `games` não foi alterado.
Evidência em `MSen/tests/TESTE_ITEM_16_3.md`.

#### 16.4 — Modelo e repositório Python

- Criar o modelo imutável da classificação.
- Criar operações de inserir/atualizar, listar por resultado e listar por grupo.
- Manter SQL restrito ao repositório.
- Teste: unitário e integração em PostgreSQL temporário.

Executado em 28/10/2026. Foram criados o modelo imutável, os dois estados
tipados e o repositório exclusivo de classificações. O salvamento insere ou
atualiza pelo par resultado/grupo, preservando a identidade, e as consultas
listam por resultado ou grupo. Passaram oito testes direcionados, a integração
real no database temporário e 392 testes de regressão. O database efêmero foi
removido e o `games` não foi alterado. Evidência em
`MSen/tests/TESTE_ITEM_16_4.md`.

#### 16.5 — Classificador de um grupo piloto

- Usar o grupo de dezenas sequenciais como piloto.
- Classificar pelo maior grupo sequencial ou registrar `SEM_CORRESPONDENCIA`.
- Garantir exatamente uma classificação por resultado nesse grupo.
- Registrar descrição do que cada função faz.
- Teste: casos aprovados manualmente, fronteiras e dezenas fora de ordem.

Executado em 28/10/2026. O classificador de `PG_001` passou a produzir uma
classe exclusiva pelo maior bloco e `SEM_CORRESPONDENCIA` quando o maior bloco
tem tamanho um. A mesma análise central alimenta os detectores existentes e
gera evidência estruturada para auditoria. Os casos de dois, três, quatro,
cinco e seis, ausência, empate, limites 01/60 e entrada fora de ordem foram
validados. Passaram 18 testes direcionados e 398 testes de regressão. Nenhum
banco foi acessado. Evidência em `MSen/tests/TESTE_ITEM_16_5.md`.

#### 16.6 — Recálculo histórico do grupo piloto

- Varrer os resultados reais em ordem de concurso.
- Persistir classificações de forma transacional e idempotente.
- Permitir recalcular quando mudar a versão da função.
- Teste: subconjunto controlado e depois histórico completo local.

Executado em 28/10/2026. O serviço transacional lê o histórico paginado,
resolve grupo e padrões pelos códigos estáveis, classifica e grava de forma
idempotente. Uma falha controlada na terceira gravação comprovou rollback
integral. No clone dos 3.069 resultados, foram obtidos 1.192 `PD_001`, 92
`PD_002`, cinco `PD_003` e 1.780 `SEM_CORRESPONDENCIA`; o total fechou em 3.069
e a segunda execução preservou todas as identidades. Passaram 400 testes. Os
databases temporários foram removidos e o `games` não foi alterado. Evidência
em `MSen/tests/TESTE_ITEM_16_6.md`.

#### 16.7 — Perfil de contagens e percentuais

- Contar ocorrências por subgrupo.
- Calcular percentual sobre todos os resultados e sobre os classificados.
- Reconciliar soma das classes com o total de resultados.
- Atualizar `num_oco` consolidado sem perder a trilha individual.
- Calcular a diferença `SEM_CORRESPONDENCIA` sem cadastrá-la como padrão.
- Receber um limite percentual experimental e indicar quais padrões ficaram
  estritamente abaixo dele, sem ativar ainda o screener.
- Teste: contagens conhecidas e fechamento em 100% somando padrões e
  `SEM_CORRESPONDENCIA`.

Executado em 28/10/2026. O perfil usa todos os resultados como denominador
oficial e mostra também o percentual entre os classificados. O operador de
raridade é estritamente `<`; `SEM_CORRESPONDENCIA` fecha os 100%, mas nunca é
selecionado. Com limite experimental de 10% no clone histórico, `PD_002`
(2,997719%) e `PD_003` (0,162920%) foram indicados, sem ativação no screener.
O catálogo foi sincronizado com estatísticas completas e reconciliado com as
classificações. Passaram cinco testes unitários, dois fluxos PostgreSQL e 403
testes de regressão. Evidência em `MSen/tests/TESTE_ITEM_16_7.md`.

#### 16.8 — API de perfil por grupo

- Expor grupo, subgrupos, contagens, percentuais, intervalo e versão.
- Permitir data ou concurso de corte para uso futuro no backtest.
- Teste: contrato JSON, corte histórico e erros seguros.

Executado em 28/10/2026. Foi criado o endpoint somente leitura
`GET /api/grupos-padroes/PG_001/perfil`, com limite de raridade e cortes
inclusivos por concurso ou data. A resposta expõe amostra, versões, contagens,
percentuais e estatísticas, mantendo `ativa_no_screener=false`. Doze testes
direcionados e a integração Flask/PostgreSQL confirmaram o perfil completo de
3.069 resultados e dois cortes de 100 resultados sem alterar o catálogo.
Passaram 410 testes de regressão. Evidência em
`MSen/tests/TESTE_ITEM_16_8.md`; contrato em `docs/API_PERFIS_PADROES.md`.

#### 16.9 — Tela compacta do perfil

- Mostrar a distribuição dos subgrupos na página de padrões.
- Usar tabela com rolagem interna e percentual claramente identificado.
- Não consumir nova linha permanente na navegação.
- Teste: JavaScript e Google Chrome.

Executado em 28/10/2026. A página de padrões recebeu um painel flutuante aberto
na própria linha do filtro, sem criar linha de navegação nem deslocar a grade.
Ele mostra resumo, corte, quatro classes, percentuais, estatísticas e indicação
de raridade em tabela com rolagem interna, sempre informando que o screener está
inativo. Passaram 24 testes JavaScript, 12 fluxos no Google Chrome e 410 testes
Python. Nenhum banco foi alterado. Evidência em
`MSen/tests/TESTE_ITEM_16_9.md`.

#### 16.10 — Regressão e fechamento da classificação

- Executar testes Python, PostgreSQL temporário, API e Chrome.
- Conferir que resultados históricos não foram alterados.
- Preparar commit somente mediante autorização.

Executado em 28/10/2026. Após backup validado de 226.601 bytes e SHA-256
registrado, somente a migração `008` foi aplicada ao `games`. Foram persistidas
3.069 classificações sem alterar resultados, frequências ou análises
geométricas. Uma instância antiga que dividia a porta 5050 foi removida; o
servidor atualizado e o Chrome real confirmaram API, perfil completo e corte.
Passaram 410 testes Python, 24 JavaScript, 12 fluxos Chrome e três fluxos
integrados. Não restou database temporário. Evidência em
`MSen/tests/TESTE_ITEM_16_10.md`.

Estado da Etapa 16: concluída localmente e operacional. O screener continua sem
exclusão pelos novos perfis. Commit e push dependem de autorização expressa.


### Etapa 17 — perfis estatísticos, geométricos e distribuições

Objetivo: construir as referências históricas usadas nas faixas e mostrá-las
simultaneamente em gráficos compreensíveis.

#### 17.1 — Catálogo dos parâmetros

- Relacionar soma, média, mediana, desvio-padrão, extensão, perímetro, área,
  quantidade de regiões e centro de gravidade X/Y.
- Registrar unidade, precisão, fórmula e fonte de cada parâmetro.
- Marcar soma e média como informações linearmente equivalentes.
- Teste: inventário comparado com as colunas e funções existentes.
- Estado: **implementado em 2026-10-28**. O catálogo técnico está em
  `docs/CATALOGO_PARAMETROS_ANALISE.md`; nenhuma regra do screener foi ativada.

#### 17.2 — Serviço de janela histórica

- Selecionar todos os resultados ou somente os anteriores a uma data/concurso.
- Proibir inclusão do próprio resultado avaliado e de resultados futuros.
- Teste: cortes inicial, intermediário e final.
- Estado: **implementado em 2026-10-28** com cortes exclusivos e contrato em
  `docs/CONTRATO_JANELA_HISTORICA.md`; nenhuma integração foi ativada ainda.

#### 17.3 — Perfil estatístico genérico

- Calcular quantidade, média, desvio-padrão, mínimo, máximo e distribuição.
- Produzir limites por percentual da média ou multiplicador de desvio-padrão.
- Permitir margens inferior e superior diferentes.
- Teste: conjunto controlado com cálculos manuais.
- Estado: **implementado em 2026-10-28** como serviço puro baseado em
  `Decimal`, ainda sem integração com banco, API, interface ou screener.

#### 17.4 — Perfis geométricos

- Aplicar o perfil genérico à tabela `analise_geometrica_resultado`.
- Tratar centro de gravidade X e Y separadamente na primeira versão.
- Registrar valores ausentes ou cálculos impossíveis sem substituição silenciosa.
- Teste: figuras controladas e reconciliação com resultados persistidos.
- Estado: **implementado em 2026-10-28** sobre os modelos persistidos, com X/Y
  separados e ausência explícita; ainda sem API, interface ou screener.

#### 17.5 — API das distribuições

- Expor classes do histograma, frequências, curva normal de referência, média,
  desvio e limites.
- Informar intervalo histórico e tamanho da amostra.
- Teste: JSON reproduzível e proteção contra intervalos vazios.
- Estado: **implementado em 2026-10-28** como API somente leitura, com curva
  normal identificada apenas como referência e screener inativo.

#### 17.6 — Painel com todos os gráficos

- Mostrar todos os parâmetros simultaneamente em uma grade compacta.
- Exibir histograma real, curva normal, média, desvios e faixa configurada.
- Usar rolagem interna e reorganização responsiva.
- Teste: dados simulados e Google Chrome em larguras diferentes.
- Estado: **implementado em 2026-10-28** em página própria, com dez cartões,
  grade responsiva e rolagem interna; o screener continua inativo.

#### 17.7 — Janela de configuração das faixas

- Escolher percentual da média ou multiplicador do desvio-padrão.
- Configurar margens inferior e superior.
- Mostrar limites calculados antes de salvar.
- Não ativar exclusão automaticamente ao salvar o estudo.
- Teste: cálculos, validação de entrada e persistência da configuração.
- Estado: **implementado em 2026-10-28** como estudo persistido no navegador,
  com prévia obrigatória pela API e sem configuração operacional do screener.

#### 17.8 — Regressão e fechamento dos perfis

- Conferir cálculos Python, API, gráficos e Chrome.
- Preparar commit somente mediante autorização.
- Estado: **concluído em 2026-10-28** com regressões Python/JavaScript/Chrome e
  validação integrada local contra os 3.069 resultados reais. Commit pendente
  de autorização expressa.


### Etapa 18 — adaptação do screener aos três níveis

Objetivo: produzir o quadro consolidado solicitado e manter contabilidade exata
do funil.

Decisão de 28/10/2026: antes de construir API, persistência ou novas funções,
será criada uma tela de demonstração com valores fictícios. O usuário deverá
aprovar a organização e a quantidade de informações. A demonstração poderá usar
texto, blocos e detalhes expansíveis; não é obrigada a usar tabelas.

#### 18.0 — Protótipo visual sem backend

- Criar uma página provisória com dados fictícios e identificada como esboço.
- Mostrar todas as informações em um conjunto único e compacto.
- Usar três blocos principais: estatística, geometria e padrões.
- Exibir em cada bloco: entrada, exclusões, percentual, saldo e detalhes dos
  filtros.
- No bloco de padrões, mostrar limite de raridade, frequência de cada padrão e
  lista de padrões selecionados para exclusão.
- Mostrar total inicial, total excluído e total aprovado em destaque.
- Permitir abrir e fechar detalhes sem aumentar permanentemente a altura.
- Não chamar API, não gravar banco e não alterar o screener atual.
- Apresentar no Chrome para aprovação antes da subetapa 18.1.
- Estado: **implementado em 2026-10-28** em página separada, com dados
  fictícios reconciliados e sem chamada de API. Aguarda aprovação visual.

#### 18.1 — Contrato do novo funil

- Fixar a ordem inicial: estatística, geometria e grupos de padrões.
- Definir entrada, saída, motivo e evidência de cada filtro.
- Definir subtotais e percentuais sobre total inicial e saldo recebido.
- Teste: exemplos manuais de fechamento contábil.
- Estado: **implementado em 2026-10-28** como contrato hierárquico extensível,
  preservando o funil linear existente e ainda sem conectar filtros reais.

#### 18.2 — Fotografia reproduzível da configuração

- Registrar parâmetros, limites, grupos aceitos, ordem, versões e semente.
- Registrar limite de raridade, operador, intervalo histórico, denominador,
  frequências e lista de padrões excludentes calculada no início da execução.
- Garantir que uma execução passada possa ser reproduzida.
- Teste: serialização e checksum da configuração.
- Estado: **implementado em 2026-10-28** como fotografia canônica e imutável,
  incluindo a evidência histórica que determinou os padrões excludentes. Ainda
  não foi conectada a uma execução real nem persistida no banco.

#### 18.3 — Família estatística

- Conectar os parâmetros configurados ao funil.
- Evitar dupla exclusão por soma e média equivalentes.
- Contabilizar exclusões líquidas e subtotal.
- Teste: combinações dentro, fora e nos limites.
- Estado: **implementado em 2026-10-28** com soma/média em uma decisão única,
  mediana e desvio-padrão independentes, todos usando as funções matemáticas
  oficiais do sistema. Ainda não foi conectado à interface nem ao ensaio real.

#### 18.4 — Família geométrica

- Conectar extensão, perímetro, área, regiões e centro de gravidade.
- Interromper a combinação no primeiro filtro geométrico que a excluir.
- Teste: figuras controladas e subtotal geométrico.
- Estado: **implementado em 2026-10-28** com uma análise compartilhada por
  combinação e cinco decisões ordenadas. Centro ausente exige política explícita.
  Ainda não foi conectado à interface nem ao ensaio de 5.000 combinações.

#### 18.5 — Família de grupos de padrões

- Classificar a combinação uma vez por grupo.
- Comparar a classe encontrada somente com os padrões excludentes da fotografia.
- Preservar `SEM_CORRESPONDENCIA` no fechamento, sem transformá-la em exclusão.
- Teste: grupo sequencial real, múltiplos grupos e subtotal líquido.
- Calcular previamente as frequências no espaço amostral disponível.
- Selecionar para exclusão os padrões estritamente abaixo do limite configurado.
- Comparar o subgrupo obtido com a fotografia dos padrões excludentes.
- Contabilizar exclusão pelo grupo, não por colunas fixas de padrões.
- Teste: grupos aceitos, rejeitados e `SEM_CORRESPONDENCIA` passando pelo funil.
- Estado: **implementado em 2026-10-28** montando um filtro de execução somente
  para cada grupo que já possua classificador Python integrado e testado. O
  classificador oficial PG_001 foi adaptado; cadastrar um grupo não cria código.

#### 18.6 — Quadro contábil consolidado

- Mostrar total possível ou tamanho da amostra.
- Mostrar filtros, exclusões, percentuais e subtotais das três famílias.
- Mostrar saldo entre famílias e total aprovado.
- Exigir: recebidas = exclusões líquidas + aprovadas.
- Teste: reconciliação automática obrigatória.
- Estado: **implementado em 2026-10-28** como representação serializável que
  valida cada transição de filtro e família. Distingue amostra do universo total
  e recusa relatórios adulterados. Ainda não foi conectado à interface.

#### 18.7 — Interface expansível do screener

- Exibir as três famílias em linhas compactas.
- Permitir expandir os filtros individuais sem ocupar espaço quando fechados.
- Mostrar total aprovado e percentuais finais.
- Teste: JavaScript, responsividade e Chrome.
- Estado: **implementado em 2026-10-28** em página própria ligada ao contrato
  serializado real, sem dados fictícios e sem API nesta subetapa. A execução
  permanece bloqueada até o ensaio protegido da 18.8.

#### 18.8 — Ensaio protegido de 5.000 e fechamento

- Executar o novo funil somente sobre a amostra protegida.
- Comparar resultados com a versão anterior e explicar divergências.
- Manter o processamento integral bloqueado.
- Preparar commit somente mediante autorização.
- Estado: **implementado em 2026-10-28** com API POST sem parâmetro de ampliação,
  fotografia SHA-256, comparação na mesma amostra e integração real no Chrome.
  O resultado é experimental e não substitui auditoria ou backtest.
- Estado: **implementado em 2026-10-28** com API POST sem parâmetro de ampliação,
  fotografia SHA-256, comparação na mesma amostra e integração real no Chrome.
  O resultado é experimental e não substitui auditoria ou backtest.


### Etapa 18-C — correção e ampliação do screener de padrões

Objetivo: corrigir o modelo de padrões após a validação experimental da Etapa
18, eliminar a classe indevida `SEM_CORRESPONDENCIA`, armazenar explicitamente
a incidência histórica de todos os padrões e aplicar no screener somente os
padrões cuja incidência seja estritamente menor que o limite configurado.

Esta etapa tem prioridade sobre as Etapas 19, 20 e 21. O backtest e a auditoria
continuam em espera. Cada subetapa exige autorização separada e foi limitada a
uma entrega curta, testável e reversível.

Regra aprovada:

```text
percentual_ocorrencia = quantidade_ocorrencias / total_sorteios * 100
padrão aplicado no screener quando percentual_ocorrencia < limite_configurado
```

Um padrão com zero ocorrências permanece cadastrado com quantidade `0` e
percentual `0%`. O complemento até 100% não é padrão, classe, ocorrência ou
critério e não deve ser persistido como `SEM_CORRESPONDENCIA`.

#### 18-C.1 — Contrato definitivo e inventário do impacto

- Registrar a distinção entre cálculo histórico e detector de combinação.
- Definir nomes semânticos: `quantidade_ocorrencias`, `total_sorteios` e
  `percentual_ocorrencia`.
- Preservar quantidade e denominador para auditoria, mas apresentar e consultar
  prioritariamente o percentual.
- Inventariar banco, Python, API, frontend, testes e documentos que ainda usam
  `SEM_CORRESPONDENCIA`.
- Teste: relatório somente de leitura provando o estado anterior à correção.
- Estado: **concluído em 29/10/2026**, sem escrita no banco. Foram localizados
  34 arquivos afetados e confirmadas 1.780 linhas `SEM_CORRESPONDENCIA`, contra
  1.289 classificações válidas. O contrato e a ordem segura estão registrados
  em `MSen/tests/TESTE_ITEM_18_C_1.md`.

#### 18-C.2 — Migração dos percentuais históricos

- Criar migração SQL versionada para armazenar `total_sorteios` e
  `percentual_ocorrencia` em todos os padrões cadastrados.
- Manter somente uma linha por padrão: cada recálculo atualizará e substituirá
  os valores estatísticos atuais nessa mesma linha, sem criar histórico ou um
  novo conjunto de registros.
- Renomear `num_oco` para `quantidade_ocorrencias`, se a análise de impacto da
  18-C.1 confirmar que a migração pode ser feita sem ambiguidade.
- Definir precisão decimal, faixa de 0% a 100% e consistência entre os três
  valores.
- Não apagar a quantidade: ela permite provar e recalcular o percentual.
- Teste: banco temporário, migração repetível e padrão com zero ocorrência.
- Estado: **concluído em 29/10/2026** pela migração `009`, aplicada ao banco
  local após teste temporário. Foram adicionados `total_sorteios` e
  `percentual_ocorrencia`; `num_oco` foi preservado por compatibilidade. Os
  campos novos permanecem nulos até o recálculo da 18-C.3. Passaram 492 testes.

#### 18-C.3 — Recálculo histórico de todos os nove padrões

- Executar as funções oficiais de `PD_001` a `PD_009` sobre os 3.069 resultados.
- Gravar quantidade, total de sorteios e percentual, inclusive quando for zero.
- Atualizar os campos do padrão existente; não inserir outra linha estatística.
- Manter intervalo médio e desvio-padrão já calculados.
- Teste: conferir manualmente amostras e reconciliar os nove totais com o banco.
- Estado: **concluído em 29/10/2026** após ensaio em restauração temporária e
  backup do `games`. As nove linhas foram atualizadas com denominador 3.069 e
  percentuais reconciliados; não houve inserção de linha. Passaram 492 testes.
  Resultado detalhado em `MSen/tests/TESTE_ITEM_18_C_3.md`.

#### 18-C.4 — Remoção do modelo `SEM_CORRESPONDENCIA`

- Remover os 1.780 registros indevidos após backup e conferência do alvo.
- Retirar enumeração, persistência, fotografia, API e apresentação dessa classe.
- Quando nenhum padrão estudado incidir sobre um resultado, não criar registro.
- O denominador histórico continuará sendo o total de sorteios, e não apenas os
  resultados que corresponderam a algum padrão.
- Teste: provar ausência da classe e preservação dos percentuais dos padrões.
- Estado: **concluído em 29/10/2026** pela migração `010`. Foram removidas
  exatamente 1.780 linhas indevidas e preservadas 1.289 ocorrências reais.
  Domínio, repositório, perfil, fotografia, API e frontend deixaram de tratar o
  complemento como classe. Passaram 493 testes Python, 35 JavaScript e 11 no
  Chrome. Relatório em `MSen/tests/TESTE_ITEM_18_C_4.md`.

#### 18-C.5 — Consulta parametrizada dos padrões raros

- Consultar somente padrões com função Python aprovada e
  `percentual_ocorrencia < limite_configurado`.
- Usar o percentual armazenado; quantidade e denominador serão evidências.
- Não usar `<=`: um padrão exatamente no limite não será aplicado.
- Recusar padrões sem detector, percentual desatualizado ou denominador
  incompatível com a fotografia histórica.
- Teste: limites 0%, exatamente iguais, abaixo e acima da configuração.

Estado: concluída em 2026-10-29. A consulta SQL parametrizada seleciona somente
os códigos com detector Python aprovado e percentual estritamente menor que o
limite. Com 10%, foram selecionados PD_002, PD_003, PD_005, PD_006 e PD_009.
A fronteira exata de PD_003 confirmou a regra `<`; fotografia com denominador
incompatível foi recusada. Passaram 8 testes direcionados e 496 testes Python.
Evidência em `MSen/tests/TESTE_ITEM_18_C_5.md`.

#### 18-C.6 — Configuração do limite de raridade

- Retirar o valor experimental fixo de 10% do serviço da Etapa 18.
- Criar uma única configuração validada para o limite percentual.
- Fotografar valor, operador `<`, data, intervalo histórico e versão do cálculo
  no início de cada execução.
- Teste: alteração da configuração muda a seleção dos padrões, mas não altera
  retroativamente uma execução já fotografada.

Estado: concluída em 2026-10-29. O limite único foi incluído em
`MSen/config/screener.toml`, validado como `Decimal` de 0% a 100% e ligado ao
ensaio extensível no lugar do valor fixo. O formato 2 da fotografia registra
data, operador `<`, limite, intervalo histórico, frequências, seleção e versões
dos cálculos. Uma mudança posterior do limite não altera fotografia anterior.
Passaram 500 testes Python. Evidência em `MSen/tests/TESTE_ITEM_18_C_6.md`.

#### 18-C.7 — Adaptadores dos três grupos disponíveis

- Integrar `PG_001`, `PG_002` e `PG_003` ao screener.
- Usar somente os detectores dos padrões selecionados pela consulta de raridade.
- Não executar detectores de padrões que estejam no limite ou acima dele.
- Interromper a combinação na primeira exclusão e contabilizar o padrão que a
  eliminou.
- Teste: combinações manuais para cada `PD_001` a `PD_009`.

Estado: concluída em 2026-10-29. Cada padrão raro selecionado produz um filtro
individual; detectores não selecionados não são executados, e a primeira
correspondência interrompe a combinação e contabiliza sua exclusão no padrão
responsável. Os nove detectores passaram por casos manuais. Na execução real de
5.000 combinações, a família recebeu 423, excluiu 9 por PD_002, PD_005 e PD_009
e entregou 414. Passaram 503 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_18_C_7.md`.

#### 18-C.8 — Relatório detalhado por padrão

- Manter o resumo compacto por família e grupo.
- Permitir expansão mostrando somente cada `PD_nnn` retornado pela consulta de
  raridade, com nome, grupo, incidência histórica, limite, combinações recebidas,
  correspondências, exclusões e saldo.
- A ausência de um grupo ou padrão significa que ele não foi selecionado pela
  consulta e, portanto, não foi aplicado ao screener.
- Teste: fechamento por padrão, grupo, família e total geral.

Estado: concluída e corrigida em 2026-10-29. O painel mantém o resumo compacto e
acrescenta somente os grupos e padrões retornados pela consulta de raridade,
com incidência, limite, avaliações, correspondências, exclusões e saldo. A
ausência já informa que o padrão não foi eleito e não foi aplicado. Com 10%,
foram exibidos PD_002, PD_003, PD_005, PD_006 e PD_009. Os grupos fecharam em
423→420, 420→417 e 417→414; a família fechou 423 = 9 + 414.
Passaram 505 testes Python, 35 JavaScript e 18 fluxos Chrome. Evidência em
`MSen/tests/TESTE_ITEM_18_C_8.md`.

#### 18-C.9 — API e interface da configuração

- Expor o limite efetivamente usado e a lista de padrões selecionados.
- Permitir configurar o limite sem editar código-fonte.
- Mostrar percentuais como informação principal; quantidades e denominador
  aparecerão nos detalhes de auditoria.
- Preservar o uso compacto de espaço vertical e horizontal.
- Teste: API, JavaScript e fluxo no Google Chrome.

Estado: concluída em 2026-10-29. A API aceita um limite de 0% a 100% por
execução, preserva o operador `<`, fotografa o valor efetivo e devolve somente a
lista selecionada. A interface possui campo compacto, mostra limite e padrões
usados e memoriza o último valor válido no navegador. Limites reais de 3% e 0%
foram reconciliados. Passaram 508 testes Python, 35 JavaScript e 18 fluxos
Chrome. Evidência em `MSen/tests/TESTE_ITEM_18_C_9.md`.

#### 18-C.10 — Ensaio protegido com 5.000 combinações

- Repetir a mesma amostra reproduzível de 5.000 combinações.
- Aplicar estatística, geometria e todos os padrões raros dos três grupos.
- Exibir somente os padrões eleitos pela consulta de raridade, com sua incidência
  histórica, o limite aplicado e quantas combinações eliminaram após receber o
  saldo dos níveis anteriores. A ausência significa que o padrão não foi eleito
  e não foi executado.
- Manter o processamento integral bloqueado.
- Teste: reconciliação automática e comparação com o ensaio anterior.

Estado: concluída em 2026-10-29. Duas execuções com a mesma semente produziram
o mesmo checksum e fecharam em 5.000 = 4.586 excluídas + 414 aprovadas.
Estatística entregou 2.001, geometria entregou 423 e os cinco padrões raros
eleitos dos três grupos excluíram 9, entregando 414. Somente PD_002, PD_003,
PD_005, PD_006 e PD_009 apareceram e foram executados. O processamento integral
permaneceu bloqueado. Passaram 508 testes Python, 35 JavaScript e 18 fluxos
Chrome. Evidência em `MSen/tests/TESTE_ITEM_18_C_10.md`.

#### 18-C.11 — Regressão, documentação e fechamento

- Executar testes Python, PostgreSQL temporário, API, JavaScript e Chrome.
- Atualizar funcionalidades, decisões e continuidade da IA.
- Registrar que novos padrões exigem função Python e recálculo histórico antes
  de poderem participar da consulta de raridade.
- Preparar commit e push somente mediante autorização específica.

Estado: concluída em 2026-10-29. Passaram 508 testes Python, 35 JavaScript, 18
fluxos Chrome simulados, três fluxos integrados Chrome/PostgreSQL e dois fluxos
Chrome contra a API local real. Uma restauração temporária recebeu as migrações
001–010, recalculou os nove padrões sobre 3.069 resultados e foi removida; a
auditoria final não encontrou databases temporários. Foram corrigidas duas
expectativas antigas dos testes integrados e atualizados funcionalidades,
decisões, critérios, plano e continuidade. Evidência em
`MSen/tests/TESTE_ITEM_18_C_11.md`. A Etapa 18-C está tecnicamente encerrada;
commit e push dependem de autorização específica.


### Etapa 18-D — consolidação do screener e separação da auditoria

Objetivo: eliminar a convivência confusa entre o funil antigo e o funil atual,
tornar o screener em três níveis a única interface oficial e transferir toda
ideia de validação humana para uma página própria de `Validação e auditoria`.

Decisão de 29/10/2026:

- o screener antigo de oito filtros e sua validação humana não permanecerão
  acessíveis na interface oficial;
- o funil em três níveis será chamado apenas de `Screener`, sem os qualificadores
  `novo`, `atual` ou `extensível`;
- a página oficial do screener continuará executando somente a amostra protegida
  de 5.000 combinações;
- `Validação e auditoria` terá item próprio no menu e página inicialmente vazia,
  apenas com identificação e aviso de funcionalidade em construção;
- os métodos de validação e auditoria continuarão reservados para a Etapa 20;
- nenhuma função provisória de validação do screener antigo será transportada
  automaticamente para a futura auditoria.

Cada subetapa exige autorização separada. A Etapa 19 permanece em espera e a
Etapa 20 não é iniciada pela simples criação de sua página vazia.

#### 18-D.1 — Inventário e contrato definitivo de consolidação

- Inventariar páginas, scripts, APIs, testes, menus e documentos dos screeners
  antigo, protótipo e atual.
- Definir o destino de cada elemento: manter, migrar, redirecionar ou remover.
- Confirmar que nenhuma função ainda necessária existe somente no screener
  antigo antes de retirá-lo.
- Teste: relatório de impacto sem modificar comportamento, banco ou rotas.

Estado: concluída em 2026-10-29, somente por inspeção. Foram confirmadas três
apresentações: screener antigo, protótipo fictício e funil real em três níveis.
A tela, a validação humana e a API antiga podem ser retiradas, mas os adaptadores
e políticas do primeiro funil devem permanecer como referência interna porque o
serviço atual os usa na comparação sobre a mesma amostra. O destino de páginas,
scripts, rotas, testes e documentos está registrado em
`MSen/tests/TESTE_ITEM_18_D_1.md`. Nenhum comportamento ou dado foi alterado.

#### 18-D.2 — Screener em três níveis como página oficial

- Fazer `/screener.html` apresentar diretamente o funil atual em três níveis.
- Usar somente os nomes `Screener` e `Funil em três níveis` onde for necessário
  explicar sua estrutura.
- Retirar da interface os links `Abrir novo funil` e `Screener atual`.
- Preservar limite de raridade, amostra de 5.000, fotografia, reconciliação e
  relatório por grupo e padrão.
- Teste: menu abre uma única página e a execução mantém o resultado validado.

Estado: concluída em 2026-10-29. `/screener.html` apresenta diretamente o funil
real em três níveis, com o nome único `Screener` e sem links `Abrir novo funil`
ou `Screener atual`. A validação provisória não aparece mais na página oficial;
os artefatos legados permanecem fisicamente preservados até 18-D.5 e 18-D.6.
Passaram 7 testes direcionados da API, 35 JavaScript, 18 fluxos Chrome e um
fluxo Chrome contra a API real, que reconciliou 5.000 = 4.586 + 414. Evidência
em `MSen/tests/TESTE_ITEM_18_D_2.md`.

#### 18-D.3 — Estado coerente dos controles

- Deixar `Abrir detalhes` e `Fechar detalhes` desabilitados antes da primeira
  execução e durante o processamento.
- Habilitá-los somente quando existirem blocos expansíveis carregados.
- Exibir mensagens claras para execução, sucesso e erro, sem botão aparentemente
  inoperante.
- Teste: estados inicial, processando, concluído e falha de API no Chrome.

Estado: concluída em 2026-10-29. Os controles de detalhes ficam desabilitados
antes da primeira execução e durante o processamento, e são habilitados somente
após conteúdo válido ser carregado. Falha inicial mantém detalhes indisponíveis;
falha posterior preserva acesso ao último resultado válido. Passaram 35 testes
JavaScript e dois fluxos Chrome direcionados cobrindo todos os estados.
Evidência em `MSen/tests/TESTE_ITEM_18_D_3.md`.

#### 18-D.4 — Página vazia de Validação e auditoria

- Criar item horizontal `Validação e auditoria` no menu oficial.
- Criar `/auditoria.html` com a barra de navegação comum, botão Voltar, título e
  aviso de que os métodos serão desenvolvidos posteriormente.
- Não criar formulário, cálculo, tabela, API ou persistência nesta subetapa.
- Preservar consumo mínimo de espaço vertical e horizontal.
- Teste: navegação de ida e volta e página compacta no Chrome.

Estado: concluída em 2026-10-29. O item horizontal `Validação e auditoria` foi
incluído nas páginas oficiais e `/auditoria.html` foi criada somente com
navegação, título e aviso de construção. Não há formulário, tabela, cálculo,
API ou persistência. Passaram 36 testes JavaScript e 11 fluxos Chrome do
conjunto principal, incluindo ida, volta e largura de 700 px. Evidência em
`MSen/tests/TESTE_ITEM_18_D_4.md`.

#### 18-D.5 — Remoção da validação humana provisória

- Remover da interface a tabela `Validação humana`, seus seletores e a lógica de
  conformidade apenas local.
- Remover dados de validação provisórios da resposta antiga quando nenhum outro
  consumidor legítimo depender deles.
- Garantir que a remoção não alcance o futuro modelo planejado da Etapa 20.
- Teste: busca de referências e regressão da API.

**Concluída em 2026-10-29.** A rota antiga deixou de aceitar
`limite_validacoes` e de produzir a coleção `validacoes`; o montador legado e
seu JavaScript também não contêm mais casos, seletores ou cálculo local de
conformidade. A página reservada à Etapa 20 não foi alterada. Passaram 505
testes Python, 36 testes JavaScript e 19 fluxos Chrome. Evidência em
`MSen/tests/TESTE_ITEM_18_D_5.md`.

#### 18-D.6 — Retirada segura do screener legado e do protótipo

- Remover ou redirecionar páginas, JavaScript e rotas exclusivas do funil antigo
  depois da confirmação do inventário.
- Retirar o protótipo fictício da navegação e dos artefatos de produção; manter
  apenas evidência histórica que ainda seja útil à documentação.
- Atualizar testes para possuir um único contrato oficial do screener.
- Teste: nenhuma URL interna aponta para tela antiga e nenhuma função de
  produção fica órfã.

**Concluída em 2026-10-29.** Permanecem publicados somente `screener.html` e
`POST /api/screener/quadro`. Foram retirados a segunda página executável, o
protótipo fictício, o JavaScript antigo, a rota GET anterior e o montador
exclusivo daquele quadro. O núcleo matemático do primeiro funil foi preservado
porque ainda alimenta a comparação interna do relatório oficial. Passaram 503
testes Python, 32 testes JavaScript, 18 fluxos Chrome e 5 testes integrados
(3 aprovados e 2 ignorados por dependerem do PostgreSQL local). Evidência em
`MSen/tests/TESTE_ITEM_18_D_6.md`.

#### 18-D.7 — Regressão, documentação e fechamento

- Executar testes Python, API, JavaScript e Google Chrome.
- Executar o fluxo real de 5.000 contra o servidor local e confirmar o mesmo
  fechamento de referência, salvo mudança expressamente aprovada.
- Atualizar funcionalidades, decisões, critérios e continuidade da IA.
- Preparar commit e push somente mediante autorização específica.

**Concluída em 2026-10-29.** A documentação operacional passou a registrar uma
única página e uma única API oficiais; documentos do protótipo foram marcados
como históricos, registros duplicados de continuidade foram removidos e as
funcionalidades e decisões foram reconciliadas. O Chrome confirmou novamente o
fechamento das 5.000 combinações: 4.586 excluídas e 414 aprovadas, com o funil
anterior aprovando 4.409 apenas como comparação interna. Passaram 503 testes
Python, 32 JavaScript, 18 Chrome e 5 integrados (3 aprovados e 2 ignorados por
dependerem do PostgreSQL local). A Etapa 18-D está encerrada; commit e push
dependem de autorização específica. Evidência em
`MSen/tests/TESTE_ITEM_18_D_7.md`.


### Etapa 19 — mecanismo de backtest sem informação futura

Objetivo: avaliar se os critérios teriam preservado resultados reais ainda
desconhecidos no ponto histórico simulado.

Estado: **em espera por decisão expressa do usuário em 2026-10-28**. Não iniciar
planejamento detalhado, implementação, preparação de dados ou testes de backtest
até nova autorização. O encerramento da Etapa 18 não autoriza esta etapa.

Estado decidido em 28/10/2026: etapa formalmente adiada. O backtest somente
será desenvolvido quando cadastro, classificações, perfis, configurações,
screener e auditoria manual estiverem operacionais e validados. A numeração é
mantida para preservar o planejamento, mas a Etapa 20 poderá ser desenvolvida
antes da Etapa 19.

#### 19.1 — Contrato temporal do backtest

- Definir concurso avaliado, janela de treinamento e primeiro concurso elegível.
- Impedir o uso do concurso avaliado e de concursos posteriores.
- Teste: casos de vazamento de futuro obrigatoriamente rejeitados.

#### 19.2 — Backtest de um único sorteio

- Construir os perfis apenas com o passado.
- Submeter o resultado real seguinte aos três níveis.
- Registrar aprovação, primeira exclusão e fotografia da configuração.
- Teste: exemplo pequeno calculado manualmente.

#### 19.3 — Execução sequencial de vários sorteios

- Repetir o processo para um intervalo histórico.
- Processar em lotes reiniciáveis e mostrar progresso.
- Teste: interrupção e retomada sem duplicidade.

#### 19.4 — Métricas do backtest

- Contar resultados reais aprovados e descartados.
- Mostrar falso descarte por filtro e por família.
- Medir estabilidade dos limites e percentuais no tempo.
- Teste: fechamento das métricas com o total avaliado.

#### 19.5 — Comparação de configurações

- Comparar percentuais, multiplicadores, grupos aceitos e ordens do funil.
- Usar exatamente os mesmos concursos para tornar a comparação justa.
- Não escolher automaticamente uma configuração vencedora.
- Teste: resultados reproduzíveis por identificação de execução.

#### 19.6 — API e tela do backtest

- Criar execução, acompanhar progresso e consultar resumo.
- Mostrar linha do tempo de aprovações e exclusões.
- Teste: API, JavaScript e Chrome sem bloquear a interface.

#### 19.7 — Regressão e fechamento do backtest

- Testar banco temporário, cálculos, retomada, API e Chrome.
- Preparar commit somente mediante autorização.


### Etapa 20 — relatório de auditoria detalhado

Objetivo: certificar que cada função estatística, geométrica ou classificadora
de padrões devolve o valor correto para todas as amostras de validação antes de
poder ser utilizada pelo Screener.

Decisão inicial de 28/10/2026, posteriormente substituída: a primeira versão
começaria pela digitação intencional de combinações. A decisão consolidada em
29/10/2026 passou a usar como conjunto inicial os primeiros 200 registros de
`resultados`, sem impedir a inclusão posterior de outras combinações de teste.

Decisão obrigatória de 28/10/2026: os valores calculados mostrados pela auditoria
serão produzidos pelas mesmas funções de produção usadas pelo sistema e pelo
Screener. Não serão criadas fórmulas duplicadas no frontend nem funções paralelas
para montar o relatório. Detalhes diagnósticos poderão ser exibidos quando forem
úteis, mas não constituem colunas obrigatórias do gabarito.

Decisão consolidada em 29/10/2026: a validação usará um gabarito permanente por
amostra e critério. Cada valor esperado será calculado independentemente pela IA
ou pelo usuário, conferido e protegido. As funções reais preencherão somente o
valor calculado. A comparação produzirá aprovação `S` ou `N`.

As amostras não repetirão as dezenas. Elas relacionarão `id_resultado` com a
tabela `resultados`, cuja leitura fornecerá `res_01` a `res_06`. O conjunto
inicial terá os primeiros 200 resultados em ordem de `numero_ap`. Não se trata
de preservar história: são combinações escolhidas como base estável de teste e
outras poderão ser acrescentadas. O número de verificações será `amostras x
critérios` e crescerá sem exigir novas colunas.

Os valores usados para selecionar combinações não serão fotografias permanentes
dos 3.069 resultados iniciais. Após cada importação, as grandezas das novas
linhas e os perfis atuais estatísticos, geométricos e de padrões serão
recalculados sobre todos os resultados então existentes. A simples chegada de
novos resultados não invalida as 200 provas matemáticas de uma função cuja
implementação não mudou; ela exige apenas atualizar com sucesso os perfis atuais.
Somente o futuro backtest reconstruirá perfis com corte por `numero_ap` ou data.

#### 20.0 — Contrato do gabarito e aprovação do modelo

- Fechar nomes, campos, estados, tipos de valor e regras de comparação.
- Separar amostra, catálogo de critérios e avaliação por amostra/critério.
- Relacionar cada critério à função Python e, quando for classificador, ao grupo
  de padrões e aos subgrupos esperado e calculado.
- Determinar que referência aprovada nunca será sobrescrita pelo recálculo.
- Definir igualdade exata para inteiros, códigos e S/N e precisão explícita para
  decimais.
- Definir que `aprovado` será `NULL` enquanto pendente, `S` quando esperado e
  calculado coincidirem e `N` quando divergirem.
- Definir que nenhuma função nova, alterada, pendente ou com algum `N` poderá ser
  usada pelo Screener.
- Teste: exemplos em tabela apresentados ao usuário antes de criar o banco.

Estado: concluída em 2026-10-29 somente em documentação. O contrato aprovado
está em `docs/CONTRATO_HOMOLOGACAO_FUNCOES.md` e a evidência em
`MSen/tests/TESTE_ITEM_20_0.md`. Nenhum DDL, código ou banco foi alterado. A
subetapa 20.1 depende de autorização separada.

#### 20.1 — DDL das amostras de validação

- Criar `amostras_validacao` com `id_resultado` como chave primária e também
  chave estrangeira para `resultados(id_resultado)`, além de ordem e estado ativo.
- Não copiar `res_01` a `res_06`; obtê-los por `INNER JOIN` com `resultados`.
- Usar `ON DELETE CASCADE`, pois a amostra não é arquivo histórico independente.
- Teste: integridade da FK, ausência de duplicidade, leitura das seis dezenas e
  cascata controlada em banco temporário.

Estado: concluída em 2026-10-29. A migração
`011_criar_amostras_validacao.sql` e o esquema consolidado criam somente
`amostras_validacao`, sem duplicar as dezenas. PostgreSQL temporário confirmou
restrições, `INNER JOIN`, cascata e idempotência; o database efêmero foi removido.
Passaram 508 testes Python. Evidência em `MSen/tests/TESTE_ITEM_20_1.md`. O banco
local `games` não foi alterado e a subetapa 20.2 depende de autorização separada.

#### 20.2 — DDL do catálogo e do gabarito

- Criar `criterios_validacao` com código estável, nome legível, categoria
  `ESTATISTICA`, `GEOMETRIA` ou `PADRAO`, função Python, tipo, precisão,
  assinatura automática da implementação, estado e `id_grupo` opcional.
- Criar `avaliacoes_validacao`, relacionando `id_resultado` e `id_criterio`, com
  valor esperado, valor calculado, `id_padrao_esperado` e
  `id_padrao_calculado` opcionais, aprovação `S/N`, data e diferença aplicável.
- Usar chave única por amostra/critério. Para padrões, relacionar grupo e os dois
  subgrupos às tabelas existentes e apresentar códigos e nomes por `JOIN`.
- Usar `ON DELETE CASCADE` das amostras e critérios para suas avaliações.
- Teste: integridade referencial, tipos de critério, uma avaliação por
  amostra/critério e cascatas em banco temporário.

Estado: concluída em 2026-10-29. A migração
`012_criar_catalogo_avaliacoes_validacao.sql` criou o catálogo e as avaliações
com restrições para categorias, tipos, precisão, assinatura, estados, grupos,
subgrupos e aprovação `NULL/S/N`. PostgreSQL temporário confirmou casos
numéricos, padrões, `SEM_CORRESPONDENCIA`, rejeições e cascatas; o database foi
removido. Passaram 514 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_2.md`. `games` não foi alterado e a subetapa 20.3
foi precedida pela nova subetapa 20.2-A, que depende de autorização separada.

#### 20.2-A — Estado global do algoritmo de seleção

- Criar DDL complementar para uma única linha de estado do algoritmo, iniciada
  como desatualizada e sem controle manual direto pelo usuário.
- Apresentar somente dois textos funcionais: `Algoritmo de seleção de combinações
  atualizado` e `Algoritmo de seleção de combinações desatualizado`.
- Guardar internamente o booleano, motivo, datas, assinatura homologada e
  quantidade/identificação do conjunto atual de resultados.
- Marcar como desatualizado quando mudar função, regra, precisão, grupo,
  subgrupo, configuração de seleção ou quando novos resultados aguardarem
  atualização dos perfis atuais.
- Permitir retorno a atualizado somente quando funções estiverem homologadas,
  perfis atuais reconciliados e cobertura de filtros do Screener confirmada.
- Teste: estados, linha única, bloqueio de alteração inválida e transições em
  PostgreSQL temporário. Não aplicar ao `games` nesta subetapa.

Estado: concluída em 2026-10-30. A migração
`013_criar_estado_algoritmo_selecao.sql` cria a linha única inicialmente
desatualizada, guarda assinaturas, quantidade de resultados e datas das três
confirmações, e impede liberação incompleta, segunda linha, quantidade negativa
ou exclusão. PostgreSQL temporário confirmou aplicação isolada da 013,
idempotência e transições; o database efêmero foi removido. Passaram 520 testes
Python. Evidência em `MSen/tests/TESTE_ITEM_20_2_A.md`. `games` não foi alterado
e a subetapa 20.3 depende de autorização separada.

#### 20.3 — Migração e aplicação local

- Acrescentar as migrações 011, 012 e a complementar da 20.2-A ao conjunto de
  DDL executado na inicialização.
- Aplicar primeiro em banco temporário e depois no PostgreSQL local.
- Teste: primeira aplicação, repetição sem erro e preservação das tabelas atuais.

Estado: concluída em 2026-10-30. Foi criado e validado backup customizado do
`games`; o estado inicial possuía somente 001–010. A primeira execução aplicou
exclusivamente 011, 012 e 013 e a segunda não reaplicou nenhuma. Permaneceram
inalterados 3.069 resultados, 3 grupos, 9 subgrupos e 1.289 classificações. As
tabelas de amostras, critérios e avaliações ficaram vazias; a linha global foi
iniciada como desatualizada. Passaram 520 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_3.md`. PythonAnywhere não foi alterado e a subetapa
20.4 depende de autorização separada.

#### 20.4 — Repositório das amostras e avaliações

- Implementar inclusão, consulta e desativação de amostras por `id_resultado`.
- Ao incluir uma amostra, criar uma avaliação pendente para cada critério ativo.
- Ao incluir um critério, criar uma avaliação pendente para cada amostra ativa.
- Consultar combinação, função, grupo e subgrupos com nomes legíveis, sem
  duplicar dezenas ou nomes nas avaliações.
- Teste: sincronização incremental no banco temporário sem destruir avaliações
  ou valores esperados existentes.

Estado: concluída em 2026-10-30. Foi criado `RepositorioValidacao`, com inclusão
transacional de amostra, criação dos pares ativos faltantes, sincronização
idempotente, desativação sem exclusão e consultas detalhadas por `JOIN`. O
PostgreSQL temporário confirmou que referências existentes são preservadas e
que critério novo alcança somente amostras ativas; o database efêmero foi
removido. Passaram 526 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_4.md`. Nenhuma amostra ou critério foi carregado no
`games`; a subetapa 20.5 depende de autorização separada.

#### 20.5 — Registro único e sincronização dos critérios

- Criar registro Python dos critérios executáveis de produção.
- Sincronizar automaticamente cálculos estatísticos, geométricos e detectores de
  padrões com `criterios_validacao`.
- Critério novo entra pendente e recebe avaliações para todas as amostras.
- Critério excluído do registro será removido do catálogo após confirmação; suas
  avaliações serão removidas por cascata.
- Alteração somente da implementação preservará os resultados esperados, limpará
  calculados/aprovações e bloqueará a função até nova execução integral.
- Alteração da regra matemática ou do significado do critério invalidará também
  os esperados, que deverão ser recalculados independentemente e conferidos.
- Detectar alteração pela assinatura automática da implementação, sem exigir que
  o usuário administre manualmente números de versão.
- O cadastro textual de um padrão sem função Python não cria critério executável.
- Teste: incluir, alterar implementação, alterar definição e excluir sem
  duplicidade nem perda indevida de referências.

Estado: concluída em 2026-10-30. O registro único contém 19 critérios atuais: 4
estatísticos, 6 geométricos e 9 detectores de padrões. A migração 014 acrescentou
assinatura automática da regra, separada da implementação. A sincronização
incremental preserva esperados em mudança somente de código, invalida-os em
mudança da regra e exige confirmação para exclusão; alterações estruturais sob o
mesmo código são recusadas. PostgreSQL temporário aprovou todos os fluxos. Após
backup validado, somente a 014 foi aplicada ao `games` e os 19 critérios foram
incluídos como pendentes; não há avaliações porque as amostras continuam vazias.
Passaram 531 testes Python. Evidência em `MSen/tests/TESTE_ITEM_20_5.md`. A
subetapa 20.5-A depende de autorização separada.

#### 20.5-A — Atualização dos perfis atuais após importação

- Integrar a importação de resultados ao recálculo das grandezas, classificações,
  incidências de padrões e perfis estatísticos/geométricos atuais.
- Usar todos os resultados disponíveis no banco operacional, sem conservar
  versões anteriores dos perfis para a execução normal.
- Guardar ou calcular o resumo atual de modo reproduzível, incluindo quantidade
  de resultados considerada e instante do recálculo.
- Não repetir as 200 avaliações quando somente chegaram novos resultados e as
  assinaturas das funções permaneceram iguais.
- Manter o algoritmo desatualizado durante o recálculo ou quando a quantidade do
  perfil não coincidir com a quantidade válida de `resultados`.
- Depois do recálculo bem-sucedido, preservar a homologação das funções e liberar
  o estado somente se as demais condições também estiverem satisfeitas.
- Reservar ao backtest o recálculo com corte por concurso ou data.
- Teste: importar resultado novo, alterar os perfis atuais, preservar as 200
  aprovações e recusar perfil incompleto ou calculado para quantidade antiga.

Estado: concluída em 2026-10-30. A migração 015 criou a tabela substitutiva
`perfis_operacionais_atuais`. A importação com novidades agora bloqueia o
algoritmo antes do recálculo e atualiza derivados, incidências dos nove padrões,
classificação sequencial, quatro perfis estatísticos e seis geométricos sobre
todos os resultados. Quantidade e assinatura do conjunto são persistidas sem
alterar avaliações de homologação. PostgreSQL temporário confirmou a passagem
de três para quatro resultados e preservou uma avaliação aprovada. Após backup,
somente a 015 foi aplicada ao `games`; os 10 perfis e os nove padrões foram
reconciliados com os 3.069 resultados. Passaram 533 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_5_A.md`. A subetapa 20.6 depende de autorização
separada.

#### 20.6 — Carga dos 200 resultados iniciais

- Relacionar os primeiros 200 resultados por `numero_ap`, sem copiar as dezenas.
- Conferir quantidade, ordem, FKs, dezenas obtidas por `JOIN` e ausência de
  duplicidade.
- Permitir acrescentar posteriormente combinações especiais de fronteira, sem
  alterar o conjunto inicial.
- Teste: comparar as amostras com `resultados` registro a registro.

Estado: concluída em 2026-10-30. Foi criado carregador idempotente que valida as
posições existentes, recusa divergências e preserva amostras adicionais. O
PostgreSQL temporário confirmou 200 amostras, 3.800 avaliações pendentes,
dezenas somente por `JOIN` e repetição sem alteração. Após backup validado, o
`games` recebeu os concursos 1–200 nas ordens 1–200 e a matriz 200 × 19; nenhum
esperado, calculado ou aprovado foi preenchido. Passaram 533 testes Python.
Evidência em `MSen/tests/TESTE_ITEM_20_6.md`. A subetapa 20.7 depende de
autorização separada.

#### 20.7 — Construção e aprovação dos valores de referência

- A IA ou o usuário calculará independentemente cada resultado esperado; uma
  demonstração poderá ser apresentada no relatório sem ser coluna obrigatória.
- O usuário poderá aprovar aos poucos; somente uma referência aprovada será
  considerada fiel para comparação.
- Proibir que as funções de produção preencham ou sobrescrevam a referência.
- Teste: referência pendente não aprova nem reprova a função.

Estado: concluída em 2026-10-30. A migração 016 e o serviço de
aprovação registram valor ou ausência legítima, origem, revisor, observação e
data, protegendo referências conferidas contra sobrescrita. PostgreSQL
temporário aprovou referências numéricas e de padrões, inclusive rejeições. Um
oráculo que não importa as funções aferidas produziu e conferiu no `games` 800
referências estatísticas e 1.800 de padrões. O Shapely 2.2.0/GEOS, usado somente
como oráculo de teste, produziu e conferiu as 1.200 referências geométricas sem
importar as funções de produção. O total é 3.800 referências conferidas, sem
pendências, valores ausentes ou metadados inválidos. Passaram 541 testes Python.
Evidência em `MSen/tests/TESTE_ITEM_20_7.md`. A subetapa 20.8 depende de
autorização separada.

#### 20.8 — Adaptadores dos critérios estatísticos

- Usar as funções reais de produção para soma, média, mediana, desvio e futuros
  critérios registrados.
- Gravar o valor calculado pela função real sem alterar o esperado.
- Teste: comparação com as referências aprovadas e exemplos manuais.

Estado: concluída em 2026-10-30. Um executor numérico transacional valida o
catálogo, a assinatura atual e a conferência das referências antes de chamar as
funções reais. Soma, média, mediana e desvio-padrão foram executados nas 200
amostras: 800 comparações `S`, nenhuma `N`. O hash das referências protegidas
permaneceu idêntico antes e depois. Os quatro critérios estatísticos estão
`APROVADO`, mas o algoritmo geral permanece desatualizado enquanto geometria e
padrões não forem executados. Passaram 545 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_8.md`. A 20.9 depende de autorização separada.

#### 20.9 — Adaptadores dos critérios geométricos

- Usar as funções reais para extensão, perímetro, regiões, área e centro de
  gravidade.
- Registrar o valor calculado e a precisão usada na comparação.
- Teste: igualdade conforme a precisão aprovada.

Estado: concluída em 2026-10-30. O adaptador entrega às funções geométricas a
tupla das seis dezenas e preserva o modelo usado pelas estatísticas. Extensão,
perímetro, regiões, área e as duas coordenadas do centro foram executados nas
200 amostras: 1.200 comparações `S`, nenhuma `N`. O comparador aplica a precisão
de 12 casas com `ROUND_HALF_UP` somente na decisão, mantendo o valor bruto para
auditoria. O hash das referências ficou idêntico antes e depois. Os seis
critérios geométricos estão `APROVADO`; o algoritmo geral continua
desatualizado até executar os padrões. Passaram 547 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_9.md`. A 20.10 depende de autorização separada.

#### 20.10 — Adaptadores dos padrões

- Executar os classificadores reais por grupo e registrar o subgrupo calculado.
- Comparar `id_padrao_calculado` com `id_padrao_esperado`; mostrar também os
  nomes legíveis de grupo e subgrupo no relatório.
- Incluir novos detectores pelo registro sincronizado, sem nova coluna no banco.
- Teste: casos positivos, negativos e classificação pelo maior bloco aplicável.

Estado: concluída em 2026-10-30. O executor valida catálogo, assinatura, grupo e
referência antes de traduzir o retorno booleano de cada detector em padrão
identificado ou ausência de correspondência. Os nove detectores foram executados
nas 200 amostras: 1.800 comparações `S`, nenhuma `N`. O hash das referências
ficou idêntico antes e depois, e os nove critérios estão `APROVADO`. Com as
subetapas 20.8 a 20.10, os 19 critérios atuais acertaram todas as 3.800
avaliações. O estado geral permanece bloqueado até a reconciliação prevista nas
subetapas seguintes. Passaram 549 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_10.md`. A 20.11 depende de autorização separada.

#### 20.11 — Motor de recálculo e comparação

- O botão `Atualizar critérios e recalcular` sincronizará o catálogo e executará
  novamente todos os critérios ativos sobre todas as amostras ativas.
- A sincronização só reconhecerá funções Python já implementadas, registradas e
  aprovadas nos testes locais.
- Atualizar somente valor calculado, assinatura executada, data, diferença e
  aprovação `S/N`.
- Nunca alterar automaticamente valores de referência aprovados.
- Para critério novo ou com regra alterada, deixar a referência pendente; o
  botão não usará a própria função aferida para fabricar seu gabarito.
- Consolidar a função como aprovada somente quando todas as amostras ativas
  tiverem esperado conferido, cálculo executado e aprovação `S`.
- Teste: uma única divergência ou pendência mantém a função bloqueada.

Fluxo obrigatório para padrão ou critério novo/alterado:

1. abrir o projeto no VS Code;
2. criar ou alterar a função Python e sua descrição;
3. criar/atualizar os testes automatizados;
4. executar e aprovar os testes localmente;
5. registrar a função no catálogo executável;
6. acionar `Atualizar critérios e recalcular`;
7. conferir o relatório antes de qualquer publicação na nuvem.

O Screener consultará a homologação da assinatura atual antes de montar seus
critérios. Ausência, alteração, pendência ou qualquer `N` produzirá bloqueio
explícito; a falha da consulta nunca será interpretada como aprovação.

Antes de executar, o Screener também comparará os filtros esperados com os
adaptadores realmente carregados. O conjunto esperado conterá todos os filtros
estatísticos e geométricos aprovados e os filtros de padrões aprovados que a
consulta selecionar por incidência inferior ao limite configurado. Filtro
esperado ausente, filtro extra ou perfil atual desatualizado bloqueará toda a
execução. A interrupção normal após uma exclusão não significa filtro ausente:
o filtro precisa estar no plano e será alcançado pelas combinações sobreviventes.

Estado: concluída em 2026-10-30. O motor transacional sincroniza o catálogo,
completa a matriz, executa estatística, geometria e padrões e consolida o
resultado. Critério com referência pendente fica `PENDENTE` sem impedir o
recálculo dos demais; qualquer `N` deixa a função `REPROVADO`. No `games`, a
sincronização foi idempotente e o ciclo confirmou 19 critérios e 3.800
avaliações aprovadas, preservando o hash das referências. Cenários forçados e
revertidos confirmaram que uma única divergência ou pendência bloqueia a função.
O estado global permanece desatualizado com motivo
`HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`, pois homologação matemática não
substitui cobertura operacional. Passaram 550 testes Python. Evidência em
`MSen/tests/TESTE_ITEM_20_11.md`. A 20.12 depende de autorização separada.

#### 20.12 — Modal reutilizável de andamento

- Criar modal que bloqueie duplo clique e informe operação, etapa atual,
  quantidade concluída/total, percentual, duração e eventual erro.
- A API iniciará uma execução identificada e a interface consultará seu estado;
  não será apresentado percentual fictício baseado apenas em animação.
- Permitir fechar o modal somente ao terminar ou após cancelamento seguro, quando
  este existir.
- Teste: sucesso, falha, atualização progressiva e prevenção de execução dupla.

Estado: concluída em 2026-10-30. Um gerenciador assíncrono com trava inicia
execuções identificadas e publica etapa, quantidades, percentual calculado,
duração, resultado e erro por POST/GET. O motor emite progresso real em quatro
etapas. O componente JavaScript reutilizável impede duplo clique e fechamento
durante a execução; a página reservada recebeu somente o botão de acionamento,
mantendo a construção completa para 20.13. Passaram 554 testes Python, 35 testes
Node e um fluxo Chromium que observou 50%, 100% e bloqueio de fechamento.
Evidência em `MSen/tests/TESTE_ITEM_20_12.md`. A 20.13 depende de autorização
separada.

#### 20.13 — Página de Validação e auditoria

- Mostrar em destaque um dos dois estados globais do algoritmo e, quando
  desatualizado, o botão `Atualizar Validação e auditoria`.
- Exibir as dezenas obtidas de `resultados`, função e nome legível do critério,
  grupo/subgrupos quando aplicáveis, esperado, calculado e aprovação `S/N`.
- Oferecer filtros por categoria, função, grupo, subgrupo e situação.
- Oferecer `Atualizar critérios e recalcular`, resumo e detalhes da divergência.
- Preservar espaço com cabeçalho compacto e rolagens internas.
- Teste: Chrome em largura normal e estreita, inclusive durante execução.

Estado: concluída em 2026-10-30. A API somente leitura entrega estado global,
resumo, opções de filtro e avaliações paginadas com dezenas, nomes e subgrupos
obtidos por `JOIN`. A página compacta mostra os dois estados globais, motivo,
botão quando desatualizado, quatro contadores, cinco filtros, grade rolável e
paginação de 50 linhas; após o modal, recarrega os dados. Consulta real confirmou
3.800 `S`, 19 critérios, 3 grupos e 9 subgrupos. Passaram 557 testes Python, 36
Node e dois fluxos Chromium em 1280×800 e 390×844. A skill Sites orientou o
trabalho local e o teste responsivo, sem publicação externa. Evidência em
`MSen/tests/TESTE_ITEM_20_13.md`. A 20.14 depende de autorização separada.

#### 20.14 — Relatório de divergências

- Informar por função total exigido, executado, aprovado, divergente e pendente,
  além de critérios novos, excluídos ou cuja implementação mudou.
- Para cada `N`, mostrar combinação, função, filtro, grupo/subgrupo, esperado,
  calculado, diferença e assinatura executada.
- Permitir que a IA analise a divergência e apresente uma hipótese diagnóstica,
  sem alterar automaticamente referência, função ou aprovação.
- Teste: relatório fecha com o total de verificações.

Estado: concluído em 2026-10-30. A API e a página apresentam, por função,
exigidas, executadas, `S`, `N`, pendentes e estado do catálogo. Cada `N` expõe
combinação, critério, grupo/subgrupo, esperado, calculado, diferença,
assinaturas e hipótese diagnóstica sem alterar a homologação. O banco `games`
fechou 3.800 verificações `S` em 19 critérios. Evidência em
`MSen/tests/TESTE_ITEM_20_14.md`.

#### 20.15 — Exportação e reprodução

- Exportar JSON técnico e formato tabular seguro para conferência humana.
- Incluir assinaturas, precisão e identificação do conjunto de referências.
- Teste: exportar e reabrir sem perda ou execução de fórmula injetada.

Estado: concluído em 2026-10-30. `GET /api/validacao/exportacao` entrega JSON
técnico reproduzível ou CSV UTF-8 seguro. Ambos incluem identificação SHA-256
do conjunto, assinaturas da função, regra e execução, precisão, proveniência
das referências e resultados esperado/calculado. O CSV neutraliza prefixos de
fórmula; o JSON reaberto é validado contra o hash. No `games`, foram exportados
3.800 registros com identificador
`aa4b253bedb2107535ce5ffc0ffaf43621605d63d808b87d5c53c8609bb6c8b4`.
Passaram 563 testes Python, 37 Node e dois fluxos Chromium. Evidência em
`MSen/tests/TESTE_ITEM_20_15.md`. A 20.16 depende de autorização separada.

#### 20.16 — Regressão técnica da validação

- Executar testes Python, banco temporário, API, JavaScript e Google Chrome.
- Confirmar que todos os valores calculados vieram das funções de produção.
- Confirmar que o Screener recusa função nova, alterada, pendente ou com algum
  `N` e aceita somente a assinatura integralmente aprovada.
- Confirmar que importação nova atualiza os perfis correntes sem refazer as 200
  provas quando nenhuma função mudou.
- Confirmar que o Screener carrega todos os filtros estatísticos e geométricos
  aprovados e exatamente os padrões aprovados selecionados pelo limite vigente.
- Confirmar bloqueio por filtro ausente/extra, perfil antigo ou estado global
  desatualizado.
- Teste: repetir os fluxos de atualização, aprovação, divergência e bloqueio sem
  depender somente da interface.

Estado: concluído em 2026-10-30. O Screener passou a consultar a homologação
antes de criar o plano executável e bloqueia estado global desatualizado,
catálogo novo/divergente, função pendente ou reprovada, assinatura antiga,
perfil antigo e cobertura com filtro ausente/extra. A cobertura exige todos os
critérios estatísticos e geométricos e exatamente os padrões homologados
selecionados pela incidência. Dois bancos temporários confirmaram 200 amostras,
3.800 avaliações e a incorporação de resultado novo nos dez perfis sem alterar
a homologação. No `games`, 19 critérios, 10 perfis e 3.069 resultados estão
coerentes, mas o estado continua deliberadamente bloqueado por
`HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`. Passaram 567 testes Python, 37
Node e 20 fluxos Chromium. Evidência em `MSen/tests/TESTE_ITEM_20_16.md`. A
20.17 depende de autorização separada.

#### 20.17 — Funcionamento vigente, índice e fechamento documental

- Atualizar `docs/funcionamento.md` para explicar o fluxo completo realmente
  implementado: entrada de resultados, recálculo dos perfis atuais, homologação
  das funções, atualização da Validação e auditoria e trava do Screener.
- Explicar separadamente validação matemática, construção dos filtros e uso dos
  filtros nas três famílias: estatística, geometria e padrões.
- Registrar que perfis operacionais usam todos os resultados disponíveis no
  momento e que somente o backtest aplica corte por concurso ou data.
- Conferir nomes reais de tabelas, páginas, APIs, arquivos de configuração e
  funções; remover ou identificar claramente descrições substituídas.
- Reconciliar `PLANO_DO_PROJETO.md`, `notas/decisoes.md`,
  `notas/funcionalidades.md`, documentos de banco/API afetados e
  `docs/INDICE_DOCUMENTACAO.md`.
- Teste: buscas por nomes e contratos revogados, links/caminhos existentes e
  comparação da narrativa com código, DDL, API e testes atuais.
- Preparar commit e push somente mediante autorização específica.

Estado: concluído em 2026-10-30, sem commit ou push. `docs/funcionamento.md`
foi reescrito como descrição canônica do fluxo implementado; a versão anterior
e o plano inicial foram preservados como históricos. Foram reconciliados plano
do projeto, visão geral, arquitetura, organização Python, decisões,
funcionalidades, contrato de homologação, API da validação e índice. Contratos
substituídos foram rotulados, inclusive os dois contextos distintos de
`SEM_CORRESPONDENCIA`. Passaram 571 testes Python, 37 Node e 20 fluxos
Chromium. Evidência em `MSen/tests/TESTE_ITEM_20_17.md`.

#### 20.18 — Fechamento da atualização e alerta de bloqueio no Screener

Objetivo: tornar inequívoco para o usuário o resultado da execução da
Validação e auditoria e o consequente bloqueio do Screener quando os critérios
de seleção ainda não estiverem integralmente aprovados.

- Manter separadas a conclusão do processamento e a aprovação da validação:
  atingir 100% significa que a execução terminou, não necessariamente que foi
  aprovada.
- Ao final do modal de atualização, apresentar o diagnóstico consolidado com
  total, aprovadas, reprovadas e pendentes.
- Quando todas as avaliações estiverem aprovadas, informar explicitamente que
  a Validação e auditoria foi concluída e aprovada.
- Quando houver qualquer `N` ou pendência, informar que o processamento foi
  concluído, mas a validação não foi aprovada, e orientar o usuário a usar o
  filtro `Situação` para localizar as ocorrências.
- Tratar erro técnico ou interrupção como resultado diferente de execução
  concluída com reprovações ou pendências.
- Bloquear a execução do Screener enquanto existir critério novo, alterado,
  pendente ou reprovado na Validação e auditoria.
- Exibir no Screener, para qualquer um desses impedimentos, somente a mensagem
  acordada: **"Screener bloqueado: há pendências na Validação e auditoria dos
  critérios de seleção."**
- Não confundir no modal o resultado da validação matemática com outras
  condições operacionais posteriores do Screener.
- Preservar os resultados esperados, calculados, aprovações e assinaturas; esta
  subetapa altera comunicação e bloqueio, não as fórmulas homologadas.
- Testar os cenários: tudo aprovado; uma reprovação; uma pendência; critério
  novo; critério alterado; erro técnico; atualização da tela após o fechamento
  do modal; e tentativa de executar o Screener bloqueado.

Estado: concluído em 2026-10-30. O modal agora diferencia processamento
concluído, validação aprovada, validação com reprovações ou pendências e falha
técnica. O cabeçalho da página passou a mostrar o diagnóstico da validação,
sem confundi-lo com o estado operacional posterior do Screener. O Screener
consulta o relatório antes de habilitar a execução e, para
critério novo, alterado, pendente ou reprovado, permanece desabilitado com a
mensagem única acordada. Nenhuma fórmula ou avaliação persistida foi alterada.
Passaram 572 testes Python, 37 Node e 24 fluxos Chromium. Evidência em
`MSen/tests/TESTE_ITEM_20_18.md`.

#### Etapa posterior — modal de andamento no Screener

- Reutilizar o componente aprovado na Validação e auditoria para a execução das
  5.000 combinações.
- Exibir progresso real pelas três famílias e pelo filtro em execução.
- Planejar e executar somente após o modal ser validado na Etapa 20; esta nota
  não autoriza alteração imediata no Screener.


### Etapa 21 — capacidade e decisão sobre o universo integral

Objetivo: preparar tecnicamente a análise das 50.063.860 combinações sem
liberá-la automaticamente.

#### 21.1 — Medição de capacidade

- Medir custo real por família, memória, tempo e volume de saída.
- Projetar cenários para o universo integral.

#### 21.2 — Processamento em lotes

- Planejar lotes, checkpoints, retomada e cancelamento seguro.
- Evitar manter todas as combinações simultaneamente em memória.

#### 21.3 — Ensaio ampliado controlado

- Aumentar o limite gradualmente somente mediante autorização.
- Confirmar contabilidade e reprodução em cada escala.

#### 21.4 — Decisão de liberação integral

- Revisar backtests, falsos descartes, auditorias, desempenho e armazenamento.
- Manter trava integral até autorização explícita final.


### Etapa 22 — Frequência das dezenas e evolução concurso a concurso

Objetivo: criar um módulo independente para estudar frequência, intervalos de
retorno e sequências de ocorrência das dezenas, preservando o que teria sido
calculado em cada momento histórico e permitindo avaliar posteriormente a
assertividade do método. O módulo terá item próprio no menu e página
`Frequência das dezenas`.

Premissas aprovadas para o primeiro estudo:

- a tabela atual `frequencia_de_resultado` continua sendo a fotografia
  acumulada do concurso 1 até o último resultado armazenado;
- a série histórica começa no concurso 500;
- a primeira fotografia usa exclusivamente os concursos 1 a 500;
- cada fotografia seguinte acrescenta um concurso: 1 a 501, 1 a 502 e assim
  sucessivamente;
- nenhum resultado posterior ao concurso da fotografia participa de seu
  cálculo;
- resultados posteriores serão usados somente na etapa separada de avaliação
  da assertividade;
- o eixo horizontal dos gráficos históricos será `numero_do_concurso`;
- a tabela histórica não repetirá `ultima_ocorrencia_conhecida` nem armazenará
  antecipadamente acerto, erro ou próxima ocorrência real;
- a primeira faixa estatística preservará unidades: média dos intervalos
  mais ou menos um desvio-padrão populacional dos intervalos;
- configuração percentual e aplicação global, por grupo ou individual serão
  estudadas posteriormente na página de Distribuições, sem conversão implícita
  entre unidades e percentuais nesta etapa;
- o tick `Salvar dados` virá marcado por padrão, mas toda gravação exigirá
  confirmação explícita do usuário.

#### 22.0 — Contrato matemático e casos-limite

- Formalizar ocorrência simples, `2VS` e `3VS` a partir da ordem dos concursos.
- Registrar os exemplos aprovados: uma dezena presente nos concursos 210 e 211
  forma `2VS`; uma dezena presente em 615, 616 e 617 forma `3VS`.
- Decidir antes do código como classificar sequências de quatro ou mais
  concursos e se uma sequência `3VS` também gera um evento `2VS`, sem usar
  informação futura no cálculo de uma fotografia.
- Definir o concurso que representa a conclusão de cada evento e calcular os
  intervalos entre eventos equivalentes.
- Confirmar desvio-padrão populacional, quantidade mínima de eventos, estados
  sem base estatística, limites inclusivos e arredondamento externo.
- Teste: exemplos manuais pequenos, sequências interrompidas, sobrepostas e com
  quatro ou mais ocorrências consecutivas.

Estado: concluído em 2026-10-30. O contrato matemático foi formalizado em
`docs/CONTRATO_FREQUENCIA_DEZENAS.md`: eventos 2VS e 3VS usam janelas
consecutivas sobrepostas, o concurso final representa a conclusão do evento,
sequências de quatro ou mais geram todas as janelas já concluídas, intervalos
são calculados somente entre eventos equivalentes, o desvio é populacional na
unidade concurso e a faixa inicial usa limites inclusivos com arredondamento
externo. Nenhum código ou banco de dados foi alterado.

#### 22.1 — Inventário e evolução da fotografia atual

- Preservar as 60 linhas e os relacionamentos atuais de
  `frequencia_de_resultado`.
- Acrescentar, por migração segura, quantidade de intervalos, intervalo mínimo
  e intervalo máximo para as ocorrências simples.
- Manter `media_oco`, `mediana_oco` e `desv_padrao_oco` na unidade concurso e
  melhorar somente os nomes apresentados ao usuário.
- Reconciliar `60` dezenas, `sum(num_oco) = quantidade de resultados × 6` e os
  valores recalculados diretamente da tabela `resultados`.
- Teste: banco temporário, migração, idempotência e preservação dos dados
  atuais.

Estado: concluído em 2026-10-30. O inventário confirmou que a fotografia atual
já calculava ocorrências, média, mediana e desvio-padrão populacional dos
intervalos simples. A migração 017 acrescentou quantidade, mínimo e máximo e os
preenche diretamente a partir das seis dezenas de `resultados`; cálculo e
repositório passaram a manter esses campos. PostgreSQL efêmero confirmou 60
linhas, reconciliação das ocorrências e os limites esperados, e 576 testes
passaram. Evidência em `MSen/tests/TESTE_ITEM_22_1.md`. O database persistente
`games` não foi alterado. A subetapa 22.2 depende de autorização separada.

#### 22.2 — Configuração reproduzível do estudo

- Criar configuração persistida com nome, concurso inicial, tamanho inicial,
  regra de evolução da janela, tipo de evento, método da faixa, parâmetros,
  arredondamento e versão de cálculo.
- Configuração inicial: concurso inicial `1`, tamanho inicial `500`, início
  fixo e final expansivo.
- Gerar assinatura SHA-256 com todos os campos e versões capazes de alterar o
  resultado.
- Comparar a configuração calculada com a configuração gravada e informar
  parâmetros divergentes, sem depender apenas da assinatura.
- Não inferir unidade pelo valor numérico: método, parâmetro e unidade deverão
  ser explícitos.
- Teste: assinaturas estáveis, alteração de cada campo relevante e rejeição de
  configurações ambíguas.

Estado: concluído em 2026-10-30. A migração 018 criou a linha única da
configuração ativa e sua semente `1 / 500 / início fixo / final expansivo`, com
os três tipos de evento representados por `TODOS`. Método, parâmetro, unidade e
arredondamento são explícitos; percentual é recusado nesta etapa. O Python gera
SHA-256 de JSON canônico, confere a assinatura persistida e compara todos os
campos, informando valores gravados e calculados divergentes. PostgreSQL
efêmero confirmou semente, substituição, restrições e idempotência; 590 testes
passaram. Evidência em `MSen/tests/TESTE_ITEM_22_2.md`. O database persistente
`games` não foi alterado. A subetapa 22.3 depende de autorização separada.

#### 22.3 — Estrutura histórica materializada

- Criar tabela histórica normalizada por `numero_do_concurso`, dezena, tipo de
  evento, configuração e versão do cálculo.
- Armazenar quantidade de ocorrências, quantidade de intervalos, intervalo
  mínimo, intervalo máximo, média, mediana, desvio-padrão, previsão central e
  limites inferior e superior.
- Não duplicar as seis dezenas dos resultados e não armazenar resultado futuro
  na fotografia calculada.
- Criar índice principal para consulta por dezena, tipo de evento e concurso.
- Usar chaves, restrições de estado e precisão decimal compatíveis com o volume
  previsto, inicialmente em torno de 150 mil linhas por tipo de evento.
- Teste: DDL, FKs, unicidade, estados sem base e plano de consulta do gráfico.

Estado: concluído em 2026-10-30. A migração 019 criou gerações isoladas e a
tabela normalizada de fotografias por geração, concurso, dezena e evento. A
geração preserva assinatura e JSON canônico da configuração e somente uma pode
estar ativa. Cada fotografia guarda quantidades, estatísticas, previsão e
limites exatos/operacionais, sem copiar as seis dezenas nem resultados futuros.
Restrições distinguem ausência de base e base calculável; índices atendem séries
por dezena/evento e cortes por concurso. PostgreSQL efêmero confirmou unicidade,
precisão, estado, cascata e plano indexado; 597 testes passaram. Evidência em
`MSen/tests/TESTE_ITEM_22_3.md`. O database persistente `games` não foi alterado.
A subetapa 22.4 depende de autorização separada.

#### 22.4 — Motor de cálculo acumulado

- Calcular a fotografia 500 com os concursos 1 a 500 e avançar um concurso por
  vez sem consultar resultados posteriores ao corte.
- Calcular separadamente ocorrência simples, `2VS` e `3VS` conforme o contrato
  aprovado na 22.0.
- Preservar as unidades: média e desvio dos intervalos permanecem em concursos;
  multiplicador de desvio permanece adimensional.
- Construir limites iniciais por `média ± 1 desvio-padrão`, sem tratar o desvio
  como percentual.
- Produzir resultados determinísticos e reproduzíveis para carga completa e
  atualização incremental.
- Teste: oráculos manuais, comparação carga completa versus incremental e
  garantia de ausência de vazamento de informação futura.

Estado: concluído em 2026-10-30. Foi implementado o motor incremental que
processa concursos estritamente em ordem, acumula eventos simples, 2VS e 3VS e
emite 60 linhas por tipo somente a partir do primeiro corte. A configuração
inicial produziu as 180 linhas esperadas no concurso 500. Média e desvio usam
precisão interna elevada e permanecem em concursos; o multiplicador é
adimensional e os limites inteiros usam arredondamento externo. Testes
confirmaram janelas sobrepostas, interrupções, estados sem base, ausência de
vazamento futuro, reconciliação com o cálculo simples existente e igualdade
entre carga integral e incremental. Passaram 608 testes. Evidência em
`MSen/tests/TESTE_ITEM_22_4.md`. Nenhum dado foi persistido e a subetapa 22.5
depende de autorização separada.

#### 22.5 — Primeira carga, substituição e atualização incremental

- Primeira gravação: construir do concurso 500 até o último disponível.
- Mesma configuração e somente concursos novos: inserir apenas as novas
  fotografias, por exemplo 903, 904 e 905 após uma base encerrada em 902.
- Configuração diferente: calcular uma geração provisória completa e substituir
  a geração ativa somente depois de fechamento bem-sucedido.
- Detectar lacuna, concurso antigo alterado, versão incompatível e contagem
  divergente; nesses casos, impedir acréscimo silencioso e exigir reconstrução.
- Manter a geração anterior intacta se houver falha ou cancelamento; depois da
  troca bem-sucedida, conservar somente a nova geração detalhada.
- Medir tempo, linhas, tamanho da tabela e custo dos índices antes de otimizar.
- Teste: primeira carga, acréscimo, repetição idempotente, troca de configuração,
  falha no meio e recuperação sem perda.

Estado: concluído em 2026-10-30. A migração 020 passou a identificar a origem
de cada geração por quantidade e SHA-256 dos resultados. O serviço cria e troca
gerações atomicamente, mantém a ativa em qualquer falha, grava somente novos
cortes quando configuração e prefixo coincidem e exige reconstrução diante de
alteração antiga, lacuna ou incompatibilidade. Testes confirmaram primeira
carga, repetição idempotente, acréscimo, troca, falhas integral/incremental e
reconstrução sem conservar gerações antigas. Com 3.069 resultados reais em
banco efêmero, foram geradas 462.600 linhas em 149,947 s, ocupando cerca de
121,9 MiB, sendo 68,4 MiB de índices. Passaram 613 testes. Evidência em
`MSen/tests/TESTE_ITEM_22_5.md`. O `games` foi somente lido no benchmark e não
foi alterado. A subetapa 22.6 depende de autorização separada.

#### 22.6 — Confirmação de gravação e simulação

- Exibir `Salvar dados` marcado por padrão em cada abertura da página, sem
  memorizar silenciosamente o tick.
- Com o tick marcado, sempre pedir confirmação antes de iniciar a gravação.
- Para configuração igual, informar os concursos que serão acrescentados.
- Para configuração diferente, mostrar lado a lado a configuração existente e
  a calculada e avisar que os dados detalhados serão reconstruídos e substituídos.
- Com o tick desmarcado, calcular a experiência sem substituir a geração ativa.
- Desabilitar dupla execução, permitir cancelamento seguro e apresentar
  progresso real da operação.
- Teste: confirmação, cancelamento, tick padrão, simulação e proteção contra
  substituição involuntária.

Estado: concluído em 2026-10-30. O estado inicial reutilizável mantém `Salvar
dados` marcado sem persistência silenciosa. A prévia distingue primeira carga,
incremental, sem alteração e reconstruções, lista concursos novos e mostra
campos divergentes lado a lado. O servidor recusa gravação sem confirmação
explícita; simulação usa o motor real sem escrever. Progresso corresponde aos
concursos processados, cancelamento entre concursos reverte toda a transação e
coordenadores no servidor/frontend impedem dupla execução. O modal compartilhado
ganhou cancelamento opcional sem permitir fechamento durante a tarefa. Passaram
615 testes Python e 42 JavaScript. Evidência em
`MSen/tests/TESTE_ITEM_22_6.md`. O `games` não foi alterado. API e página
permanecem nas subetapas 22.7 e 22.8; a 22.7 depende de autorização separada.

#### 22.7 — API do módulo

- Criar consultas para fotografia atual, configuração ativa, resumo da base,
  pontos históricos por dezena/tipo/período e prévia de simulação.
- Criar tarefa assíncrona para carga, simulação, substituição e acréscimo
  incremental, com progresso consultável.
- Limitar período e volume devolvido; os gráficos não receberão todas as dezenas
  e tipos quando apenas uma série tiver sido solicitada.
- Validar parâmetros, unidade, configuração e concorrência no servidor.
- Teste: contratos JSON, erros previsíveis, paginação/séries e indisponibilidade
  do banco.

Estado: concluído em 2026-10-30. A API foi criada em
`MSen/src/msen/api/frequencias.py`, registrada na aplicação e documentada em
`docs/API_FREQUENCIAS.md`. Ela oferece estado, fotografia atual, uma série
histórica filtrada, prévia e execução assíncrona com progresso e cancelamento.
Cada consulta histórica devolve somente uma dezena e um tipo de evento, em
período máximo de 5.000 concursos. Parâmetros desconhecidos ou incompletos são
recusados, gravações exigem confirmação explícita e somente uma execução pode
ficar ativa. A validação em PostgreSQL efêmero confirmou estado, 60 dezenas e
série filtrada sem copiar as dezenas dos resultados. Passaram 626 testes Python
e 42 JavaScript. Evidência em `MSen/tests/TESTE_ITEM_22_7.md`; o banco `games`
não foi alterado. A 22.8 permanece pendente de autorização específica.

#### 22.8 — Item de menu e página Frequência das dezenas

- Acrescentar `Frequência das dezenas` à navegação comum sem retirar os itens
  existentes.
- Criar HTML, CSS e JavaScript separados nas pastas reservadas do frontend.
- Apresentar configuração calculada e configuração gravada, estado da base,
  último concurso processado, quantidade de linhas e ações de executar/salvar.
- Manter a página funcional em larguras normal e estreita, com rolagem interna
  das regiões densas.
- Teste: navegação, acessibilidade, estado inicial, confirmação e layout no
  Google Chrome.

Estado: concluído em 2026-10-30. `Frequência das dezenas` foi acrescentada à
navegação comum e a página `/frequencias.html` foi criada com HTML, CSS e
JavaScript separados. Ela apresenta estado da base, concursos disponíveis,
último concurso processado, linhas históricas, configuração gravada e
configuração a calcular. A operação calcula a prévia antes de executar, inicia
com `Salvar dados` marcado, exige a confirmação aprovada para gravação e usa o
modal compartilhado para progresso e cancelamento. Com o tick desmarcado, faz
simulação sem gravar. A barra comum ganhou rolagem a partir de 50 rem para
acomodar o novo item sem alargar páginas estreitas. Passaram 626 testes Python,
45 JavaScript e 27 fluxos no Google Chrome, incluindo a nova página em 1280 px
e 520 px. Evidência em `MSen/tests/TESTE_ITEM_22_8.md`; o banco `games` não foi
alterado. Os gráficos permanecem nas subetapas 22.9 e 22.10.

#### 22.9 — Gráficos de colunas da fotografia atual

- Criar um gráfico de colunas para cada medida comparável entre as 60 dezenas:
  ocorrências, intervalo mínimo, máximo, médio, mediana e desvio-padrão.
- Permitir selecionar ocorrência simples, `2VS` ou `3VS` quando os respectivos
  dados estiverem disponíveis.
- Exibir unidade, quantidade de intervalos, concurso inicial/final e data da
  atualização sem rotular desvio em concursos como percentual.
- Teste: 60 dezenas, escalas, valores nulos, responsividade e conferência com o
  banco.

Estado: concluído em 2026-10-30. A fotografia atual passou a ser lida da última
linha da geração ativa em uma única consulta para as 60 dezenas, filtrada por
`SIMPLES`, `2VS` ou `3VS`. A página apresenta seis gráficos de colunas: número
de ocorrências, intervalo mínimo, máximo, médio, mediana e desvio-padrão. Cada
cartão informa sua unidade; os tooltips mostram dezena, valor e quantidade de
intervalos, e ausência de amostra suficiente permanece nula. O cabeçalho exibe
período, total de intervalos, unidade e data de atualização. A API rejeita tipos
inválidos e o PostgreSQL efêmero confirmou 60 dezenas em cada um dos três tipos.
Passaram 627 testes Python, 47 JavaScript e 27 fluxos no Google Chrome, com 360
barras e troca para 2VS conferidas. Evidência em
`MSen/tests/TESTE_ITEM_22_9.md`; o banco `games` não foi alterado. O gráfico
histórico permanece na 22.10.

#### 22.10 — Gráfico histórico por dezena

- Usar `numero_do_concurso` no eixo horizontal.
- Desenhar as linhas de intervalo mínimo, média, intervalo máximo e a faixa
  estatística configurada, com legenda inequívoca.
- Obter os pontos de ocorrência real diretamente de `resultados`, sem gravá-los
  como se fossem conhecidos pela fotografia histórica.
- Permitir filtrar dezena, tipo de evento e intervalo de concursos, ampliando
  uma série sem sobrepor 60 curvas ilegíveis.
- Teste: concurso 500, avanço sucessivo, pontos reais, ausência de futuro nos
  cálculos e desempenho da consulta indexada.

Estado: concluído em 2026-10-30. A página recebeu filtros de dezena, tipo de
evento e período, limitado pela API a 5.000 concursos. Para não misturar
unidades, a visualização foi dividida em dois gráficos sincronizados pelo eixo
`numero_do_concurso`: evolução do intervalo mínimo, médio e máximo; e faixa
prevista com limite inferior, previsão central, limite superior e ocorrências
reais. As ocorrências reais são consultadas diretamente em `resultados` e não
alteram as fotografias: presença para `SIMPLES`, segunda ocorrência consecutiva
para `2VS` e terceira para `3VS`. Os cálculos históricos continuam contendo
somente informações disponíveis até cada corte. Passaram 627 testes Python, 50
JavaScript e 27 fluxos no Google Chrome. O PostgreSQL efêmero confirmou as três
regras de ocorrência e a série filtrada. Evidência em
`MSen/tests/TESTE_ITEM_22_10.md`; o banco `games` não foi alterado. A avaliação
de acertos e erros permanece na 22.11.

#### 22.11 — Avaliação posterior da assertividade

- Manter a construção da fotografia separada da avaliação do método.
- Cruzar previsões armazenadas com ocorrências posteriores já existentes em
  `resultados`, sem modificar as fotografias históricas.
- Informar total avaliável, acertos, erros, percentual de acerto, erro absoluto
  e erro percentual; previsões sem futuro suficiente não contam como erro.
- Definir o denominador e a regra exata do erro percentual antes da
  implementação desta subetapa.
- Comparar configurações somente quando usarem o mesmo período e a mesma regra
  de evento.
- Teste: acerto nos limites, erro abaixo/acima, final censurado e ausência de
  alteração na base calculada.

Estado: concluído em 2026-10-30. Cada fotografia é comparada com o primeiro
evento real posterior ao seu corte, mantendo cálculo e avaliação separados.
Limites são inclusivos. O erro absoluto é a distância entre ocorrência real e
previsão central; o percentual divide essa distância pelo intervalo real entre
o último evento conhecido e o próximo. Casos sem evento anterior, estatística
completa ou próximo evento conhecido são censurados e não entram no
denominador. A página informa avaliáveis, acertos, erros, censurados, percentual
de acerto, erro absoluto médio e erro percentual médio, além de relatório das
previsões abaixo ou acima da faixa. A avaliação usa a mesma geração e período da
série selecionada, sem alterar fotografias. Passaram 629 testes Python, 50
JavaScript e 27 fluxos no Google Chrome. O PostgreSQL efêmero confirmou série,
regras de evento e censura final. Evidência em
`MSen/tests/TESTE_ITEM_22_11.md`; o banco `games` não foi alterado. A 22.12
permanece pendente de autorização específica.

#### 22.12 — Regressão, desempenho e documentação

- Executar testes matemáticos, banco temporário, API, JavaScript e Chrome.
- Confirmar que carga completa e incremental produzem o mesmo resultado final.
- Medir custo da carga histórica, acréscimo de concurso, consulta dos gráficos
  e tamanho real das tabelas/índices.
- Atualizar funcionamento, arquitetura, banco de dados, API, decisões,
  funcionalidades e índice de documentação.
- Registrar separadamente o estudo futuro de percentuais na página de
  Distribuições.
- Preparar commit e push somente mediante autorização específica.

Estado: concluído em 2026-10-30. Passaram os validadores PostgreSQL de carga,
incremento, troca, rollback, simulação, cancelamento, API, três eventos,
gráficos e assertividade. A regressão final confirmou 629 testes Python, 50
JavaScript e 27 fluxos no Google Chrome. O benchmark local com 3.069 resultados
produziu 462.600 linhas: carga completa em 146,761 s, um concurso incremental
em 0,189 s, três fotografias em 0,003 s e série de 2.571 pontos em 0,057 s. A
tabela com índices ocupou 127.811.584 bytes, sendo 71.688.192 bytes de índices.
Funcionamento, visão do projeto, modelo PostgreSQL, código Python, API, índice,
decisões, funcionalidades e continuidade foram reconciliados. Evidência em
`MSen/tests/TESTE_ITEM_22_12.md`. Todos os databases temporários foram removidos,
o `games` não foi alterado e nenhum commit ou push foi executado. Etapa 22
concluída.
