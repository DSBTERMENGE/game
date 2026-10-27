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

## Próximo item proposto

Definir e planejar com o usuário as próximas funcionalidades locais. A Etapa 8
permanece adiada até o sistema estar completo, testado e aprovado localmente.

Este item não deve ser iniciado sem autorização expressa do usuário.
