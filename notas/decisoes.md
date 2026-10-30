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

## 2026-10-29 — Homologação das funções e comunicação de operações demoradas

- `amostras_validacao` relacionará por FK os primeiros 200 registros de
  `resultados`, ordenados por `numero_ap`, sem repetir as seis dezenas.
- `id_resultado` será PK/FK e usará `ON DELETE CASCADE`; as amostras são uma base
  de teste, não um arquivo histórico independente.
- O catálogo de critérios crescerá por sincronização com o registro das funções
  Python realmente executáveis; cadastro textual sem função não será incluído.
- Cada avaliação relacionará amostra e função, com esperado independente,
  calculado pela função real e aprovação `S/N`.
- Critérios de padrões relacionarão grupo e subgrupos esperado/calculado; a tela
  mostrará códigos e nomes legíveis por `JOIN`.
- O recálculo nunca sobrescreverá o esperado. Mudança apenas da implementação
  preserva esperados; mudança da regra matemática exige novas referências.
- Critérios excluídos serão removidos com suas avaliações por cascata.
- Critério ou padrão novo/alterado exige função Python e testes locais no VS
  Code antes de ser reconhecido pelo botão de sincronização e recálculo.
- A assinatura da implementação será automática. Função nova, alterada,
  pendente ou com qualquer `N` ficará bloqueada no Screener; somente a função
  que acertar todas as amostras ativas poderá ser utilizada.
- O relatório resumirá a homologação por função e detalhará cada divergência; a
  IA poderá propor diagnóstico sem corrigir ou aprovar automaticamente.
- A publicação na nuvem ocorrerá somente depois da validação local.
- A Validação e auditoria será a primeira área a usar modal com progresso real.
- O mesmo conceito será levado ao Screener em etapa posterior e separadamente
  autorizada.

## 2026-10-29 — Documentação canônica e reconciliação por etapa

- `docs/funcionamento.md` será a descrição funcional vigente de ponta a ponta.
- `docs/INDICE_DOCUMENTACAO.md` indicará onde localizar plano, decisões,
  funcionamento, continuidade, banco, contratos e evidências.
- Cada subetapa continuará registrando plano, teste e continuidade.
- Toda etapa funcional terminará com revisão integral do funcionamento e dos
  documentos de banco/API afetados; na Etapa 20 isso será a subetapa 20.17.
- Documento antigo divergente deverá ser atualizado ou identificado como
  histórico; não poderá continuar parecendo uma regra vigente.

## 2026-10-29 — Homologação estável e perfis operacionais atuais

- As 200 avaliações serão refeitas quando mudar implementação, fórmula,
  precisão ou significado da função, conforme a natureza da alteração.
- A importação de resultados não invalida uma função inalterada. Ela recalcula
  grandezas, classificações, incidências e perfis estatísticos e geométricos
  atuais usando todos os resultados válidos disponíveis.
- Perfis operacionais anteriores não serão preservados como versões. O backtest
  reconstruirá os valores aplicáveis ao corte por concurso ou data.
- O usuário verá somente `Algoritmo de seleção de combinações atualizado` ou
  `Algoritmo de seleção de combinações desatualizado`. Perfil incompleto,
  quantidade divergente ou validação pendente bloqueará o Screener.
- O Screener carregará todos os filtros estatísticos e geométricos aprovados e
  somente os padrões aprovados selecionados pela incidência inferior ao limite.
  Diferença entre filtros esperados e carregados bloqueará a API.

## 2026-10-30 — Oráculo geométrico independente da subetapa 20.7

- Shapely 2.2.0/GEOS será dependência somente de desenvolvimento/teste.
- As 1.200 referências geométricas iniciais foram produzidas sem importar ou
  chamar as funções geométricas de produção.
- O Shapely não será usado pelo Screener; as funções reais continuarão sendo o
  objeto da aferição contra as referências protegidas.

## 2026-10-30 — Execução estatística da subetapa 20.8

- A execução recusa catálogo divergente, assinatura desatualizada ou referência
  pendente antes de gravar resultados.
