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

Em 2026-10-27 foi concluído o Item 10.1, exclusivamente documental. O contrato
em `docs/CONTRATO_GRUPOS_E_NAVEGACAO.md` define as tabelas `padroes_grupo` e
`padroes_subgrupo`, relação obrigatória, proteção contra duplicidades e exclusão
de grupo ocupado, migração preservando os três padrões atuais e navegação em
uma única linha. O próximo item é 10.2: criar e testar a migração somente em
PostgreSQL temporário. Aguardar autorização expressa; não alterar o `games`, a
aplicação ou o PythonAnywhere antes dela.

O Item 10.2 foi concluído em 2026-10-27. A migração
`004_organizar_grupos_de_padroes.sql` cria `padroes_grupo`, renomeia `padroes`
para `padroes_subgrupo`, classifica os padrões nos grupos aprovados e protege
nomes normalizados e exclusão de grupo ocupado. O teste partiu de `001`–`003` com
estatística preenchida, aplicou `004`, preservou os valores e removeu o database
efêmero. O `games` não recebeu a migração. Antes de autorizar a aplicação local,
considerar que o código atual ainda consulta a tabela antiga `padroes`.

O Item 10.4 foi concluído em 2026-10-27 antes do 10.3 para evitar quebrar a
aplicação local. O novo `RepositorioGruposPadroes` implementa CRUD, consulta de
vínculos, códigos não reutilizáveis e proteção contra exclusão de grupo ocupado.
Passaram 5 testes unitários e o fluxo PostgreSQL temporário; nenhum database de
teste permaneceu. O próximo item seguro é 10.5, adaptação do repositório de
padrões. O `games` ainda não recebeu a migração 004.

O Item 10.5 foi concluído em 2026-10-27. `RepositorioPadroes` usa a nova tabela,
retorna dados do grupo, exige associação válida, filtra e transfere padrões
entre grupos sem alterar estatísticas. Passaram 27 testes direcionados e o fluxo
PostgreSQL temporário com cálculos. O `games` permanece na versão 003. A API
real ainda chama as assinaturas antigas de criação e edição; por isso, executar
10.6 e 10.7 antes de retornar à aplicação local do Item 10.3.

O Item 10.6 foi concluído em 2026-10-27. A nova API
`/api/grupos-padroes` lista, cria, edita e exclui grupos vazios, com código e
identificador protegidos e respostas específicas para duplicidade, grupo em uso
e ausência. Passaram 28 testes simulados; `games` não foi acessado. O próximo
item é 10.7, adaptação da API de padrões ao grupo obrigatório.

O Item 10.7 foi concluído em 2026-10-27. `/api/padroes` exige e retorna o grupo,
filtra por `grupo_cod` e permite transferência entre grupos. Passaram 36 testes
direcionados e um fluxo HTTP real em PostgreSQL temporário; o database efêmero
foi removido. Não aplicar ainda a migração 004 ao `games`: o frontend atual não
envia `grupo_cod` e deixaria de criar ou editar padrões. O próximo item seguro é
10.8, seguido de 10.9 e 10.10; depois retornar ao 10.3.

O Item 10.8 foi concluído em 2026-10-27. Foram criadas páginas separadas para
Painel, visão geral de Cadastros, Grupos de padrões e Padrões. A barra horizontal
de 2,8 rem contém Voltar, Painel, submenu flutuante e página atual. Passaram 20
testes de frontend, 4 fluxos Chrome e a entrega HTTP 200 pelo Flask. As páginas
de grupos e padrões ainda são estruturais. Próximo item: 10.9, grade CRUD de
grupos; `games` permanece na versão 003.

O Item 10.9 foi concluído em 2026-10-27. `/grupos-padroes.html` possui barra de
inclusão horizontal e grade CRUD com cabeçalho fixo e rolagem interna. Passaram
21 testes de frontend e o fluxo Chrome, inclusive a rejeição visual da exclusão
de grupo ocupado. A API foi simulada e PostgreSQL não foi acessado. Próximo item:
10.10, adaptar a grade de padrões aos grupos; `games` segue na versão 003.

O Item 10.10 foi concluído em 2026-10-27. `/padroes.html` possui grupo
obrigatório, filtro, transferência e grade compacta; estatísticas continuam
somente para leitura. Passaram 22 testes de frontend e 6 fluxos Chrome. Agora
frontend, API, repositórios e migração são compatíveis. Próximo passo: retornar
ao 10.3, gerar backup, aplicar 004 ao `games`, validar e reiniciar o servidor
local. O servidor antigo em memória deve ser encerrado antes da migração.

O Item 10.3 foi concluído em 2026-10-27 após as camadas compatíveis. O backup
pré-004 está em `MSen/dados/backups/games_pre_migracao_004_20261027_075306.dump`
e possui SHA-256 `1F3FE26CF8202F97A2CAF9909EF6669F1C6488563727DA08C3F57BF98B98A8ED`.
A inspeção encontrou `PD_004`–`PD_006` relacionados a colunas; a migração foi
corrigida e testada para criar `PG_002` e associá-los corretamente, abortando se
existir código desconhecido. O `games` está na versão 004 com 3.069 resultados,
60 frequências, 2 grupos e 6 padrões. O servidor atualizado está em
`http://127.0.0.1:5050/`, PID 23176; o antigo PID 228 foi encerrado. Próximo
item: 10.11, integração completa temporária e leitura final do `games`.

O Item 10.11 foi concluído em 2026-10-27. Passaram três fluxos integrados no
Chrome em 16 segundos: importação Excel, CRUD real de grupos/padrões em banco
temporário e gráficos em leitura do `games`. Nenhum database temporário ficou.
O `games` permanece com 3.069 resultados, 60 frequências, 2 grupos e 6 padrões,
três em cada grupo, com estatísticas preservadas. O servidor 5050 segue
saudável. Próximo item: 10.12, validação específica da compactação visual.

O Item 10.12 foi concluído em 2026-10-27. O Chrome mediu as páginas com 30 grupos
e 45 padrões em 1280 × 720 e 700 × 600. A barra permaneceu em até 46 px, o
submenu não deslocou o conteúdo, as grades contiveram suas rolagens e os
cabeçalhos ficaram fixos. Passaram 22 testes de frontend e 8 fluxos Chrome, sem
acesso ao banco. Próximo item: 10.13, regressão completa e fechamento documental
da Etapa 10.

O Item 10.13 e a Etapa 10 foram concluídos em 2026-10-27. Passaram 193 testes
Python, 22 de frontend, 8 fluxos Chrome e 3 fluxos Chrome/PostgreSQL. A migração
004 passou no caminho normal, rejeitou e reverteu integralmente um padrão legado
sem classificação e o esquema canônico foi validado do zero. O `games`
permaneceu com 3.069 resultados, 60 frequências, 2 grupos e 6 padrões; o servidor
local na porta 5050 permaneceu saudável. A Etapa 10 foi commitada e publicada
em `origin/developer` como `022331c`. PythonAnywhere continua adiado.

O Item 11.1 foi concluído em 2026-10-27 e corrigido no Item 11.6. O contrato
define a matriz 6 × 10, a coluna pela fórmula `((dezena - 1) % 10) + 1` e a
classificação exclusiva pela maior sequência em linhas subjacentes: `PD_004`
para exatamente duas, `PD_005` para exatamente três e `PD_006` para mais de três. Mesmo com
mais de uma coluna empatada, o resultado conta uma única ocorrência. Foram
registrados casos normais, limites e entradas inválidas; nenhum código ou dado
foi alterado. Próxima ação: aguardar autorização para o Item 11.2, destinado
aos detectores Python puros. PythonAnywhere permanece adiado.

O Item 11.2 foi concluído em 2026-10-27. O módulo puro
`msen/padroes/mesma_coluna.py` implementa os três detectores exclusivos pela
maior sequência vertical subjacente, com validação e docstrings em português. Passaram 18
testes direcionados: 6 novos e 12 de regressão dos padrões sequenciais. As
funções foram exportadas, mas ainda não foram registradas em `PD_004`–`PD_006`;
nenhum banco foi acessado. Próxima ação: aguardar autorização para o Item 11.3,
registro e estatísticas históricas em memória. PythonAnywhere permanece adiado.

O Item 11.3 foi concluído em 2026-10-27. `padroes/colunas.py` associa
`PD_004`–`PD_006` aos três detectores e calcula em memória ocorrências,
intervalos, média e desvio-padrão populacional. Passaram 29 testes direcionados,
incluindo históricos insuficientes, iterador e regressões; nenhum banco foi
acessado. Próxima ação: aguardar autorização para o Item 11.4, que fará a
integração transacional e a persistência, primeiro em PostgreSQL temporário.
PythonAnywhere permanece adiado.

O Item 11.4 foi concluído em 2026-10-27. O catálogo unificado expõe os seis
detectores; serviço e API agora reconhecem `PD_001`–`PD_006`. Passaram 204
testes Python. O database temporário `games_test_7_1_1114` confirmou duas
execuções idempotentes e as estatísticas esperadas de `PD_004`–`PD_006`, sendo
removido ao final; o `games` não foi acessado. Próxima ação: aguardar autorização
para o Item 11.5, que criará backup e recalculará o database local. PythonAnywhere
permanece adiado.

