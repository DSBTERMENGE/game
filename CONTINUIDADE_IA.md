# Continuidade entre sessões da IA

## Como usar este arquivo

Este é o primeiro arquivo que uma nova sessão deve ler, seguido de
`PLANO_DO_PROJETO.md`, `notas/decisoes.md` e do documento específico da etapa.
Ao terminar uma sessão relevante, atualizar as seções “Último trabalho” e
“Próxima ação”. Não registrar senhas, tokens ou outras credenciais aqui.

## Identidade e objetivo

- Projeto: Game / MSen.
- Repositório: `C:\Applications_DSB\Game`.
- Aplicação: organização e análise do histórico da Mega-Sena.
- Banco planejado: PostgreSQL, database `games`.
- Ambientes previstos: desenvolvimento local e PythonAnywhere.
- Ordem dos ambientes: concluir e aprovar todo o desenvolvimento local antes de
  iniciar qualquer preparação ou publicação no PythonAnywhere.
- Ordem dos ambientes: concluir e aprovar todo o desenvolvimento local antes de
  iniciar qualquer preparação ou publicação no PythonAnywhere.

## Regras permanentes

1. O FinCtl, em `C:\Applications_DSB\FinCtl`, é somente referência externa.
   Nunca incluí-lo no Git do Game nem copiar seus dados ou credenciais.
2. O repositório Git termina na pasta `Game`.
3. O banco físico, dumps, backups, relatórios locais e credenciais não são
   versionados. Somente o modelo reproduzível (`schema_postgresql.sql`) e as
   migrações SQL pertencem ao Git.
4. Não executar comandos no banco local ou remoto sem conferir banco, usuário,
   ambiente e efeito da operação.
5. Não publicar, criar commit ou alterar o PythonAnywhere sem pedido explícito.
6. Preservar a planilha original em `MSen/dados/fontes`.
7. Ideias de `notas/ideias.md` não estão automaticamente aprovadas.
8. Registrar decisões arquiteturais em `notas/decisoes.md`.
9. Seguir `PLANO_ETAPAS_E_TESTES.md`: executar somente o item autorizado, testar,
   relatar a conclusão e pedir autorização antes do item seguinte.

## Estado atual em 2026-10-25

- Existe um pacote Python mínimo em `MSen/src/msen`.
- Existe apenas um teste simples para o ponto de entrada.
- O DDL da tabela `resultados` está em `database`, mas ainda não foi executado
  em nenhum servidor PostgreSQL por este projeto. Ele ainda representa o modelo
  anterior e deverá ser revisado antes da execução para incluir identificador,
  número da apresentação e os campos calculados recém-definidos.
- Nenhuma dependência de banco foi adicionada ao `pyproject.toml`.
- A planilha disponível contém concurso, data e seis bolas; o cabeçalho está na
  linha 7 e os dados começam na linha 8. Ela está em `MSen/dados/fontes`.
- A interface está organizada em `frontend/index.html`, `frontend/css` e
  `frontend/js`, ainda sem integração com Python.
- O FinCtl foi adicionado ao workspace apenas para consulta.
- `Game.code-workspace` referencia `../FinCtl` e não deve ser incluído no commit
  enquanto essa referência temporária permanecer.
- O backend compartilhado já menciona o app `game`, mas contém configuração de
  senha inadequada e uma variável incorreta (`INVCTL_PG_PASSWORD` no bloco do
  Game). Não copiar esse padrão inseguro.

## Último trabalho realizado

- Inspeção somente leitura da organização do Game, FinCtl e backend
  compartilhado.
- Criação do plano geral, plano do banco, plano do Python e deste documento.
- Ampliação dos arquivos de funcionalidades e ideias.
- Organização dos arquivos da interface na pasta `frontend`, com atualização
  dos caminhos usados pelo HTML.
- Nenhum código Python, DDL, banco ou ambiente remoto foi alterado.
- A tentativa de executar os testes em 2026-10-25 não iniciou porque `pytest`
  não está instalado no ambiente Python atual.