- O cálculo pode atualizar somente os campos calculados e de comparação; os
  campos do esperado permanecem protegidos e tiveram seu hash conferido.
- Um critério recebe `APROVADO` somente com `S` em todas as amostras ativas.
- A aprovação de uma categoria não libera o algoritmo geral enquanto houver
  outra categoria pendente.

## 2026-10-30 — Precisão da homologação geométrica na subetapa 20.9

- A decisão `S/N` de critérios decimais respeitará `precisao_decimal` cadastrada
  e usará `ROUND_HALF_UP` em esperado e calculado.
- O arredondamento será aplicado somente para comparação; o valor bruto da
  função real permanecerá armazenado para auditoria.
- Diferenças além da precisão declarada não reprovam uma função; diferenças que
  atinjam a precisão declarada continuam produzindo `N`.

## 2026-10-30 — Execução dos padrões na subetapa 20.10

- Cada critério de padrão continuará ligado ao grupo e ao subgrupo `PD_xxx`
  correspondente; retorno verdadeiro grava esse `id_padrao` e retorno falso
  grava ausência de correspondência.
- Estado e identificador calculados devem coincidir com a referência para gerar
  `S`; nomes legíveis serão obtidos por `JOIN` com grupo e subgrupo.
- A aprovação dos 19 critérios não libera isoladamente o algoritmo geral; a
  reconciliação completa continuará pertencendo às subetapas seguintes.

## 2026-10-30 — Motor integrado da subetapa 20.11

- Sincronização, criação de pares faltantes, três famílias de execução e
  consolidação formarão uma única transação lógica.
- Uma função com qualquer referência pendente ficará inteiramente `PENDENTE`,
  sem impedir o recálculo de outras funções completas.
- Uma única divergência marca a função `REPROVADO`; aprovação exige `S` em todas
  as amostras ativas.
- Homologação completa grava
  `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`, não `atualizado = TRUE`.

## 2026-10-30 — Andamento assíncrono da subetapa 20.12

- A execução de validação terá identificador e estado consultável por API; o
  percentual será derivado de etapas reais, nunca de animação temporal.
- Somente uma execução poderá ficar ativa; nova tentativa receberá conflito.
- O modal reutilizável não poderá fechar durante a tarefa e exibirá eventual
  erro terminal. Cancelamento só será acrescentado quando houver interrupção
  transacional segura.
- O componente estreia na Validação e auditoria; sua adoção pelo Screener exige
  autorização posterior.

## 2026-10-30 — Página de Validação e auditoria da subetapa 20.13

- A grade será paginada no servidor e limitada a 100 linhas por consulta.
- Dezenas, grupos e subgrupos continuarão obtidos por `JOIN`; a interface não
  criará cópia desses dados.
- Os filtros oficiais serão categoria, função, grupo, subgrupo e situação.
- O botão de atualização aparecerá quando o estado global estiver desatualizado
  e reutilizará o motor e o modal já aprovados.

## 2026-10-30 — Relatório de divergências da subetapa 20.14

- O fechamento será calculado diretamente das avaliações ativas e deverá
  satisfazer `exigidas = aprovadas + divergentes + pendentes`.
- Inclusões, exclusões e mudanças detectadas pertencem ao resultado da última
  atualização; o estado persistente por função continua vindo do catálogo.
- A hipótese diagnóstica da IA é texto explicativo determinístico e não tem
  permissão para alterar esperado, calculado, implementação ou aprovação.

## 2026-10-30 — Exportação reproduzível da subetapa 20.15

- O identificador do conjunto é o SHA-256 do JSON canônico dos registros e não
  inclui o horário da exportação.
- O JSON é o formato técnico reabrível e verificável; o CSV é uma projeção
  tabular para conferência humana e repete o identificador em cada linha.
- Toda célula CSV com prefixo interpretável como fórmula será precedida por
  apóstrofo. A importação do JSON nunca executará conteúdo armazenado.

## 2026-10-30 — Trava operacional do Screener da subetapa 20.16

- Estado global desatualizado bloqueia antes da construção dos adaptadores;
  aprovação das 200 amostras, isoladamente, não libera o Screener.