O Item 11.5 foi concluído em 2026-10-27. Antes do recálculo foi criado e
validado o backup ignorado pelo Git
`games_pre_recalculo_colunas_20261027_090452.dump`, com 117.894 bytes e SHA-256
`4FF31B6CFF1EEA32B916147CE469AABEC724E114F349AB2A1F78C200CB3C1C62`.
O primeiro recálculo foi invalidado após o esclarecimento da regra no Item 11.6;
o backup e os valores provisórios foram preservados apenas para rastreabilidade.

O Item 11.6 foi concluído em 2026-10-27. O usuário esclareceu que as dezenas
devem ocupar a mesma coluna em linhas imediatamente subjacentes, equivalendo a
uma sequência vertical com diferença dez. Contrato, detectores, testes, nomes e
descrições foram corrigidos. Um segundo backup foi criado com 117.935 bytes e
SHA-256 `688DC50925E583007A205566F29D2038992A8E34CD7E372D1FE423286D636D4F`.
O `games` preservou 3.069 resultados e passou a registrar `PD_004=1037`,
`PD_005=66` e `PD_006=4`. Passaram 205 testes Python, 22 de frontend, 8 fluxos
Chrome e a validação real da grade. O servidor foi reiniciado no PID 8556 e os
seis detectores aparecem como implementados. Próxima ação: aguardar autorização
para o Item 11.7, regressão integrada e fechamento da Etapa 11. PythonAnywhere
permanece adiado.

O Item 11.7 e a Etapa 11 foram concluídos localmente em 2026-10-27. A primeira
regressão integrada revelou que instalações novas deixavam `PD_004` livre. Foi
criada a migração `005`, que inicializa `PD_004`–`PD_006` em `PG_002`, reserva
esses códigos e deixa `PD_007` como primeiro cadastro futuro; o esquema canônico
também foi atualizado. Passaram 205 testes Python, 22 de frontend, 8 fluxos
Chrome e 3 fluxos Chrome/PostgreSQL. Migrações `001`–`005`, esquema criado do
zero, API, grade real e `games` foram auditados; nenhum database temporário
permaneceu. O `games` está na versão `005`, com 3.069 resultados e estatísticas
verticais `PD_004=1037`, `PD_005=66` e `PD_006=4`. A Etapa 11 foi commitada e
publicada em `origin/developer` como `e24ba66`. PythonAnywhere permanece adiado.

O Item 12.1 foi concluído em 2026-10-27. A leitura da API confirmou `PG_003 —
Dezenas na mesma linha` e `PD_007`–`PD_009` corretamente associados, ainda sem
detector ou estatística. O contrato define a linha por
`((dezena - 1) // 10) + 1` e classifica exclusivamente pela maior ocupação:
exatamente duas, exatamente três ou mais de três dezenas, sem exigir que sejam
sequenciais. Nenhum código ou dado foi alterado. Próxima ação: aguardar
autorização para o Item 12.2, detectores Python puros. PythonAnywhere permanece
adiado.

O Item 12.2 foi concluído em 2026-10-27. `padroes/mesma_linha.py` implementa os
três detectores exclusivos pela maior ocupação de linha, sem exigir
sequencialidade, com validação e docstrings em português. Passaram 38 testes
direcionados. As funções foram exportadas, mas ainda não foram registradas em
`PD_007`–`PD_009`; nenhum banco foi acessado. Próxima ação: aguardar autorização
para o Item 12.3, registro e estatísticas históricas em memória. PythonAnywhere
permanece adiado.

O Item 12.3 foi concluído em 2026-10-27. `padroes/linhas.py` associa
`PD_007`–`PD_009` e calcula em memória ocorrências, intervalos, média e
desvio-padrão populacional. O catálogo unificado passou a conter nove
detectores. Foram aprovados 55 testes direcionados, incluindo históricos
insuficientes, iterador e regressões; nenhum banco foi acessado. Próxima ação:
aguardar autorização para o Item 12.4, integração e persistência em PostgreSQL
temporário. PythonAnywhere permanece adiado.

O Item 12.4 foi concluído em 2026-10-27. O serviço transacional passou a
calcular os nove padrões. A migração `006` reserva `PG_003` e `PD_007`–`PD_009`,
e o esquema canônico agora cria três grupos e nove padrões. A persistência
idempotente produziu intervalos controlados de 15, 10 e 20 concursos. Passaram
216 testes Python; migrações `001`–`006` e esquema do zero foram validados, e
nenhum database temporário permaneceu. O `games` não foi acessado e continua na
versão `005`. Próxima ação: aguardar autorização para o Item 12.5, backup,
migração `006` e recálculo local. PythonAnywhere permanece adiado.

O Item 12.5 foi concluído em 2026-10-27. Antes da migração e do recálculo foi
criado o backup ignorado pelo Git
`games_pre_recalculo_colunas_20261027_105900.dump`, com 118.044 bytes e SHA-256
`55DDB37760DC36DC8311A61061F188A389F2590A183625741633762F7277CED5`.
O `games` passou à versão `006`, preservou 3.069 resultados e gravou
`PD_007=2053`, `PD_008=863` e `PD_009=93`, com médias e desvios. Textos e grupos
foram preservados. A API retornou os valores, mas o processo antigo ainda mostra
os detectores como pendentes. Próxima ação: aguardar autorização para o Item
12.6, reinício e validação real no Chrome. PythonAnywhere permanece adiado.

O Item 12.6 foi concluído em 2026-10-27. O servidor atualizado foi iniciado no
PID 12888 e permaneceu saudável em `127.0.0.1:5050`. A API retornou nove padrões
e nove detectores implementados. O validador real no Google Chrome confirmou as
nove linhas da grade e os nomes, estatísticas e estado de `PD_004`–`PD_009`, sem
alterar dados. Próxima ação: aguardar autorização para o Item 12.7, regressão
integrada e fechamento da Etapa 12. PythonAnywhere permanece adiado.

O Item 12.7 e a Etapa 12 foram concluídos em 2026-10-27. Passaram 216 testes
Python, 22 testes de frontend, 8 fluxos Chrome e 3 fluxos Chrome/PostgreSQL. Os
fluxos integrados foram adaptados de seis para nove padrões e agora respeitam
os próximos códigos livres `PG_004`, `PD_010` e `PD_011`. A auditoria confirmou
as migrações `001`–`006`, nenhum database temporário e a API saudável com nove
detectores. No `games`, `PD_007=2053`, `PD_008=863` e `PD_009=93`. O servidor
local permanece no PID 12888; PythonAnywhere não foi alterado. As mudanças da
Etapa 12 estão sem commit. Próxima ação exata: aguardar autorização para criar
o commit de segurança da Etapa 12; solicitar o push separadamente.

A Etapa 12 foi publicada em `origin/developer` no commit `a299404`. Depois do
commit, ficaram pendentes apenas ajustes visuais não versionados nas grades:
nomes de grupo e padrão multilinha e colunas de grupo/nome ampliadas; os 22
testes de frontend passaram.

Em 2026-10-27 foram planejadas as Etapas 13 e 14. A Etapa 13 construirá a
análise geométrica com dezenas sempre em ordem crescente: caminho aberto,
fechamento, interseções, soma das áreas das regiões e um centro de gravidade
ponderado único. Primeiro serão analisados os 3.069 resultados históricos, sem
qualquer exclusão. A Etapa 14 criará gerador e screener experimental. O ensaio
usará 5.000 combinações aleatórias distintas com semente reproduzível; o gerador
integral com `itertools.combinations` permanecerá protegido. O universo completo
tem 50.063.860 combinações e não será executado sem revisão de desempenho e
autorização expressa. Próxima ação: aguardar autorização para o Item 13.1.

O Item 13.1 foi concluído em 2026-10-27. O contrato geométrico determina ordem
crescente, coordenadas lógicas, extensão aberta, perímetro, decomposição do
percurso cruzado em regiões, soma positiva das áreas e um centro de gravidade
ponderado. Interseções deverão usar coordenadas exatas e figuras sem área terão
CG nulo. Quatro exemplos numéricos foram fixados antes do código. Nenhum banco
foi acessado. Próxima ação: aguardar autorização para o Item 13.2, funções puras
do caminho aberto e medidas básicas.

O Item 13.2 foi concluído em 2026-10-27. O pacote `msen.geometria` contém pontos
e segmentos exatos, constrói o percurso crescente sem modificar a entrada e
calcula extensão aberta e perímetro fechado com `Decimal`. Os exemplos simples,
cruzado e colinear foram reproduzidos. Passaram 11 testes específicos e 227
testes Python acumulados. Interseções, regiões e áreas ainda não foram
implementadas; nenhum banco foi acessado. Próxima ação: aguardar autorização
para o Item 13.3.

O Item 13.3 foi concluído em 2026-10-27. O módulo de regiões encontra
cruzamentos, contatos e sobreposições com `Fraction`, divide os segmentos,
remove arestas duplicadas e percorre a rede planar para obter somente as faces
limitadas. Foram validadas figuras com zero, uma, duas e três regiões e casos
degenerados. Passaram 12 testes específicos, uma varredura de estabilidade de
5.000 combinações e 239 testes Python acumulados. Nenhum banco foi acessado.
Próxima ação: aguardar autorização para o Item 13.4, área total e centro de
gravidade.