- Foram criados `database/schema_postgresql.sql` e a migração inicial, depois
  substituída por `001_criar_estrutura_inicial.sql` no Item 1.4. O cliente
  `psql` 16.11 existe fora do `PATH`; o servidor local exige senha e não foi
  alterado.
- As regras iniciais de cálculos, frequências, intervalos e gráficos foram
  registradas em `docs/funcionamento.md` e `notas/funcionalidades.md`.
- A grade foi definida no sistema lógico `(0; 0)` a `(9; 5)`. A média espacial
  aceita decimais e será convertida em pixels a partir dos centros reais das
  células. Foram definidos os modos animação de 0,5 segundo e mancha acumulada.
- Foi criado `docs/PLANO_FUNCIONALIDADES.txt`, consolidando banco, módulos
  Python, matemática, gráficos e importação incremental de planilhas Excel.
- O frontend agora possui painel de comandos, navegação, tempo configurável,
  voo dos pássaros e mancha. A seleção do Excel chama as rotas planejadas
  `POST /api/resultados/importar` e `GET /api/resultados`, ainda inexistentes.
- Em 2026-10-26, a fonte Excel foi movida para `MSen/dados/fontes` sem alteração:
  tamanho de 129646 bytes e SHA-256
  `027726F33A89738AD9DC95FAC9A7ECCD390609F5C63CACBB2F00B3873724CE67`.
- Foi criado `PLANO_ETAPAS_E_TESTES.md`, que passa a controlar a execução item a
  item, sempre com teste e nova autorização antes de avançar.

## Próxima ação recomendada

O Item 2.1 foi concluído em 2026-10-26. O código Python está separado em
`MSen/src/msen/modelos/resultado.py`, com modelo imutável, normalização de data,
validações e erros identificados por código. Os 15 testes de
`MSen/tests/test_resultado.py` passaram com `unittest`.

O Item 2.2 foi concluído em 2026-10-26. As funções puras `calcular_soma`,
`calcular_media_aritmetica` e `calcular_mediana` estão em
`MSen/src/msen/calculos/estatisticas_linha.py`. Seis testes específicos e 21
testes acumulados passaram.

O Item 2.3 foi concluído em 2026-10-26. O desvio-padrão populacional usa
`Decimal`, precisão interna de 50 algarismos e `ROUND_HALF_UP` somente no final.
Nove testes específicos e 30 testes acumulados passaram.

O Item 2.4 foi concluído em 2026-10-26. Coordenadas e média espacial estão em
`MSen/src/msen/calculos/coordenadas.py`. O exemplo decimal
`(2,000000; 4,333333)` foi confirmado. Dez testes específicos e 40 testes
acumulados passaram.

O Item 2.5 foi concluído em 2026-10-26. A análise histórica está em
`MSen/src/msen/calculos/frequencias.py` e devolve 60 resumos com ocorrências,
intervalos, média, mediana e desvio-padrão. Treze testes específicos e 53 testes
acumulados passaram.

O Item 2.6 foi concluído em 2026-10-26. Quatro testes integrados, 57 testes
acumulados, comparação independente com `statistics` e compilação em memória de
15 arquivos passaram. A Etapa 2 está concluída.

O Item 3.1 foi concluído em 2026-10-26. `openpyxl>=3.1.5,<4` e
`defusedxml>=0.7.1,<1` foram registrados em `MSen/pyproject.toml`. Seis arquivos
controlados estão em `MSen/tests/fixtures`; todos abriram em modo somente
leitura, e a fonte original manteve o SHA-256 documentado.

O Item 3.2 foi concluído em 2026-10-26. O leitor em
`MSen/src/msen/importacao/excel.py` abre `.xlsx` em modo somente leitura,
localiza as oito colunas sem depender da linha 7 e entrega objetos
`ResultadoEntrada`. A fonte real produziu 3.069 registros e manteve seu hash.
Sete testes específicos e 64 acumulados passaram.

O Item 3.3 foi concluído em 2026-10-26. `calcular_resultado` concentra todos os
cálculos aprovados em um `ResultadoCalculado`, e
`ler_resultados_calculados_excel` aplica a mesma composição a todas as linhas
importadas. A equivalência com a entrada manual foi confirmada. Seis testes
específicos e 70 acumulados passaram.