- O catálogo ativo deve coincidir com o registro Python de produção, inclusive
  assinaturas de função e regra.
- Todos os filtros estatísticos e geométricos devem estar cobertos; para padrões,
  a cobertura executável contém exatamente os selecionados pelo limite vigente.
- Perfis operacionais devem conter os dez códigos esperados e a mesma quantidade
  de resultados do estado global e da tabela `resultados`.
- A regressão não alteraá artificialmente o flag do banco `games` para obter
  sucesso; enquanto faltar confirmação de cobertura, a recusa é obrigatória.

## 2026-10-30 — Fechamento documental da Etapa 20

- `docs/funcionamento.md` é a narrativa funcional canônica; planos antigos
  preservados como histórico não definem o comportamento atual.
- `SEM_CORRESPONDENCIA` continua removido da classificação histórica, mas é um
  estado válido e distinto nas avaliações de classificadores da validação.
- O estado real bloqueado do Screener deve constar da documentação; 3.800
  aprovações não autorizam forçar o flag global.
- Commit e push permanecem operações separadas e exigem autorização explícita.

## 2026-10-30 — Contrato matemático da frequência das dezenas

- Cada fotografia usa somente concursos até seu próprio corte, sem consultar o
  futuro.
- Ocorrência simples é representada pelo concurso em que a dezena apareceu.
- Um evento 2VS termina no segundo concurso consecutivo e um evento 3VS termina
  no terceiro.
- As sequências usam janelas consecutivas sobrepostas: três concursos seguidos
  produzem dois eventos 2VS e um 3VS; quatro produzem três 2VS e dois 3VS.
- Intervalos são diferenças entre concursos de conclusão do mesmo tipo de
  evento; tipos diferentes nunca são misturados.
- Média, mediana e desvio populacional são calculados sobre os intervalos e
  permanecem na unidade concurso.
- Sem intervalo, as estatísticas são `NULL`; com um único intervalo, o desvio é
  zero.
- A faixa inicial é a última conclusão mais a média, com mais ou menos um
  desvio-padrão. Limites inteiros são inclusivos e arredondados para fora.
- Percentuais continuam fora desta etapa e serão estudados em Distribuições.
- O contrato completo está em `docs/CONTRATO_FREQUENCIA_DEZENAS.md`.

## 2026-10-30 — Configuração reproduzível da frequência das dezenas

- A configuração gravada é uma linha ativa única, comparada com a configuração
  calculada antes de qualquer substituição futura.
- A configuração inicial usa concurso 1, tamanho 500, início fixo e final
  expansivo.
- `TODOS` representa o cálculo conjunto de ocorrências simples, 2VS e 3VS;
  também são aceitos os três tipos individualmente para experiências futuras.
- Método, parâmetro, unidade e arredondamento são campos distintos e explícitos.
- O parâmetro inicial é `1.000000` na unidade
  `MULTIPLICADOR_DESVIO_PADRAO`; percentual permanece recusado até o estudo em
  Distribuições.
- A assinatura é o SHA-256 do JSON canônico de todos os campos funcionais. A
  comparação também lista campo e valores divergentes para interpretação do
  usuário.

## 2026-10-30 — Estrutura histórica da frequência das dezenas

- Fotografias pertencem a uma geração; uma geração provisória pode ser
  construída sem retirar a anterior antes da conclusão.
- Apenas uma geração pode estar ativa.
- Cada geração preserva assinatura e JSON canônico da configuração.
- A chave funcional da fotografia é geração, concurso, dezena e tipo de evento.
- Limites decimais exatos e concursos inteiros operacionais são distintos.
- A tabela não repete as seis dezenas de `resultados` e não possui FK que apague
  apenas um corte quando um resultado antigo mudar; a reconstrução integral
  pertence às etapas posteriores.
- `ON DELETE CASCADE` existe somente da geração para suas fotografias.

## 2026-10-30 — Motor acumulado da frequência das dezenas