O Item 13.4 foi concluído em 2026-10-27. O módulo de medidas calcula exatamente
a área e o centroide de cada face, soma as áreas e produz um único centro de
gravidade ponderado. Os exemplos do contrato resultaram em área 36/CG
`(4,125; 2,5)`, área 4,5/CG `(4,5; 0,5)` e área zero/CG nulo. Passaram 10 testes
específicos, uma varredura coerente de 5.000 combinações e 249 testes Python
acumulados. Nenhum banco foi acessado. Próxima ação: aguardar autorização para
o Item 13.5, desenho da persistência e validação em PostgreSQL temporário.

O Item 13.5 foi concluído em 2026-10-27. A migração `007` cria a tabela
individual `analise_geometrica_resultado`; o repositório persiste extensão,
perímetro, regiões, área, CG e versão com doze casas. PostgreSQL temporário
confirmou migrações `001–007`, área 36/CG `(4,125; 2,5)`, área nula,
idempotência, restrições, cascata e esquema canônico. O temporário foi removido,
249 testes Python passaram e o `games` não foi alterado. Próxima ação: aguardar
autorização para o Item 13.6, serviço de cálculo histórico.

O Item 13.6 foi concluído em 2026-10-27. O novo serviço persiste uma análise ou
recalcula o histórico; inclusão, edição e importação o executam dentro de suas
transações. PostgreSQL temporário confirmou inclusão com área 36, importação com
área 4,5, edição com área zero, relação um para um e idempotência. Passaram 249
testes Python e o temporário foi removido. O `games` não foi conectado e ainda
não recebeu a migração `007`. Próxima ação: aguardar autorização para o Item
13.7, desenho geométrico no painel.

O Item 13.7 foi concluído em 2026-10-27. A API calcula e entrega vértices,
regiões, extensão, perímetro, área e CG sem depender da tabela ainda vazia. O
painel desenha percurso verde, fechamento tracejado, regiões transparentes,
pontos de 2 mm, média e CG, com resumo compacto e redimensionamento. Passaram
250 testes Python, 23 testes de frontend e 8 fluxos Chrome. Seletores Chrome
antigos das caixas multilinha também foram corrigidos. O servidor local não foi
reiniciado e o `games` segue sem a migração `007`. Próxima ação: aguardar
autorização para o Item 13.8, configuração visual persistente.

O Item 13.8 foi concluído em 2026-10-27. O botão compacto `Aparência` abre um
diálogo para sete cores, espessura, tamanho, transparência e visibilidade. As
preferências são validadas, salvas no `localStorage`, reaplicadas após recarregar
e restauráveis. Passaram 250 testes Python, 24 de frontend e 9 fluxos Chrome.
Nenhum banco foi acessado e o servidor não foi reiniciado. Próxima ação:
aguardar autorização para o Item 13.9, backup, migração `007`, recálculo dos
3.069 resultados e validação visual local.

O Item 13.9 foi concluído em 2026-10-27. O backup ignorado pelo Git
`games_pre_geometria_20261027_132845.dump` tem 118.150 bytes, catálogo válido e
SHA-256 `4A39BE414502479081F53048FF4F7AA88309BDAD192629140821212C90AFA8FC`.
A migração `007` foi aplicada e 3.069 análises foram gravadas sem alterar os
3.069 resultados. Áreas: mínima 1,5, máxima 29,5 e média 9,5777839879303392;
regiões de 1 a 4; nenhum CG nulo. O servidor atualizado está saudável no PID
37548. O Chrome real confirmou os desenhos, medidas e diálogo. A carga completa
da API levou cerca de 8,1 segundos e merece revisão no Item 13.10. Próxima ação:
aguardar autorização para o Item 13.10, distribuições, regressão e fechamento.

O Item 13.10 e a Etapa 13 foram concluídos em 2026-10-27. As distribuições
geométricas dos 3.069 resultados foram registradas. A API do painel passou a
carregar a lista sem geometria e buscar a análise do concurso selecionado sob
demanda, reduzindo o corpo inicial de 3.807.101 para 1.093.806 bytes (71,3%) e
medindo cerca de 0,5 s localmente. Passaram 254 testes Python, 24 JavaScript,
9 fluxos Chrome, 3 integrações Chrome/PostgreSQL e a validação visual real.
Não restaram bancos temporários. O servidor local está no PID 35448 e o
PythonAnywhere continua intocado. Próxima ação: aguardar autorização para o
commit de segurança da Etapa 13; depois, iniciar o Item 14.1 somente mediante
nova autorização.

O Item 14.1 foi concluído em 2026-10-27. O contrato do screener e o arquivo
versionado `MSen/config/screener.toml` definem modo amostral, semente, limite
obrigatório de 5.000 e a ordem padrões/estatísticas/geometria. O arquivo
`screener.local.toml` existe localmente e está ignorado pelo Git. Os exemplos
de tolerância de 3% e 20% foram registrados, mas todos os filtros permanecem
inativos até aprovação das regras. O leitor rejeita limite alterado, ordem
inválida e ativação prematura. Passaram 260 testes Python. Nenhum gerador foi
executado e nenhum banco foi alterado. Próxima ação: aguardar autorização para
o Item 14.2, gerador amostral repetível.

O Item 14.2 foi concluído em 2026-10-27. `msen.screener.gerar_amostra` usa um
`Random` isolado com a semente configurada e retorna exatamente 5.000 tuplas
únicas, cada uma com seis dezenas distintas, crescentes e entre 01 e 60. A
mesma semente reproduz a lista e sua ordem; modo integral e objeto não validado
são rejeitados. Passaram 7 testes específicos e 267 na regressão Python. Nada
foi gravado e nenhum filtro ou banco foi acionado. Próxima ação: aguardar
autorização para o Item 14.3, gerador integral protegido.

O Item 14.3 foi concluído em 2026-10-27. O iterador definitivo usa
`itertools.combinations(range(1, 61), 6)` e confirma o universo de 50.063.860.
Em modo amostral, `islice` encerra em 5.000. O modo integral exige tanto a
confirmação booleana da configuração quanto a frase explícita
`PROCESSAR_50063860_COMBINACOES`; o iterador continua preguiçoso. Passaram 7
testes específicos e 274 na regressão. O teste integral leu somente dois itens;
nenhum processamento integral ou banco foi acionado. Próxima ação: aguardar
autorização para o Item 14.4, estrutura do funil e contadores.

O Item 14.4 foi concluído em 2026-10-27. `executar_funil` recebe critérios
ordenados e, na primeira reprovação, contabiliza o critério e salta para a
próxima combinação. `RelatorioFunil` guarda total recebido/aprovado, avaliações,
exclusões, saldo após cada filtro e aprovadas. Códigos duplicados ou divergentes
são rejeitados. Sem critérios, as 5.000 amostras passam integralmente. Passaram
5 testes específicos e 279 na regressão. Apenas critérios artificiais de teste
foram usados; banco e filtros reais permaneceram intocados. Próxima ação:
aguardar autorização para o Item 14.5, adaptadores dos critérios.

O Item 14.5 foi concluído em 2026-10-27. Há adaptadores separados para padrões
históricos, medidas estatísticas e medidas geométricas. Eles repassam as
tolerâncias e devolvem ao funil aprovação/reprovação, código e valores
justificadores. Quando desabilitados, aprovam de forma neutra sem chamar a
função; quando habilitados, exigem avaliador com retorno validado. Passaram 5
testes específicos e 284 na regressão, usando somente avaliadores artificiais.
Nenhuma regra real ou banco foi acionado. Próxima ação: aguardar autorização
para o Item 14.6, quadro de avaliação.

O Item 14.6 foi concluído em 2026-10-27. `executar_ensaio` mede o funil e gera
um quadro com versão, modo, semente, limite, configuração dos critérios, tempo,
totais e linhas contendo ordem/avaliações/exclusões/saldo. A serialização é
compatível com JSON. Uma execução real em memória, sem filtros, recebeu e
aprovou as 5.000 combinações; todos os critérios ficaram inativos. Passaram 5
testes específicos e 289 na regressão. Nada foi persistido. Próxima ação:
aguardar autorização para o Item 14.7, ensaio integrado de 5.000 combinações.

O Item 14.7 foi concluído em 2026-10-27 no escopo autorizado. O fluxo integrado
carrega a configuração, gera a amostra reproduzível, executa o funil vazio e
serializa o quadro. A execução manual recebeu/aprovou 5.000, sem linhas de
exclusão, com cerca de 0,0003 s no funil. Categorias ativas são bloqueadas:
como nenhuma regra real de exclusão foi aprovada, o ensaio filtrado e a
comparação de ordens foram corretamente considerados não aplicáveis. Passaram
5 testes específicos e 294 na regressão. Nada foi persistido. Próxima ação:
aguardar autorização para o Item 14.8, revisão antes do processamento integral.

O Item 14.8 e a Etapa 14 foram concluídos em 2026-10-27. Em 5.000 combinações,
a geometria levou 2,8978 s; a projeção linear do universo foi de cerca de 8,1 h
em um processo, sem filtros adicionais ou I/O. Armazenar tuplas Python projetou
4,81 GB; CSV compacto, 901 MB; seis bytes binários, 300 MB, todos sem resultados
ou metadados. A decisão é processar futuramente de modo sequencial, particionado
e em fluxo, com retomada; paralelismo somente após medir filtros reais. O limite
de 5.000 permanece e nenhuma execução integral ocorreu. Passaram 3 testes
específicos e 297 na regressão. Próxima ação: aguardar autorização para o
commit de segurança da Etapa 14; depois, definir e aprovar regras reais antes de
qualquer ativação. PythonAnywhere continua adiado.