O Item 3.4 foi concluído em 2026-10-26. A comparação incremental está em
`MSen/src/msen/importacao/comparacao.py` e classifica linhas como `NOVA`,
`IGUAL`, `ALTERADA` ou `INVALIDA`, sem modificar origem ou existentes. Dados
originais definem igualdade; mudança isolada da versão de cálculo não representa
divergência da fonte. Oito testes específicos e 78 acumulados passaram.

O Item 3.5 foi concluído em 2026-10-26. A fonte real foi lida integralmente em
modo somente leitura: 3.069 linhas válidas, zero inválidas, concursos únicos de
1 a 3069, primeiro concurso 3069 na linha 8 e último concurso 1 na linha 3076.
Tamanho e SHA-256 permaneceram iguais. Cinco testes específicos e 83 acumulados
passaram. A Etapa 3 está concluída.

O Item 4.1 foi concluído em 2026-10-26. `MSen/src/msen/config.py` valida as
variáveis `GAME_DB_*`, e `MSen/src/msen/database/connection.py` abre e verifica
conexões usando Psycopg 3.3.6 sem incluir a senha em mensagens. Nove testes
específicos e 92 acumulados passaram. A conexão válida e o banco inexistente
foram testados num cluster PostgreSQL 16.11 temporário, depois parado e removido.
Os serviços persistentes não foram alterados.

O Item 4.2 foi concluído em 2026-10-26. O executor em
`MSen/src/msen/database/migrations.py` descobre e ordena arquivos, valida
checksum, aplica SQL e registro atomicamente e usa `pg_advisory_lock` contra
concorrência. Oito testes específicos e 100 acumulados passaram; banco vazio,
banco atualizado, rollback, checksum divergente e duas execuções concorrentes
foram aprovados em PostgreSQL 16.11 temporário. O cluster foi removido.

O Item 4.3 foi concluído em 2026-10-26. O repositório em
`MSen/src/msen/database/repositories.py` insere, busca, atualiza e lista
resultados. A atualização recebe `ResultadoEntrada` e recalcula todos os campos
derivados. Seis testes específicos e 106 acumulados passaram; integração real
confirmou leitura, duplicidade, rollback, recálculo, listagem e ausência em
PostgreSQL 16.11 temporário. O cluster foi removido. Aguardar autorização para o
Item 4.4; não importar a planilha no banco persistente antes de confirmação e
backup.

O Item 4.4 foi concluído em 2026-10-26. A referência do FinCtl confirmou que
PostgreSQL 16.11 usa `127.0.0.1:5432` e usuário `postgres`; o Game recebeu o
database separado `games`. A migração `001`, 3.069 resultados e 60 frequências
foram persistidos. A soma de ocorrências é 18.414 e a reimportação inseriu zero
linhas. Como `games` não existia, não havia backup anterior aplicável. O backup
pós-importação `games_pos_importacao_20261026.dump` foi validado e possui
SHA-256 `96814C5A3D92D15EB9309697F6EF2DFD68526EBDCDE85112181FBEED7B73BA1F`.
O `.env`, os relatórios JSON e o dump estão ignorados pelo Git. A Etapa 4 está
concluída. Aguardar autorização para o Item 5.1.

O Item 5.1 foi concluído em 2026-10-26. Flask 3.1.3 foi escolhido por ser WSGI,
síncrono como a camada Psycopg atual, simples para a API prevista e diretamente
compatível com PythonAnywhere. A fábrica está em `MSen/src/msen/api/app.py`, e
`MSen/wsgi.py` expõe `application` sem iniciar servidor. O endpoint
`GET /api/saude` existe apenas para verificação técnica. Sete testes específicos
e 116 acumulados passaram. Aguardar autorização para o Item 5.2; a rota
`GET /api/resultados` ainda não foi implementada.

