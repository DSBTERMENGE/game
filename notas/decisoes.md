# Decisões do projeto

## 2026-10-24 — Estrutura inicial

- O código Python ficará em `MSen/src/msen`.
- Os dados específicos da aplicação ficarão em `MSen/dados`.
- Testes automatizados ficarão em `MSen/tests`.
- Documentação estável ficará em `docs`.
- Ideias e planejamento em andamento ficarão em `notas`.
- Os arquivos HTML e CSS existentes permanecerão na raiz até que sua relação
  com a aplicação Python seja definida.

## 2026-10-25 — Estrutura inicial dos resultados

- A tabela principal se chamará `resultados`.
- Ela começará somente com os campos conhecidos: `numero_concurso`,
  `data_sorteio` e `bola_1` a `bola_6`.
- Não serão criados campos genéricos `C8` a `C50`.
- Campos futuros serão adicionados por novas migrações depois que nome, tipo e
  regras estiverem definidos.
- As bolas devem estar entre 1 e 60 e não podem se repetir no mesmo concurso.
- Os arquivos da interface foram movidos da raiz para `frontend`.

## 2026-10-25 — Coordenadas e visualização

- A grade de 01 a 60 possui coordenadas de `(0; 0)` a `(9; 5)`.
- O eixo horizontal cresce para a direita e o vertical cresce para baixo.
- A média espacial será calculada pela média independente das coordenadas X e Y
  dos seis resultados.
- Coordenadas decimais não serão arredondadas para uma dezena.
- A animação exibirá um resultado a cada 0,5 segundo e apagará o anterior.
- O modo mancha conservará as marcações anteriores.

## 2026-10-26 — Execução controlada e fonte de dados

- A planilha original fica em `MSen/dados/fontes` e será tratada como somente
  leitura pela aplicação.
- `PLANO_ETAPAS_E_TESTES.md` é o roteiro operacional vigente.
- Somente um item autorizado será executado por vez.
- Cada item deve terminar com seus testes e um pedido de autorização para o
  item seguinte.

## 2026-10-26 — Dicionário da tabela `resultados`

- `numero_ap` representa o número da coluna `Concurso`.
- O desvio-padrão da linha será populacional, com divisor 6.
- Médias, coordenadas e desvio-padrão serão armazenados com seis casas decimais
  e inicialmente exibidos com duas.
- A tabela terá os campos técnicos `versao_calculo`, `criado_em` e
  `atualizado_em`.
- `id_resultado` será uma identidade interna automática e `numero_ap` será a
  identificação funcional única.
- O dicionário aprovado está em `docs/DICIONARIO_DADOS_RESULTADOS.md`.

## 2026-10-26 — Contrato dos cálculos

- Os cálculos decimais usarão `Decimal` e `ROUND_HALF_UP`.
- Somente o resultado final de cada campo será arredondado; valores
  intermediários manterão a precisão de cálculo.
- Análises históricas serão ordenadas por `numero_ap` crescente, com a data como
  conferência.
- Intervalo é a diferença entre os números das apresentações: ocorrências nas
  apresentações 35 e 50 produzem intervalo 15.
- Ausência de intervalo será representada por `NULL`.
- Com exatamente um intervalo observado, seu desvio-padrão será zero.
- O contrato aprovado está em `docs/CONTRATO_RESULTADOS_E_CALCULOS.md`.
- Uma linha de resultado nunca aceita dezenas repetidas. Valores iguais somente
  podem aparecer em sequências derivadas, como os intervalos entre ocorrências.

## 2026-10-26 — Modelo PostgreSQL

- O banco terá as tabelas `resultados`, `frequencia_de_resultado` e
  `schema_migrations`.
- O nome correto será `id_dezena`.
- `media_oco` e `mediana_oco` serão campos separados.
- Média, mediana e desvio de ocorrências serão calculados sobre os intervalos.
- `frequencia_de_resultado` manterá uma linha para cada dezena de 01 a 60.
- As 60 linhas serão recalculadas na mesma transação de alterações em
  `resultados`.