Em 2026-10-27 foi planejada a Etapa 15 com 16 subetapas curtas. Ela separa
detecção, política de exclusão, modo sombra e ativação. O primeiro critério será
escolhido somente depois do inventário; detector, operador e tolerância exigem
aprovação própria. Padrões históricos precedem critérios estatísticos e
geométricos; comparar ordens exige ao menos dois aprovados. A etapa termina com
quadro visual e regressão, mantendo o universo integral travado. Nenhum código
ou filtro foi alterado neste planejamento. Próxima ação: aguardar autorização
para o Item 15.1, inventário somente leitura.

O Item 15.1 foi concluído em 2026-10-27 somente com leitura. O PostgreSQL tem
3.069 resultados, 3 grupos e 9 padrões; o catálogo tem os 9 detectores
correspondentes, sem órfãos. O inventário com funções, ocorrências, percentuais,
intervalos e desvios está em `MSen/tests/TESTE_ITEM_15_1.md`. Foram observadas,
mas não corrigidas, a docstring do catálogo que ainda cita somente PD_001 a
PD_006 e a duplicidade de espaço no nome de PD_008. Nenhuma estatística foi
recalculada e nenhum critério foi ativado. Próxima ação: aguardar autorização
para o Item 15.2, contrato de detecção e exclusão.

O Item 15.2 foi concluído em 2026-10-27 apenas como contrato. Detector booleano,
política e modo foram separados. O percentual usa todos os resultados válidos
avaliados pela mesma versão, compara a razão exata e exibe seis casas com
`ROUND_HALF_UP`. A semântica proposta é inclusiva (`<=`), mas nenhum valor foi
aprovado. Dados ausentes, inconsistentes ou não reconciliados nunca excluem.
Modos seguem inativo -> sombra -> ativo, sempre com autorização. Intervalos e
desvios exigem política própria. Nenhum código, configuração ou banco mudou.
Próxima ação: aguardar autorização para o Item 15.3, escolha do piloto.

O Item 15.3 foi iniciado em 2026-10-27. A análise recomendou PD_003 (mais de
três dezenas sequenciais): 5 ocorrências, 0,162920%, regra simples/exclusiva e
testes existentes. PD_006, com 4 ocorrências, é a alternativa, mas exige maior
cuidado com coluna e linhas subjacentes. PD_002 e PD_009 foram evitados como
primeiro piloto por estarem quase exatamente na fronteira exemplificativa de
3%, ainda não aprovada. Nenhum piloto foi selecionado, pois falta a aprovação
explícita do usuário.

Ainda em 2026-10-27, o usuário aprovou PD_003 como piloto de teste e o Item 15.3
foi concluído. A escolha autoriza somente os casos e a validação do detector;
não autoriza tolerância, sombra, exclusão ou ativação. Próxima ação: aguardar
autorização para o Item 15.4, casos de aceitação do PD_003.

O Item 15.4 foi iniciado em 2026-10-27. Foram preparados 8 casos positivos, 6
negativos e 6 entradas inválidas para PD_003. Os pontos de decisão são:
sequência numérica atravessa 10/11; 60/01 não é circular; blocos separados não
são somados; bloco de quatro ou mais pertence exclusivamente a PD_003. Nenhum
código foi alterado. Próxima ação: obter aprovação ou correção dos casos em
`docs/CASOS_ACEITACAO_PD003.md` antes de concluir o Item 15.4.

Ainda em 2026-10-27, o usuário aprovou os casos e o Item 15.4 foi concluído. A
classificação usa o maior bloco consecutivo; atravessa 10/11, mas não 60/01;
blocos separados não são somados; quatro ou mais pertence exclusivamente a
PD_003. Assim, `58,59,60,01,02,03` não é PD_003 e `01,02,03,04,20,40` é
somente PD_003. Isso não aprova exclusão. Próxima ação: aguardar autorização
para o Item 15.5, validação/implementação isolada do detector.

O Item 15.5 foi concluído em 2026-10-27. O detector existente de PD_003 passou
nos 20 casos aprovados (8 positivos, 6 negativos e 6 erros) e os positivos não
foram classificados por PD_001/PD_002. Não houve mudança no detector. O script
`validar_detector_pd003.py` gera saída com esperado, obtido, motivo e
conformidade; o Item 15.15 agora exige uma saída visual equivalente para
validação humana antes de filtros reais. Passaram 2 testes específicos e 299 na
regressão. Próxima ação: aguardar autorização para o Item 15.6, reconciliação
histórica de PD_003.

O Item 15.6 foi concluído em 2026-10-27 com leitura dos 3.069 resultados. PD_003
ocorreu nos concursos 186, 509, 2052, 2789 e 2908; todos possuem bloco máximo de
quatro. Intervalos: 323, 1543, 737 e 119. Quantidade 5, média 680,500000 e
desvio populacional 545,478460 coincidiram exatamente com o banco. A menção
anterior de mediana foi corrigida: mediana dos resultados pertence aos critérios
estatísticos, não à tabela de padrões. PD_003 está reconciliado e nada foi
escrito. Próxima ação: aguardar
autorização para o Item 15.7, política piloto em modo sombra.

O Item 15.7 foi concluído em 2026-10-27. `PoliticaPadraoSombra` usa comparação
exata e devolve marca hipotética, mas sempre aprova a combinação. Para PD_003,
5/3069 = 0,162920% seria marcado sob a hipótese ainda não aprovada de 3%; com
0,1% não seria. Evidência não reconciliada produz `nao_avaliavel` sem exclusão.
A decisão registra todos os valores e motivo. O funil de teste recebeu/aprovou
2 e excluiu 0. A configuração real continua desabilitada. Passaram 6 testes
específicos e 305 na regressão. Próxima ação: aguardar autorização para o Item
15.8, simulação sombra de 5.000 combinações.

O Item 15.8 foi concluído em 2026-10-27. Sob a hipótese não aprovada de 3%, a
semente 20261027 marcou 11/5000 (0,22%, saldo hipotético 4989) e a semente 42
marcou 5/5000 (0,10%, saldo 4995). O histórico é 0,162920%; a variação demonstra
sensibilidade da amostra para evento raro, não a proporção do universo. As
10.000 foram aprovadas de fato e zero excluídas. A configuração continua
inativa. Passaram 4 testes da simulação e 309 na regressão. Próxima ação:
aguardar autorização para o Item 15.9, decisão humana sobre detector, operador,
tolerância e dado ausente de PD_003.

O Item 15.9 foi iniciado em 2026-10-27. A proposta recomenda: detector já
validado; operador inclusivo `percentual_historico <= tolerancia`; tolerância
inicial de 3%; e falha conservadora que aprova quando falta evidência. Foi
esclarecido que 3% qualifica o padrão, não determina 3% de exclusões; nas
amostras PD_003 marcou 0,22% e 0,10%. Nenhuma ativação foi feita. Próxima ação:
obter aprovação ou correção explícita dos quatro pontos.

Ainda em 2026-10-27, o usuário autorizou a regra e o Item 15.9 foi concluído.
Foram aprovados: detector PD_003; operador inclusivo `<=`; tolerância de 3%; e
falha conservadora `nao_avaliavel` que não exclui. A autorização vale somente
para a futura execução protegida de 5.000. Nenhuma ativação ocorreu ainda; o
universo integral e outros padrões continuam bloqueados. Próxima ação: aguardar
autorização para o Item 15.10, ativação controlada de PD_003.

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
## Atualização — 2026-10-27 — subetapa 15.10

- PD_003 foi ativado exclusivamente na amostra protegida de 5.000 combinações.
- Regra: detector de mais de três consecutivas, operador `<=`, tolerância 3% e
  evidência reconciliada de 5 ocorrências em 3.069 resultados.
- Semente 20261027: 5.000 recebidas, 11 excluídas e 4.989 aprovadas.
- O modo integral continua bloqueado e sua confirmação permanece falsa.
- Passaram 316 testes Python; nenhuma escrita foi feita no banco.
- Próxima subetapa proposta: 15.11, escolhendo e validando um novo padrão antes
  de qualquer outra ativação.
## Atualização — 2026-10-27 — subetapa 15.11 (PD_002)

- Próximo padrão preparado: PD_002, maior bloco com exatamente três dezenas.
- Histórico reconciliado: 92/3.069 (`2,997719%`), intervalo médio `33,527473`
  e desvio-padrão `33,637806`.
- Sombra: 162/5.000 marcadas na semente 20261027 e 142/5.000 na semente 42;
  nenhuma exclusão real.
- Casos e classificação exclusiva foram testados; PD_002 ainda não está ativo.
- Próxima decisão: usuário aprovar ou rejeitar detector, operador `<=`,
  tolerância 3% e falha conservadora para a ativação amostral de PD_002.

## Atualização — 2026-10-27 — ativação de PD_002

- O usuário aprovou os quatro critérios de PD_002.
- Funil amostral: PD_003 excluiu 11; PD_002 excluiu 162; 4.827 foram aprovadas.
- Contabilidade: `5.000 = 11 + 162 + 4.827`.
- PD_003 avaliou 5.000 e PD_002 avaliou o saldo de 4.989, respeitando a saída na
  primeira exclusão.
- Passaram 323 testes; modo integral continua bloqueado; banco não foi escrito.
- Próximo trabalho: selecionar o próximo padrão do Item 15.11, sem ativá-lo
  antes de nova autorização específica.