O Item 5.2 foi concluído em 2026-10-26. `GET /api/resultados` está em
`MSen/src/msen/api/resultados.py`, usa o repositório PostgreSQL e devolve o
contrato do frontend em ordem crescente. Datas usam ISO e decimais são textos.
Seis testes específicos e 121 acumulados passaram. Teste HTTP local real
retornou 3.069 resultados, do concurso 1 ao 3069, sem alterar a contagem do
banco. O servidor de desenvolvimento foi encerrado. Conforme decisão do usuário,
o primeiro commit completo será preparado somente após fechar a API. O item
seguinte, 5.3, foi posteriormente autorizado e concluído conforme abaixo.

O Item 5.3 foi concluído em 2026-10-26. `POST /api/resultados/importar` recebe
o Excel pelo campo multipart `arquivo`, valida extensão e tamanho, usa arquivo
temporário e chama a importação incremental transacional existente. Sete testes
específicos e 128 acumulados passaram. A reimportação real manteve os 3.069
resultados e uma falha controlada confirmou o rollback. O primeiro commit ficou
adiado até o fechamento da API; o Item 5.4 foi depois autorizado e concluído.

O Item 5.4 foi concluído em 2026-10-26. As rotas de inclusão e edição
individual recalculam todos os derivados e as frequências na mesma transação.
Nove testes específicos e 137 acumulados passaram. A homologação local do
concurso temporário 3070 confirmou inclusão, edição e rollback integral; o
banco voltou a 3.069 resultados. A API planejada está fechada. Conforme decisão
do usuário, o próximo trabalho deverá preparar o primeiro versionamento antes
de iniciar a Etapa 6, mas somente após nova autorização.

O primeiro versionamento foi criado no commit `f8e75c2` e enviado para
`origin/developer`. O Item 6.1 foi concluído em 2026-10-26: cinco testes Node.js
validam o painel, mensagens, seleção e navegação circular; os 137 testes Python
também passaram. Com um único resultado, Anterior, Próximo e Voo ficam
desabilitados. Aguardar autorização para o Item 6.2.

O Item 6.2 foi concluído em 2026-10-26. Cinco testes geométricos adicionais
confirmaram as marcas em 01, 10, 51 e 60, média em centro inteiro, o ponto
decimal `(2; 4,33)`, legibilidade e redimensionamento. A implementação existente
não precisou de correção. Dez testes de frontend e 137 testes Python passaram.
Aguardar autorização para o Item 6.3.

O Item 6.3 foi concluído em 2026-10-26. Cinco testes com relógio controlado
confirmaram intervalo padrão, avanço ordenado, pausa limpa, alteração do tempo,
limites de 0,1 a 30 segundos e redimensionamento durante o voo. Quinze testes de
frontend e 137 testes Python passaram. O PythonAnywhere permanece fora do
escopo até todo o desenvolvimento local e as novas funcionalidades ainda a
serem apresentadas pelo usuário estarem concluídos. Aguardar autorização para o
Item 6.4.

O Item 6.5 foi concluído em 2026-10-26. Playwright 1.64.1 executou três fluxos
no Google Chrome real: carregar/navegar/desenhar, iniciar/pausar o voo e
selecionar Excel/importar com API simulada/desenhar mancha/limpar. Todos
passaram, assim como os dezenove testes unitários de frontend e 137 testes
Python. A Etapa 6 está concluída e este é o ponto de versionamento combinado. O
PythonAnywhere continua fora do escopo; ainda há funcionalidades futuras a
serem fornecidas pelo usuário. Aguardar autorização para versionar a Etapa 6 e,
depois, para o Item 7.1.

Por solicitação do usuário, o Item 7.2 foi executado antes do 7.1 e concluído
em 2026-10-26. O Flask agora entrega frontend e API na mesma origem. O Chrome
carregou os 3.069 resultados reais do PostgreSQL, navegou, executou o voo,
desenhou 18.414 marcas de dezenas e 3.069 médias e limpou a camada. O banco
permaneceu com 3.069 linhas. O Item 7.1 continua pendente e é o próximo passo;
o PythonAnywhere permanece fora do escopo.

O Item 7.1 foi concluído em 2026-10-26 usando database PostgreSQL temporário.
O Chrome selecionou a planilha, a API inseriu dois resultados calculados,
atualizou 60 frequências/12 ocorrências, apresentou o relatório e reimportou sem
duplicar. O database temporário foi removido e `games` permaneceu intacto. Os
dois testes integrados passaram em 8,1 segundos; 19 testes de frontend, 3 testes
Chrome isolados e 140 testes Python também passaram. Aguardar autorização para
o Item 7.3; o PythonAnywhere continua fora do escopo.