- A tabela de frequência terá `versao_calculo` e `atualizado_em`.
- `schema_migrations` registrará o checksum SHA-256 de cada migração.
- O modelo aprovado está em `docs/MODELO_POSTGRESQL.md`.

## 2026-10-26 — DDL inicial validado

- A migração inicial se chama `001_criar_estrutura_inicial.sql`.
- O esquema completo e a migração possuem conteúdo equivalente.
- O DDL foi validado em PostgreSQL 16.11 temporário e isolado.
- Os testes não autorizam execução no banco persistente ou no PythonAnywhere.
- As evidências estão em `database/TESTE_DDL_ITEM_1_4.md`.

## 2026-10-26 — Conexão PostgreSQL pelo Python

- O driver será Psycopg 3 com distribuição binária e faixa de versão
  `>=3.3.6,<4`.
- A configuração usará exclusivamente variáveis `GAME_DB_*`.
- Host, database, usuário e senha não terão valores implícitos.
- Arquivos `.env` continuarão ignorados; `.env.example` conterá apenas exemplos.
- Mensagens de conexão não reproduzirão mensagens brutas que possam conter
  credenciais.
- O Item 4.1 não cria databases, tabelas ou dados.

## 2026-10-26 — Executor de migrações

- Migrações seguem o padrão `NNN_nome.sql` e são ordenadas numericamente.
- O SHA-256 é calculado sobre os bytes originais do arquivo.
- Alterar uma migração registrada interrompe a inicialização.
- Cada migração e seu registro são confirmados ou revertidos juntos.
- Uma trava consultiva PostgreSQL serializa execuções simultâneas.
- `BEGIN` e `COMMIT` externos são removidos somente em memória para que o Python
  controle a atomicidade; o arquivo SQL permanece inalterado.

## 2026-10-26 — Repositório de resultados

- O SQL de `resultados` fica restrito à camada `database`.
- Inserção exige `ResultadoCalculado`; atualização exige `ResultadoEntrada` e
  recalcula todos os campos derivados.
- Cada método usa uma transação e participa de uma transação externa quando ela
  existir, permitindo rollback de operações compostas.
- A listagem inicial usa `numero_ap` crescente e paginação por limite e
  deslocamento.
- Divergências de importação não são atualizadas automaticamente.

## 2026-10-26 — Framework da API

- O framework será Flask 3.1, inicialmente fixado em `>=3.1.3,<4`.
- A aplicação usa o padrão de fábrica para permitir configurações e instâncias
  independentes em testes.
- Flask foi preferido porque a API é pequena, a persistência atual é síncrona e
  o PythonAnywhere fornece integração WSGI direta.
- FastAPI exigiria uma camada ASGI ou adaptação adicional no ambiente planejado;
  Django acrescentaria componentes que o escopo atual não necessita.
- O servidor de desenvolvimento nunca será iniciado durante a importação WSGI.

## 2026-10-26 — Desenvolvimento local antes da publicação

- Todas as funcionalidades serão desenvolvidas, integradas e testadas primeiro
  no computador local.
- O PostgreSQL local `games` será o ambiente de desenvolvimento atual.
- O PythonAnywhere não receberá código, DDL, migração ou dados durante as etapas
  locais.
- A publicação será uma fase posterior, iniciada somente após conclusão, testes,
  backup e autorização explícita do usuário.

## 2026-10-26 — Banco fora do versionamento Git

- Arquivos físicos do PostgreSQL, dumps, backups e relatórios locais não entram
  no Git.
- `.env` e qualquer credencial permanecem somente no ambiente local.
- `schema_postgresql.sql` e `database/migrations/*.sql` entram no Git porque são
  código reprodutível da estrutura, não o database nem seus dados.
- `Game.code-workspace` fica ignorado porque referencia provisoriamente o FinCtl.

## 2026-10-26 — Navegação do painel

- Sem resultados, seleção, navegação, voo e mancha ficam desabilitados.
- Com um resultado, seleção e mancha ficam disponíveis; Anterior, Próximo e
  Voo ficam desabilitados porque não existe outro item para apresentar.