## Atualização — 2026-10-27 — preparação de PD_006

- Regra validada: maior sequência de quatro, cinco ou seis dezenas na mesma
  coluna e em linhas imediatamente subsequentes.
- Histórico: 4/3.069 (`0,130336%`), concursos 363, 844, 2066 e 2453; estatísticas
  coincidiram exatamente com o banco.
- Sombra: 5/5.000 marcações na semente 20261027 e 0/5.000 na semente 42.
- PD_006 ainda não está ativo; PD_003 e PD_002 continuam como únicas regras.
- Próxima decisão: aprovar ou rejeitar detector, operador `<=`, tolerância 3% e
  falha conservadora para a ativação amostral de PD_006.

## Atualização — 2026-10-27 — ativação de PD_006

- O usuário aprovou os quatro critérios de PD_006.
- Funil: PD_003 excluiu 11, PD_002 excluiu 162 e PD_006 excluiu 5; saldo 4.822.
- Contabilidade: `5.000 = 11 + 162 + 5 + 4.822`.
- Avaliações: PD_003 5.000, PD_002 4.989 e PD_006 4.827, respeitando a saída na
  primeira exclusão.
- Passaram 327 testes; modo integral continua bloqueado; banco não foi escrito.
- Próximo trabalho: selecionar o próximo padrão histórico sem ativá-lo antes
  de nova autorização específica.

## Atualização — 2026-10-27 — preparação de PD_005

- Regra validada: maior sequência de exatamente três dezenas na mesma coluna e
  em linhas imediatamente subsequentes.
- Histórico: 66/3.069 (`2,150538%`), intervalo médio `45,969231` e desvio-padrão
  `42,006948`, todos reconciliados.
- Sombra: 113/5.000 marcações na semente 20261027 e 97/5.000 na semente 42.
- PD_005 ainda não está ativo; as regras ativas continuam PD_003, PD_002 e
  PD_006.
- Próxima decisão: aprovar ou rejeitar detector, operador `<=`, tolerância 3% e
  falha conservadora para a ativação amostral de PD_005.

## Atualização — 2026-10-27 — ativação de PD_005

- O usuário aprovou os quatro critérios de PD_005.
- PD_005 avaliou o saldo de 4.822 e excluiu 110; três de suas 113 marcações
  sombra já haviam sido excluídas por filtros anteriores.
- Funil completo: 11 por PD_003, 162 por PD_002, 5 por PD_006, 110 por PD_005 e
  saldo final 4.712.
- Contabilidade: `5.000 = 11 + 162 + 5 + 110 + 4.712`.
- Passaram 331 testes; modo integral continua bloqueado; banco não foi escrito.
- Próximo trabalho: selecionar outro padrão histórico, sem ativação antes de
  nova autorização específica.

## Atualização — 2026-10-27 — avaliação de PD_009

- Histórico reconciliado: 93/3.069 (`3,030303%`), intervalo médio `33,141304`
  e desvio-padrão `35,099728`.
- O detector encontrou 177 combinações na semente 20261027 e 154 na semente 42.
- A política marcou zero nas duas porque `3,030303% > 3%`.
- PD_009 não foi ativado e não deve excluir sob a tolerância atual.
- Próximo trabalho proposto: revisar os padrões restantes, todos acima de 3%,
  sem ativá-los.

## Atualização — 2026-10-27 — fechamento dos padrões históricos

- PD_001, PD_004, PD_007 e PD_008 foram recalculados e reconciliados.
- Os detectores encontraram muitas combinações nas duas amostras, mas a política
  marcou zero porque todos possuem percentual histórico acima de 3%.
- Etapa 15.11 fechada para os nove padrões cadastrados.
- Ativos somente na amostra: PD_003, PD_002, PD_006 e PD_005.
- Não ativos: PD_009, PD_001, PD_004, PD_007 e PD_008.
- Próximo item planejado: 15.12, critérios estatísticos, começando pela escolha
  de um piloto e sem exclusão antes de validação e autorização.

## Atualização — 2026-10-27 — início do Item 15.12

- Média aritmética escolhida como primeiro piloto estatístico.
- Histórico: média das médias `30,515749`, mediana `30,666667` e desvio
  populacional `6,659667`.
- A margem exemplificativa de ±20% atingiria 1.151/3.069 resultados e não foi
  recomendada.
- Candidato para discussão: faixa P01/P99 de `15,000000` a `45,886666`, com
  comparação `< inferior` ou `> superior`; 59 históricos (`1,922450%`) e
  108/5.000 amostrais ficariam fora.
- Nenhuma política estatística foi implementada ou ativada.
- Próxima decisão depende do usuário aprovar ou ajustar essa faixa.

## Atualização — 2026-10-27 — média em modo sombra

- Usuário aprovou a faixa P01/P99 para teste experimental.
- Regra: média `< 15,000000` ou `> 45,886666`; limites exatos são aceitos.
- Sombra: 108/5.000 marcações na semente 20261027 e 96/5.000 na semente 42.
- Todas as combinações foram realmente aprovadas; política não está no funil
  ativo.
- Próxima decisão: manter em sombra, ajustar a faixa ou autorizar ativação
  amostral específica.

## Atualização — 2026-10-27 — ativação experimental da média

- Usuário autorizou a opção 3, somente na amostra protegida.
- A média foi adicionada como quinto filtro e recebeu o saldo de 4.712.
- Excluiu 89 combinações; 19 das 108 marcações sombra já haviam sido excluídas
  pelos padrões históricos.
- Saldo final 4.623; contabilidade:
  `5.000 = 11 + 162 + 5 + 110 + 89 + 4.623`.
- Passaram 346 testes; modo integral continua bloqueado; banco não foi escrito.
- Próxima decisão: escolher mediana ou desvio-padrão como próximo piloto
  estatístico.

## Atualização — 2026-10-27 — inventário do desvio-padrão

- Histórico: média dos desvios `15,556645`; margem ±20% seria agressiva e
  atingiria 1.197/3.069 resultados.
- Faixa candidata P01/P99: `7,145546` a `22,774694`, comparação estrita.
- Fora historicamente: 62 (`2,020202%`); na amostra: 132/5.000.
- Nenhuma política foi criada ou ativada.
- Próxima decisão: usuário aprovar, ajustar ou rejeitar a faixa experimental.

## Atualização — 2026-10-27 — mediana em sombra

- Faixa aprovada para teste: `10,5` a `50,5`, comparação estrita.
- Sombra: 92/5.000 marcações na semente 20261027 e 91/5.000 na semente 42.
- Todas foram realmente aprovadas; política não integra o funil ativo.
- Próxima decisão: autorizar ou não a ativação apenas para teste da engrenagem.

## Atualização — 2026-10-27 — ativação experimental da mediana

- Mediana adicionada como sétimo filtro somente na amostra protegida.
- Recebeu 4.528, excluiu 44 e deixou saldo 4.484.
- Das 92 marcações sombra, 48 já tinham sido excluídas anteriormente.
- Contabilidade:
  `5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 44 + 4.484`.
- Passaram 362 testes; limites experimentais; integral bloqueado; banco não
  escrito.
- Os três pilotos estatísticos previstos — média, desvio e mediana — já foram
  testados. Próximo item: 15.13, critérios geométricos.

## Atualização — 2026-10-27 — inventário da extensão aberta

- Primeiro piloto geométrico: soma dos cinco segmentos do caminho crescente.
- Histórico: média `18,398295`; ±20% atingiria 1.523/3.069 e foi descartado.
- Faixa P01/P99 aprovada: `8,650282` a `32,300058`, comparação estrita.
- Com os limites arredondados realmente usados: 64 históricos (`2,085370%`) e
  106/5.000 na amostra principal; isso corrige a estimativa bruta 61/102.
- Sombra: 106/5.000 na semente 20261027 e 115/5.000 na semente 42.
- Política ainda não integra o funil ativo.
- Próxima decisão: autorizar ou não ativação apenas para teste da engrenagem.

## Atualização — 2026-10-27 — desvio-padrão em sombra

- Faixa aprovada para teste: `7,145546` a `22,774694`, comparação estrita.
- Sombra: 132/5.000 marcações na semente 20261027 e 122/5.000 na semente 42.
- Todas foram realmente aprovadas; política não integra o funil ativo.
- Próxima decisão: manter em sombra, ajustar ou autorizar ativação amostral.

## Atualização — 2026-10-27 — ativação experimental do desvio

- Usuário autorizou somente para testar a engrenagem; limites não são
  definitivos.
- Sexto filtro recebeu 4.623, excluiu 95 e deixou saldo 4.528.
- Das 132 marcações sombra, 37 já tinham sido excluídas anteriormente.
- Contabilidade: `5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 4.528`.
- Passaram 353 testes; integral bloqueado; banco não escrito.
- Próximo piloto proposto: mediana das seis dezenas.

## Atualização — 2026-10-27 — inventário da mediana

- Histórico: média das medianas `30,677908`; ±20% atingiria 1.678/3.069 e foi
  considerado agressivo.
- Faixa candidata P01/P99: `10,5` a `50,5`, comparação estrita.
- Fora historicamente: 57 (`1,857283%`); na amostra: 92/5.000.
- Passaram 355 testes; nenhuma política foi criada ou ativada.
- Próxima decisão: usuário aprovar, ajustar ou rejeitar a faixa experimental.