- O motor recebe concursos estritamente consecutivos; lacuna ou retrocesso
  interrompem o cálculo para não produzir uma série falsa.
- Cada concurso é incorporado antes de sua fotografia ser emitida.
- 2VS começa no segundo concurso seguido e 3VS no terceiro; sequências maiores
  continuam gerando janelas sobrepostas.
- O estado incremental mantém somente dados conhecidos até o corte atual.
- Média e desvio são calculados com precisão interna elevada; o armazenamento
  recebe seis casas decimais com `ROUND_HALF_UP`.
- O multiplicador do desvio é adimensional. Nenhum valor de desvio em concursos
  é reinterpretado como percentual.
- Carga integral e processamento parcelado devem produzir fotografias idênticas.

## 2026-10-30 — Carga e atualização do histórico de frequência

- Cada geração guarda assinatura e quantidade dos resultados que a originaram.
- A atualização compara a assinatura do prefixo já processado; concursos novos
  não invalidam esse prefixo.
- No acréscimo incremental, os concursos antigos apenas recompõem o estado do
  motor em memória; somente os novos cortes são calculados para saída e gravados.
- Mudança antiga, lacuna, origem encurtada ou incompatibilidade impedem
  acréscimo silencioso e exigem reconstrução.
- A geração provisória e todas as suas linhas pertencem à mesma transação. A
  geração antiga só é retirada no instante da troca bem-sucedida.
- Depois da troca, somente a geração detalhada nova é mantida.
- O benchmark inicial com 3.069 resultados produziu 462.600 linhas em cerca de
  150 segundos e ocupou aproximadamente 122 MiB; otimizações serão avaliadas a
  partir dessa referência, sem alterar previamente a regra matemática.

## 2026-10-30 — Confirmação e simulação da frequência das dezenas

- `Salvar dados` inicia marcado em cada abertura, sem ser memorizado
  silenciosamente.
- A gravação depende de confirmação tanto na interface quanto no serviço do
  servidor; uma requisição sem confirmação é recusada.
- A simulação executa o mesmo motor, mas não cria geração, não substitui
  configuração e não insere fotografias.
- A prévia lista concursos novos na atualização incremental e campos com valores
  gravado/calculado quando a configuração divergir.
- Cancelamento ocorre somente entre unidades seguras de trabalho. Como toda a
  gravação pertence a uma transação, linhas parciais são revertidas.
- Somente uma operação de frequência pode executar por vez.

## 2026-10-30 — API da frequência das dezenas

- A fotografia atual sempre representa as 60 dezenas da geração ativa.
- Cada consulta de série histórica aceita uma dezena, um tipo de evento e um
  período máximo de 5.000 concursos; a API não envia séries alheias ao gráfico
  solicitado nem repete as seis dezenas de `resultados`.
- Valores decimais são enviados como texto para preservar a precisão do banco.
- A configuração recebida deve conter exatamente todos os campos funcionais;
  campos ausentes, extras ou valores fora do contrato são recusados.
- Uma solicitação que grave dados é recusada antes de criar a tarefa se não
  trouxer confirmação explícita.
- A execução é assíncrona, tem progresso consultável e cancelamento
  cooperativo; somente uma execução pode permanecer ativa.
- Falha de conexão nas consultas síncronas é devolvida de forma controlada com
  HTTP 503, em vez de uma página HTML interpretada incorretamente como JSON.

## 2026-10-30 — Página da frequência das dezenas

- `Frequência das dezenas` é um item próprio da navegação comum e abre
  `/frequencias.html`.
- A página separa visualmente a configuração gravada da configuração que será
  usada no próximo cálculo; qualquer alteração invalida a prévia anterior.
- `Salvar dados` inicia marcado em cada abertura. A execução calcula a prévia e
  exige a confirmação aprovada antes de solicitar gravação ao servidor.
- Com `Salvar dados` desmarcado, o mesmo fluxo executa simulação sem persistir.
- Progresso, resultado, erro e cancelamento usam o modal compartilhado.
- Os gráficos não foram antecipados: fotografia atual e histórico continuam
  reservados às subetapas 22.9 e 22.10.