O Item 7.3 foi concluído em 2026-10-26. A regressão aprovou 140 testes Python,
19 testes unitários de frontend, 3 fluxos isolados no Google Chrome e 2 fluxos
integrados Chrome/PostgreSQL. O backup local foi restaurado com sucesso em um
database efêmero, contendo 3.069 resultados, 60 frequências e 18.414
ocorrências; o database temporário foi removido. A Etapa 7 está concluída e não
há pendência crítica conhecida no escopo implementado. As alterações da Etapa
7 ainda não foram commitadas. Aguardar autorização para o commit e, depois,
orientação do usuário sobre as próximas funcionalidades. O PythonAnywhere
permanece adiado até a conclusão e aprovação de todo o desenvolvimento local.

Por solicitação do usuário, o Item 7.2 foi executado antes do 7.1 e concluído
em 2026-10-26. O Flask agora entrega frontend e API na mesma origem. O Chrome
carregou os 3.069 resultados reais do PostgreSQL, navegou, executou o voo,
desenhou 18.414 marcas de dezenas e 3.069 médias e limpou a camada. O banco
permaneceu com 3.069 linhas. O Item 7.1 continua pendente e é o próximo passo;
o PythonAnywhere permanece fora do escopo.

O Item 6.4 foi concluído em 2026-10-26. Quatro testes específicos confirmaram a
mancha pequena, reinício das posições quando uma célula lota, desenho de 3.000
resultados dentro dos limites locais e limpeza completa. Dezenove testes de
frontend e 137 testes Python passaram. As alterações dos Itens 6.2 a 6.4 seguem
sem commit por decisão do usuário; o próximo ponto de versionamento será ao
fechar a Etapa 6. Aguardar autorização para o Item 6.5.

A definição de intervalo foi confirmada: é a diferença entre os números das
apresentações. Exemplo: ocorrências da dezena 02 nas apresentações 35 e 50
produzem intervalo 15.

## Pendências conhecidas

Em 2026-10-26 foi planejada a Etapa 9, destinada ao cadastro e à análise de
padrões. O plano divide o trabalho em contrato, migração PostgreSQL, módulo
Python documentado, detectores e estatísticas, persistência, API CRUD, grade com
rolagem e integração local. Toda função pública do novo módulo deverá ter
docstring em português explicando finalidade, parâmetros, retorno e regra. O
screener em funil foi registrado como funcionalidade posterior e não integra a
Etapa 9. A Etapa 8/PythonAnywhere continua adiada. Aguardar autorização expressa
para o Item 9.1.

O Item 9.1 foi concluído em 2026-10-26 e documentado em
`docs/CONTRATO_PADROES.md`. Foram definidos `id_padrao`, `padrao_cod`,
`padrao_nome`, `padrao_descr`, `num_oco`, `intervalo_medio` e `desv_padrao`.
Código, identificador e estatísticas são somente leitura; nome e descrição são
editáveis. `padrao_cod` vinculará o registro ao detector Python, e uma ideia sem
detector não poderá produzir estatística nem participar do screener. Aguardar
autorização expressa para o Item 9.2; nenhuma tabela foi criada ainda.

O Item 9.2 foi concluído em 2026-10-26. A migração `002` criou `padroes` com as
sete colunas e restrições do contrato. O teste temporário confirmou estrutura,
estados estatísticos e rejeições, e o database de teste foi removido. A migração
foi aplicada ao `games` local: 3.069 resultados e 60 frequências foram
preservados, `padroes` ficou vazia e `schema_migrations` contém `001` e `002`.
Passaram 140 testes Python e 2 fluxos Chrome/PostgreSQL. Aguardar autorização
para o Item 9.3; nenhuma alteração foi feita no PythonAnywhere.