## Atualização — 2026-10-27 — ativação experimental da extensão

- Extensão aberta adicionada como oitavo filtro somente na amostra protegida.
- Recebeu 4.484, excluiu 75 e deixou saldo 4.409.
- Das 106 marcações sombra, 31 já tinham sido excluídas anteriormente.
- Contabilidade:
  `5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 44 + 75 + 4.409`.
- Passaram 369 testes; limites experimentais; integral bloqueado; banco não
  escrito.
- Próximo item proposto: 15.14, comparar a eficiência de ordens diferentes.

## Atualização — 2026-10-27 — comparação das ordens

- Foram comparadas três ordens sobre a mesma amostra e as mesmas regras.
- Todas preservaram exatamente as mesmas 4.409 combinações aprovadas.
- Avaliações: atual 37.985; históricos frequentes 37.569; geometria e
  estatísticas primeiro 37.315.
- Medianas locais de três tempos: 0,670447 s; 0,629925 s; 0,638000 s.
- A ordem padrão não foi alterada porque quantidade de avaliações e custo por
  função são diferentes.
- Passaram 372 testes; integral bloqueado; banco não escrito.
- Próximo item: 15.15, quadro visual e saída de validação.

## Atualização — 2026-10-27 — quadro visual do screener

- Criada a API `GET /api/screener/quadro`, sem dependência do banco.
- Criada `/screener.html`, com CSS e JavaScript separados e link na barra.
- Quadro mostra os oito estágios, avaliações, exclusões, percentual e saldo.
- Saída traz 30 combinações; o usuário informa o esperado e a tela mostra
  conformidade ou divergência sem persistência.
- Na seleção atual: 27 aprovadas e 3 excluídas.
- Passaram 379 testes Python e 24 testes JavaScript; integral bloqueado; banco
  não escrito.
- Próximo item: 15.16, regressão, Chrome local e fechamento.

## Atualização — 2026-10-27 — fechamento da Etapa 15

- Passaram 379 testes Python, 24 JavaScript e 11 fluxos no Google Chrome.
- O Chrome usou a API Flask real e confirmou 5.000 recebidas, 591 excluídas,
  4.409 aprovadas, oito estágios e 30 casos para validação humana.
- Conformidade manual, layout compacto e rolagens foram verificados.
- Nenhuma porta de teste permaneceu aberta; banco não acessado; integral
  bloqueado; PythonAnywhere adiado.
- Etapa 15 concluída. Próxima ação: commit de segurança somente se autorizado.

## Atualização — 2026-10-28 — contrato de classificação por grupos

- Subetapa 16.1 executada somente em documentação e validação das funções reais.
- Os grupos atuais são exclusivos pelo maior bloco ou maior ocupação.
- Quando nenhum padrão do grupo corresponder, será usado o estado
  `SEM_CORRESPONDENCIA`; ele não será um novo padrão PD.
- As propostas PD_010, PD_011 e PD_012 foram retiradas após esclarecimento.
- Denominador principal proposto: todos os resultados válidos. A diferença até
  100% será `SEM_CORRESPONDENCIA`.
- As frequências serão obtidas executando as funções no histórico e revelarão
  quais padrões são raros. Nenhuma raridade será presumida previamente.
- No screener, `SEM_CORRESPONDENCIA` passa; somente padrões configurados para
  exclusão poderão eliminar a combinação.
- Contrato em `docs/CONTRATO_CLASSIFICACAO_GRUPOS.md`.
- A raridade será calculada aplicando os padrões ao histórico. Um limite
  configurável selecionará os padrões estritamente abaixo dele; 10% é apenas
  hipótese inicial.
- A lista excludente será calculada uma vez por execução e registrada com o
  intervalo, denominador, frequências, operador e versões.
- Contrato conceitual aprovado. Nenhuma tabela ou função foi alterada; a
  subetapa 16.2 depende de autorização para preparar o DDL.

## Atualização — 2026-10-28 — DDL da classificação por grupos

- Subetapa 16.2 concluída sem aplicar alterações ao database `games`.
- Criada a migração `008_criar_classificacao_resultado_padrao.sql`.
- A tabela garante uma linha por resultado/grupo e aceita um padrão do mesmo
  grupo ou o estado `SEM_CORRESPONDENCIA`, nunca ambos.
- Foram incluídos versão, data de cálculo e índice para o perfil histórico.
- O esquema PostgreSQL consolidado foi atualizado.
- Passaram 13 testes direcionados e 384 testes na regressão Python.
- Próxima ação: aguardar autorização para a subetapa 16.3, que executará a
  migração e testará suas restrições em um database PostgreSQL temporário.

## Atualização — 2026-10-28 — teste PostgreSQL da migração 008

- Subetapa 16.3 concluída exclusivamente no database efêmero
  `games_test_7_1_163`.
- A estrutura anterior recebeu `001`–`007`; na primeira execução seguinte,
  somente a `008` foi aplicada.
- A segunda execução reconheceu `001`–`008` e não reaplicou nenhuma versão.
- Foram aceitos os estados válidos com padrão e sem correspondência.
- Foram rejeitados duplicidade resultado/grupo, estados incompatíveis, padrão
  de outro grupo e versão não positiva.
- A exclusão em cascata do resultado foi confirmada.
- Uma migração `009` defeituosa, criada como fixture de teste, sofreu rollback:
  nem sua tabela nem sua versão permaneceram.
- O database temporário foi removido; a auditoria de remanescentes retornou
  lista vazia. O database `games` não foi alterado.
- Próxima ação: aguardar autorização para a subetapa 16.4, modelo imutável e
  repositório Python da classificação.

## Atualização — 2026-10-28 — modelo e repositório de classificações

- Subetapa 16.4 concluída.
- Criado o modelo imutável `ClassificacaoPadrao`, com estados tipados e
  validação de coerência antes do SQL.
- Criado `RepositorioClassificacoesPadrao`, com salvamento idempotente por
  resultado/grupo e consultas por resultado e por grupo.
- O recálculo preserva `id_classificacao` e atualiza padrão, estado, versão e
  data do cálculo.
- A integração passou no database efêmero `games_test_7_1_164`, que foi
  removido; a auditoria de remanescentes retornou `[]`.
- Passaram oito testes direcionados e 392 testes na regressão Python.
- O database principal `games` não foi alterado.
- Próxima ação: aguardar autorização para a subetapa 16.5, classificador do
  grupo piloto de dezenas sequenciais.

## Atualização — 2026-10-28 — classificador piloto do grupo PG_001

- Subetapa 16.5 concluída sem acesso ao banco.
- O classificador retorna exclusivamente `PD_001`, `PD_002`, `PD_003` ou
  `SEM_CORRESPONDENCIA`, conforme o maior bloco consecutivo.
- A análise central agora também fornece dezenas ordenadas, tamanho máximo e
  blocos máximos, usando a mesma regra dos detectores históricos.
- `58,59,60,01,02,03` foi confirmado como dois blocos de três (`PD_002`), sem
  continuidade circular entre 60 e 01.
- `01,02,03,04,20,40` foi confirmado como `PD_003`.
- Passaram 18 testes direcionados e 398 testes na regressão Python.
- Nenhuma classificação foi persistida.
- Próxima ação: aguardar autorização para a subetapa 16.6, recálculo histórico
  e persistência transacional/idempotente do grupo piloto.

## Atualização — 2026-10-28 — recálculo histórico do grupo piloto

- Subetapa 16.6 concluída sem alterar o database principal `games`.
- O novo serviço resolve `PG_001` e seus três padrões, percorre resultados em
  ordem, classifica e persiste tudo em uma única transação.
- Uma falha controlada no terceiro registro comprovou rollback sem gravações
  parciais.
- O subconjunto controlado produziu uma ocorrência em cada uma das quatro
  classes e preservou identidades em três recálculos, inclusive ao mudar a
  versão para 2.
- Um clone do histórico completo classificou 3.069 resultados: `PD_001=1.192`,
  `PD_002=92`, `PD_003=5` e `SEM_CORRESPONDENCIA=1.780`.
- O segundo recálculo do histórico preservou as 3.069 identidades.
- Os databases temporários foram removidos; a auditoria retornou `[]`.
- Passaram 400 testes na regressão Python.
- Próxima ação: aguardar autorização para a subetapa 16.7, perfil de contagens,
  percentuais, fechamento em 100% e indicação experimental de raridade.

## Atualização — 2026-10-28 — perfil histórico e raridade experimental

- Subetapa 16.7 concluída sem alterar o database principal `games`.
- O denominador oficial é o total de resultados; o perfil também mostra o
  percentual alternativo entre os resultados que encontraram algum padrão.
- `SEM_CORRESPONDENCIA` participa do fechamento oficial, mas nunca pode ser
  selecionado como padrão raro.
- O operador foi comprovado como estritamente menor (`<`): valor exatamente no
  limite é preservado.
- No clone dos 3.069 resultados, `PD_001=38,840013%`, `PD_002=2,997719%`,
  `PD_003=0,162920%` e `SEM_CORRESPONDENCIA=57,999348%`.
- Com limite experimental de 10%, somente `PD_002` e `PD_003` foram indicados;
  nenhuma exclusão foi ativada no screener.
- O perfil sincroniza as estatísticas completas do catálogo e rejeita histórico
  com classificações incompletas ou divergentes.