- Com dois ou mais resultados, Anterior e Próximo usam navegação circular: o
  anterior ao primeiro é o último, e o próximo ao último é o primeiro.
- O seletor de fonte aceita somente `.xlsx`, em conformidade com a API.

## 2026-10-27 — Grupos de padrões e navegação compacta

- Os padrões serão organizados em `padroes_grupo` e `padroes_subgrupo`, ligados
  por chave estrangeira obrigatória.
- Um grupo com padrões não poderá ser excluído.
- Nomes de grupos serão únicos sem diferenciar maiúsculas, minúsculas e espaços
  externos; nomes de padrões seguirão a mesma regra dentro de cada grupo.
- Estatísticas continuarão pertencendo aos padrões, não aos grupos.
- A aplicação separará Painel e Cadastros usando uma única barra horizontal,
  submenu flutuante e botão Voltar na mesma linha.
- Grades deverão conter sua própria rolagem e priorizar largura para nomes e
  descrições.

## 2026-10-26 — Testes reais de navegador

- Playwright 1.64.1 é a ferramenta de testes funcionais do frontend.
- Os testes locais reutilizam o Google Chrome instalado e não baixam outro
  navegador.
- A camada de interface simula as respostas HTTP para testar o navegador sem
  modificar o PostgreSQL; a integração com o banco pertence à Etapa 7.
- `node_modules`, `test-results` e `playwright-report` não são versionados.

## 2026-10-28 — Auditoria usa as funções reais do sistema

- Todo valor apresentado na auditoria será produzido pela mesma função de
  produção usada no screener, na persistência ou na análise correspondente.
- Não haverá cópia da fórmula no frontend nem função paralela exclusiva para
  produzir valores do relatório.
- As funções de produção fornecerão valor e evidências da mesma execução.
- A tela de auditoria apenas organizará as evidências para conferência humana.
- Testes deverão provar a igualdade entre valor auditado, valor persistido e
  valor utilizado na decisão do funil.

## 2026-10-28 — Cadastro de padrão não cria função de filtro

- O cadastro organiza grupo, padrão, descrição e estatísticas; ele não gera
  lógica Python automaticamente.
- Cada novo grupo de padrões precisa de uma função classificadora Python,
  testes automatizados, versão de cálculo e integração explícita ao registro.
- Um grupo sem classificador não participa do screener e deve aparecer como
  indisponível, nunca como padrão que não ocorreu.
- Somente após a classificação histórica e sua fotografia a frequência poderá
  definir quais subgrupos são candidatos à exclusão.

## 2026-10-29 — Incidência histórica e seleção dos padrões raros

- O percentual de cada padrão usa todos os sorteios válidos como denominador:
  `num_oco / total_sorteios * 100`.
- Um resultado que não corresponda aos padrões estudados não cria classe,
  registro ou filtro complementar; `SEM_CORRESPONDENCIA` foi removido.
- Quantidade, denominador e percentual atuais são atualizados na própria linha
  do padrão, sem criar séries históricas a cada recálculo.
- O screener consulta somente padrões com detector Python aprovado e
  `percentual_ocorrencia < limite_configurado`; igualdade não seleciona.
- Somente os padrões retornados pela consulta aparecem no relatório e são
  executados. Ausência significa que o padrão não foi eleito.
- Novos padrões exigem detector Python, testes, integração ao registro e
  recálculo histórico antes de poderem participar do screener.
- O processamento das 50.063.860 combinações permanece bloqueado; por enquanto
  somente a amostra reproduzível de 5.000 está autorizada.

## 2026-10-29 — Consolidação da interface do Screener

- Existe somente um Screener público: `/screener.html`.
- Sua única rota de execução é `POST /api/screener/quadro`.
- O relatório apresenta as famílias estatística, geométrica e de padrões em um
  conjunto único, com detalhes expansíveis.
- O protótipo fictício, a interface anterior e suas rotas não fazem parte do
  produto atual.
- O cálculo do primeiro funil permanece apenas como referência interna da
  comparação `anterior x atual`; não possui tela nem API própria.
- A página `/auditoria.html` permanece vazia e reservada à Etapa 20.