O Item 9.3 foi concluído em 2026-10-26. O novo pacote `msen.padroes` contém o
contrato chamável e o registro que vinculará `padrao_cod` às funções. Ele começa
sem detectores, rejeita códigos inválidos e substituições, e diferencia função
pendente de resultado falso. Todas as APIs públicas têm docstrings em português;
7 testes específicos e 147 testes Python acumulados passaram. Aguardar
autorização para o Item 9.4, que deverá começar pela aprovação das regras exatas
de sobreposição das sequências.

O Item 9.4 foi concluído em 2026-10-26. O usuário aprovou classificação
exclusiva pelo maior bloco: exatamente dois (`PD_001`), exatamente três
(`PD_002`) ou mais de três (`PD_003`). Foram criados detectores puros e cálculo
de estatísticas históricas, todos documentados. Passaram 19 testes específicos e
159 testes Python acumulados. Em leitura dos 3.069 resultados, foram encontradas
1.192, 92 e 5 ocorrências respectivamente; `PD_003` apareceu nos concursos 186,
509, 2052, 2789 e 2908. Nada foi persistido. Aguardar autorização para o Item
9.5.

O Item 9.5 foi concluído em 2026-10-26. Repositório e serviço agora cadastram os
três padrões e atualizam somente suas estatísticas, preservando textos editados.
Importação, inclusão e edição de resultados recalculam padrões e frequências na
mesma transação. O `games` contém `PD_001=1192`, `PD_002=92` e `PD_003=5`, com
suas médias e desvios. O teste temporário confirmou idempotência e preservação
do nome; passaram 164 testes Python e 2 fluxos Chrome/PostgreSQL. Aguardar
autorização para o Item 9.6.

O Item 9.6 foi concluído em 2026-10-26. A API CRUD de padrões aceita somente
nome e descrição; código, identificador e estatísticas são protegidos. A
migração `003` cadastrou os padrões iniciais e criou sequência que não reutiliza
códigos excluídos. O recálculo respeita exclusões e ignora estatisticamente
cadastros sem detector. Passaram 10 testes específicos, 174 testes Python e 2
fluxos Chrome/PostgreSQL. Aguardar autorização para o Item 9.7.

O Item 9.7 foi concluído em 2026-10-26. O frontend possui grade CRUD de padrões
com cabeçalho fixo, rolagem, inclusão, edição de nome/descrição, estatísticas
somente para leitura e exclusão confirmada. HTML, CSS e JavaScript estão em
arquivos separados. Passaram 20 testes de frontend, 4 fluxos Chrome simulados,
174 testes Python e 2 fluxos Chrome/PostgreSQL. A integração com `games` apenas
leu os três padrões. Aguardar autorização para o Item 9.8.

O Item 9.8 e a Etapa 9 foram concluídos em 2026-10-26. O fluxo integrado real
em database temporário cobriu histórico, cálculo, persistência, API, grade CRUD,
códigos não reutilizados e exclusão respeitada. O backup anterior foi restaurado,
migrado por `002/003` e reproduziu as três estatísticas. Passaram 174 testes
Python, 20 de frontend, 4 fluxos Chrome isolados e 3 fluxos
Chrome/PostgreSQL. O `games` permaneceu com 3.069 resultados e três padrões. As
alterações de 9.1 a 9.8 ainda não foram commitadas. Aguardar autorização para o
commit de segurança; PythonAnywhere continua adiado.

- Criar o controle de migrações antes da automatização pelo Python.
- Confirmar se o desvio-padrão será populacional ou amostral.
- Definir o comportamento da mancha quando os círculos excederem a área do
  retângulo de um número.
- Escolher framework da API e driver PostgreSQL.
- Definir a origem confiável para atualizações futuras dos concursos.
- Decidir se `Game.code-workspace` será ignorado ou limpo antes do primeiro
  commit do projeto.
- Confirmar a estratégia para o backend compartilhado.
- Preparar o ambiente virtual e instalar as dependências de desenvolvimento
  antes de executar os testes.

## Modelo para encerrar futuras sessões

```text
Data:
Objetivo da sessão:
Arquivos alterados:
Testes executados e resultados:
Banco/ambiente afetado:
Decisões tomadas:
Pendências:
Próxima ação exata:
```