- Passaram cinco testes unitários, dois ensaios PostgreSQL temporários e 403
  testes de regressão. Os databases temporários foram removidos.
- Próxima ação: aguardar autorização para a subetapa 16.8, API do perfil por
  grupo com corte histórico preparado para uso futuro.

## Atualização — 2026-10-28 — API do perfil histórico

- Subetapa 16.8 concluída sem alterar o database principal `games`.
- Criado `GET /api/grupos-padroes/PG_001/perfil`.
- A API aceita limite de raridade e um corte inclusivo por concurso ou data;
  os dois cortes juntos são rejeitados.
- A resposta inclui intervalo efetivo, totais, versões, quatro classes,
  percentuais, intervalo médio, desvio-padrão e padrões indicados.
- `ativa_no_screener` permanece sempre falso nesta etapa.
- Na integração, o perfil completo retornou 3.069 resultados; os cortes no
  concurso 100 e na data 1998-02-01 retornaram 100 cada.
- Fotografias antes/depois comprovaram que as requisições GET não alteraram o
  catálogo global.
- Passaram 12 testes direcionados, integração Flask/PostgreSQL e 410 testes de
  regressão. O database temporário foi removido.
- Próxima ação: aguardar autorização para a subetapa 16.9, tela compacta do
  perfil na página de padrões.

## Atualização — 2026-10-28 — painel compacto do perfil

- Subetapa 16.9 concluída sem alteração de banco.
- `padroes.html` ganhou o acionador `Perfil PG_001` na mesma linha do filtro.
- O painel é absoluto e flutuante: não acrescenta linha à navegação e não
  reduz permanentemente a altura da grade.
- São exibidos limite, corte, amostra, classificados, sem correspondência,
  padrões indicados e as quatro classes com percentuais e estatísticas.
- A interface declara explicitamente que o screener continua inativo.
- Passaram 24 testes JavaScript, 12 fluxos no Google Chrome e 410 testes Python.
- A API real já passou em clone PostgreSQL na 16.8; o perfil no servidor ligado
  ao `games` continuará indisponível até a migração `008` e o recálculo serem
  aplicados com autorização expressa.
- Próxima ação: aguardar autorização para a subetapa 16.10, regressão e
  fechamento da Etapa 16, incluindo decisão segura sobre aplicação local.

## Atualização — 2026-10-28 — fechamento operacional da Etapa 16

- Backup criado antes da aplicação local:
  `games_pre_classificacao_20261028_100708.dump`, 226.601 bytes, SHA-256
  `9C662ADC4EC8E94336C13E2D576AC91F6AD706C10D56DB8E3D4F78B1D389880E`.
- O `games` recebeu somente a migração `008` e 3.069 classificações de
  `PG_001`; resultados, frequências e análises geométricas foram preservados.
- Contagens finais: `PD_001=1.192`, `PD_002=92`, `PD_003=5` e
  `SEM_CORRESPONDENCIA=1.780`.
- Duas instâncias concorrentes na porta 5050 foram encerradas. O servidor
  atualizado está no PID 17116 e responde pela única escuta da porta.
- API e Chrome reais confirmaram o perfil completo, corte até concurso 100,
  painel compacto e screener inativo.
- Regressão: 410 testes Python, 24 JavaScript, 12 Chrome e três fluxos
  integrados aprovados; nenhum database temporário permaneceu.
- Etapa 16 concluída localmente. PythonAnywhere não foi acessado.
- Próxima ação recomendada: criar commit de segurança da Etapa 16 somente após
  autorização expressa; depois iniciar a subetapa 17.1.

## Atualização — 2026-10-28 — catálogo dos parâmetros de análise

- Subetapa 17.1 implementada como inventário técnico, sem mudança no banco, na
  API, na interface ou no screener.
- `docs/CATALOGO_PARAMETROS_ANALISE.md` relaciona os dez parâmetros, fórmulas,
  unidades, precisões, colunas PostgreSQL e funções Python existentes.
- Soma e média foram marcadas como linearmente equivalentes (`média = soma/6`),
  portanto não deverão ser contadas como dois filtros independentes.
- Foi documentado que `desvio_padrao_media` contém o desvio-padrão populacional
  das seis dezenas de uma linha, não o desvio de uma série histórica de médias.
- Passaram 4 testes específicos e 414 testes Python de regressão. Banco, API,
  interface e regras do screener permaneceram inalterados.
- Próxima ação: aguardar autorização expressa para a 17.2, serviço de janela
  histórica.

## Atualização — 2026-10-28 — serviço de janela histórica

- A subetapa 17.2 criou `selecionar_janela_historica`, sem consultar ou alterar
  banco, API, interface e screener.
- Sem corte, o serviço entrega toda a série validada e ordenada. Os cortes
  `numero_ap_antes_de` e `data_antes_de` são exclusivos e mutuamente exclusivos.
- Assim, o resultado que será avaliado e todos os posteriores não participam
  da amostra do futuro backtest.
- O serviço rejeita concursos duplicados, datas divergentes da ordem dos
  concursos, tipos inválidos e cortes ambíguos.
- Passaram 8 testes específicos e 422 testes Python de regressão. Banco, API,
  interface e regras do screener permaneceram inalterados.
- Próxima ação: aguardar autorização expressa para a 17.3, perfil estatístico
  genérico.

## Atualização — 2026-10-28 — perfil estatístico genérico

- A subetapa 17.3 criou um serviço puro para quantidade, média, desvio-padrão
  populacional, mínimo, máximo e distribuição empírica de qualquer parâmetro.
- Os cálculos usam `Decimal`; a distribuição conserva valor, frequência e
  percentual realmente observados, sem pressupor normalidade.
- As faixas podem usar percentuais da média ou múltiplos do desvio-padrão, com
  margens inferior e superior independentes e limites inclusivos.
- Nenhuma faixa foi conectada ao screener e nenhuma exclusão foi ativada.
- Passaram 8 testes específicos e 430 testes Python de regressão. Banco, API,
  interface e regras do screener permaneceram inalterados.
- Próxima ação: aguardar autorização expressa para a 17.4, perfis geométricos.

## Atualização — 2026-10-28 — perfis geométricos

- A subetapa 17.4 aplica o perfil genérico às seis medidas da tabela de análise
  geométrica: extensão, perímetro, regiões, área e centro X/Y separados.
- Cada parâmetro contabiliza total, valores existentes e ausentes.
- Área zero e quantidade zero permanecem valores válidos. Centro inexistente
  em figura sem área continua nulo e não contamina média ou desvio como zero.
- O serviço rejeita resultado duplicado e incoerências entre área e centro.
- Nenhum perfil foi exposto em API ou ligado ao screener.
- Passaram 7 testes específicos e 437 testes Python de regressão. Banco, API,
  interface e regras do screener permaneceram inalterados.
- Próxima ação: aguardar autorização expressa para a 17.5, API das
  distribuições.

## Atualização — 2026-10-28 — API das distribuições

- A subetapa 17.5 criou `GET /api/perfis/distribuicoes`, somente leitura.
- A resposta reúne os dez parâmetros, janela, tamanho da amostra, média,
  desvio, extremos, faixa, histograma real e curva normal de referência.
- Os cortes por concurso/data são exclusivos; classes e margens são validadas.
- Janela vazia e geometria incompleta são recusadas explicitamente.
- Soma e média são declaradas dependentes e o screener permanece inativo.
- Passaram 9 testes específicos e 446 testes Python de regressão. Uma consulta
  real, somente leitura, processou 3.069 resultados e os dez parâmetros com dez
  classes cada; o screener permaneceu inativo.
- Próxima ação: aguardar autorização expressa para a 17.6, painel com todos os
  gráficos.

## Atualização — 2026-10-28 — painel das distribuições

- A subetapa 17.6 criou `distribuicoes.html`, acessível pela barra compacta.
- Os dez parâmetros aparecem juntos em cartões com histograma real, normal de
  referência, média, desvio, extremos, faixa, amostra e ausências.
- A grade usa rolagem interna e se reorganiza em uma, duas ou três colunas sem
  aumentar continuamente a altura da página.
- A página declara permanentemente que soma/média são dependentes, a normal é
  só referência e o screener está inativo.
- Passaram 25 testes JavaScript, 3 testes específicos e 15 fluxos completos no
  Google Chrome, além de 446 testes Python. A grade ficou contida nas larguras
  de 1.280 e 760 pixels com rolagem interna.
- O servidor Flask local em 5050 não foi reiniciado nesta subetapa; a nova rota
  da API exige reinício antes da visualização real pelo usuário.
- Próxima ação: aguardar autorização expressa para a 17.7, janela de
  configuração das faixas.

## Atualização — 2026-10-28 — configuração das faixas do estudo

- A subetapa 17.7 adicionou um diálogo compacto à página de distribuições.
- O usuário escolhe percentual da média ou múltiplos do desvio e informa
  margens inferior/superior independentes.
- Uma prévia pela API mostra os dez pares de limites antes de habilitar salvar.
- A configuração é persistida no `localStorage` do navegador e restaurada ao
  reabrir a página; ela ainda não é uma regra operacional compartilhada.
- Salvar atualiza somente o estudo e não contém nem ativa estado do screener.
- Passaram 29 testes JavaScript, 16 fluxos completos no Google Chrome e 446
  testes Python. O Chrome confirmou prévia, salvamento e recuperação.
- O servidor Flask local em 5050 continua sem reinício desde a inclusão da nova
  API; ele precisa ser reiniciado antes da conferência manual com dados reais.