- Em janelas de até 50 rem, a navegação comum passa a ter rolagem horizontal
  própria, sem alargar o documento.

## 2026-10-30 — Gráficos da fotografia atual das dezenas

- A fotografia dos gráficos vem do último concurso da geração ativa, inclusive
  para ocorrências simples; assim, todos os tipos usam o mesmo corte temporal.
- A API devolve as 60 dezenas de um único tipo por chamada: `SIMPLES`, `2VS` ou
  `3VS`. Não são feitas 60 consultas HTTP individuais.
- São exibidos seis gráficos: ocorrências, intervalo mínimo, intervalo máximo,
  média, mediana e desvio-padrão dos intervalos.
- Número de ocorrências usa unidade `ocorrências`; todas as medidas de intervalo
  usam `concursos`. Desvio-padrão não é apresentado como percentual.
- Medidas sem intervalos suficientes continuam nulas e são identificadas como
  ausência de amostra, sem conversão indevida para zero.
- Cada barra identifica dezena, valor e quantidade de intervalos; o cabeçalho
  informa corte, total de intervalos e atualização.

## 2026-10-30 — Gráfico histórico por dezena

- A série histórica aceita uma dezena, um tipo de evento e até 5.000 concursos
  por consulta; não serão sobrepostas as 60 dezenas no mesmo gráfico.
- O eixo horizontal é sempre `numero_do_concurso`.
- Intervalos e números previstos de concursos possuem escalas diferentes e são
  exibidos em dois gráficos sincronizados, sem mistura de unidades.
- O primeiro gráfico apresenta intervalo mínimo, médio e máximo na unidade
  concurso. O segundo apresenta faixa inferior, previsão central, faixa
  superior e pontos de ocorrência real na escala dos números dos concursos.
- Ocorrências reais vêm diretamente de `resultados`: presença no concurso para
  `SIMPLES`, presença também no concurso imediatamente anterior para `2VS` e
  presença nos dois concursos imediatamente anteriores para `3VS`.
- Os pontos reais não são copiados para a tabela histórica nem usados para
  refazer cálculos de cortes passados; servem somente como sobreposição visual.
- Contagem formal de acertos, erros e percentuais continua pertencendo à 22.11.

## 2026-10-30 — Avaliação da assertividade da frequência

- Cada fotografia prevê o primeiro evento real estritamente posterior ao seu
  corte. O evento no próprio corte é a última informação conhecida, não o
  retorno futuro avaliado.
- Acerto significa ocorrência real dentro dos limites inteiros inclusivos.
  Falhas são separadas em abaixo e acima da faixa.
- Erro absoluto é `abs(concurso_real - previsao_central)` em concursos.
- Erro percentual é o erro absoluto dividido pelo intervalo real entre o último
  evento conhecido e o próximo evento, multiplicado por 100. O número absoluto
  do concurso não é usado como denominador.
- Sem evento anterior, sem estatística completa ou sem próximo evento conhecido,
  a previsão é censurada e fica fora dos totais de acertos e erros.
- A página apresenta totais e médias e lista somente previsões avaliáveis que
  ficaram fora da faixa; censurados permanecem contabilizados no resumo.
- A avaliação é calculada sobre a série e os resultados existentes, sem gravar
  resultado de avaliação nem modificar fotografias históricas.

## 2026-10-30 — Fechamento e desempenho da frequência das dezenas

- A referência local com 3.069 resultados gerou 2.570 cortes e 462.600 linhas.
- A carga completa mediu 146,761 s e o acréscimo de um concurso, com 180 linhas,
  mediu 0,189 s.
- As três fotografias atuais mediram juntas 0,003 s. Uma série de 2.571 pontos,
  incluindo assertividade, mediu 0,057 s.
- Tabela e índices ocuparam 127.811.584 bytes; os índices responderam por
  71.688.192 bytes.
- As medições são referência do equipamento e banco locais, não compromisso de
  desempenho em outro ambiente.
- A Etapa 22 termina sem ativar o módulo como filtro do Screener e sem executar
  commit ou push.