- Próxima ação: aguardar autorização expressa para a 17.8, regressão e
  fechamento dos perfis.

## Atualização — 2026-10-28 — fechamento da Etapa 17

- O fechamento reuniu as subetapas 17.1 a 17.7 sem ativar exclusões.
- Foram confirmados 446 testes Python, 29 JavaScript e 16 fluxos no Chrome.
- `netstat` revelou duas instâncias antigas concorrendo na porta 5050; somente
  os PIDs Python 17116 e 34644 foram encerrados.
- Uma única instância atualizada foi iniciada no PID 31468 com `PYTHONPATH`
  absoluto do workspace.
- A API real respondeu saúde `ok`, 3.069 resultados, dez parâmetros e
  `ativa_no_screener=false`.
- A conferência final no Chrome passou usando a página e o PostgreSQL reais,
  sem simular a API: dez gráficos, amostra 3.069 e prévia dos dez limites.
- PythonAnywhere não foi acessado. Commit e push aguardam autorização expressa.

## Atualização — 2026-10-28 — protótipo do screener em três níveis

- A subetapa 18.0 criou `screener-prototipo.html` sem alterar a execução atual.
- O esboço usa dados totalmente fictícios e três blocos: estatística, geometria
  e padrões, com entrada, exclusões, percentuais e saldo.
- Os detalhes são fechados inicialmente e podem ser expandidos em conjunto.
- O bloco de padrões mostra limite de 10%, frequências e lista selecionada.
- A contabilidade fictícia fecha em total inicial = exclusões + aprovadas.
- O protótipo não usa `fetch`, não grava banco e não ativa filtros reais.
- Passaram 33 testes JavaScript, 17 fluxos completos no Google Chrome e 446
  testes Python. A página real respondeu HTTP 200 na porta 5050.
- Próxima ação, após testes e avaliação do usuário: aprovar ou solicitar ajustes
  visuais antes de autorizar a subetapa 18.1.

## Atualização — 2026-10-28 — contrato extensível do novo funil

- A subetapa 18.1 criou um contrato hierárquico separado, sem quebrar o funil
  linear usado pelo ensaio atual.
- Famílias e filtros são definições ordenadas e dinâmicas; não existem colunas
  ou nomes fixos no executor.
- Toda decisão contém código, aprovação/exclusão, motivo e evidências imutáveis.
- A primeira exclusão interrompe a combinação e é contabilizada uma única vez.
- Filtros e famílias informam percentuais sobre total inicial e saldo recebido.
- O fechamento obrigatório é total inicial = excluídas + aprovadas.
- Passaram 7 testes específicos e 453 testes Python de regressão.
- Filtros reais ainda não foram conectados; a próxima ação é aguardar
  autorização para a subetapa 18.2.

## Atualização — 2026-10-28 — fotografia reproduzível da configuração

- A subetapa 18.2 criou uma fotografia canônica e imutável para cada futura
  execução do novo funil.
- Ela congela modo, semente, limite da amostra, ordem de famílias/filtros,
  parâmetros e versões das funções de cálculo.
- Para cada grupo de padrões, registra o intervalo histórico, denominador,
  frequências, política de raridade e a lista excludente calculada no início.
- A classe sem correspondência fecha os 100%, mas nunca se torna um padrão
  excludente.
- Datas, decimais e mapas possuem representação determinística; tipos ambíguos
  são recusados. O JSON canônico recebe checksum SHA-256 verificável.
- A fotografia ainda não é persistida nem ligada ao ensaio real; isso ocorrerá
  nas subetapas de integração do novo screener.
- Passaram 8 testes específicos e 461 testes Python de regressão; os três
  arquivos da subetapa também passaram pela validação sintática em memória.
- Próxima ação: aguardar autorização expressa para a subetapa 18.3, conexão da
  família estatística ao contrato extensível.

## Atualização — 2026-10-28 — família estatística extensível

- A subetapa 18.3 conectou a primeira família real ao contrato do novo funil.
- `EST_SOMA_MEDIA` trata soma e média em uma única decisão, pois a média é
  exatamente a soma dividida por seis; a evidência conserva as duas medidas e
  seus limites equivalentes sem gerar dupla exclusão.
- `EST_MEDIANA` e `EST_DESVIO_PADRAO` são filtros independentes e recebem apenas
  o saldo aprovado pelos filtros anteriores.
- Todos os cálculos reutilizam as funções oficiais do domínio, importantes para
  a futura auditoria.
- As faixas são fechadas: valores exatamente nos limites são aprovados.
- Passaram 5 testes específicos e 466 testes Python de regressão.
- A família ainda não foi ligada à interface, API ou amostra de 5.000.
- Próxima ação: aguardar autorização para a subetapa 18.4, família geométrica.

## Atualização — 2026-10-28 — família geométrica extensível

- A subetapa 18.4 conectou a família geométrica ao contrato do novo funil.
- Os filtros são extensão, perímetro, área, quantidade de regiões e centro de
  gravidade; X e Y do centro constituem uma decisão única.
- Cada combinação tem uma única análise geométrica compartilhada pelos filtros.
- A primeira exclusão interrompe a combinação, produzindo subtotal líquido.
- Faixas são fechadas e aceitam os valores exatamente nos limites.
- Figuras sem centro de gravidade exigem política explícita `aprovar` ou
  `excluir`; essa política deverá integrar a fotografia do screener completo.
- Passaram 7 testes específicos e 473 testes Python de regressão.
- A família ainda não foi ligada à interface, banco ou amostra de 5.000.
- Próxima ação: aguardar autorização para a subetapa 18.5, grupos de padrões.

## Atualização — 2026-10-28 — família extensível de padrões

- A subetapa 18.5 conectou os grupos de padrões ao novo funil.
- Cada grupo fotografado produz um filtro e classifica cada combinação uma vez.
- A exclusão consulta apenas a lista rara congelada pela fotografia da execução.
- A classe sem correspondência fecha os 100%, mas nunca vira padrão excludente.
- A evidência contém classe, frequência, denominador, política e detalhes do
  classificador, permitindo futura auditoria.
- O classificador oficial PG_001 foi adaptado; a estrutura aceita novos grupos,
  mas exige que cada um possua classificador específico e resposta reconciliada.
- Passaram 6 testes específicos e 479 testes Python de regressão.
- Próxima ação: aguardar autorização para a subetapa 18.6, quadro contábil
  consolidado das três famílias.

## Atualização — 2026-10-28 — quadro contábil consolidado

- A subetapa 18.6 criou a visão serializável das três famílias do novo funil.
- O quadro distingue universo total, amostra analisada e execução integral.
- Cada filtro mostra entrada, avaliações, exclusões, percentuais sobre total e
  saldo recebido, além do saldo final.
- Cada família mostra entrada, subtotal líquido e saldo entregue à seguinte.
- Todas as transições e percentuais são recalculados e comparados; relatórios
  adulterados ou não reconciliados são recusados.
- A equação obrigatória é total analisado = excluído + aprovado.
- Passaram 7 testes específicos e 486 testes Python de regressão.
- O quadro ainda não foi conectado à API ou interface.
- Próxima ação: aguardar autorização para a subetapa 18.7, interface expansível.

## Atualização — 2026-10-28 — interface expansível do novo screener

- A subetapa 18.7 criou `screener-extensivel.html`, ligada ao formato real do
  quadro consolidado e sem números fictícios.
- A tela mostra resumo, três famílias recolhidas, filtros expansíveis, dois
  percentuais, saldos e fechamento, conservando espaço vertical e horizontal.
- Ficou registrada a regra: cadastro não gera filtro. Cada grupo exige função
  Python, testes, versão e integração; sem isso ele não participa da execução.
- O botão de execução permanece desabilitado e nenhuma API é chamada; a amostra
  de 5.000 será conectada somente na subetapa 18.8.
- Passaram 35 testes JavaScript e 18 testes completos no Google Chrome.
- A página respondeu HTTP 200 no servidor local em 5050.
- Próxima ação: aguardar autorização para a subetapa 18.8, ensaio protegido e
  fechamento da Etapa 18.

## Atualização — 2026-10-28 — fechamento da Etapa 18

- A subetapa 18.8 ligou o novo quadro à API e executou somente 5.000 combinações.
- O modo integral continua bloqueado por configuração, validação e ausência de
  parâmetro de ampliação na API POST.
- A configuração foi fotografada com SHA-256
  `10f549c1b1c6cd4e05b38d8f8b981a5db33bedb6fb101805e322530bb0274db3`.
- O novo funil excluiu 2.999 em estatística, 1.578 em geometria e 3 em PG_001,
  aprovando 420; a contabilidade fecha em 5.000.
- Na mesma amostra, o screener anterior aprovou 4.409. A diferença não representa
  superioridade porque ordem, faixas e conjunto de filtros são diferentes.
- Passaram 487 testes Python, 35 JavaScript, 18 fluxos controlados no Chrome e
  um fluxo Chrome/PostgreSQL real.
- Duas instâncias locais concorrentes, PIDs 31468 e 39120, foram encerradas; o
  servidor atualizado é o único listener, PID 34596, na porta 5050.
- A Etapa 18 está implementada e testada, mas ainda não foi commitada.
- Próxima ação: aguardar autorização para o commit de segurança da Etapa 18 ou
  orientação do usuário sobre a etapa seguinte.
