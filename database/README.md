# Banco de dados do Game / MSen

Esta pasta contém a estrutura PostgreSQL versionada do projeto. O banco
planejado chama-se `games`, mas os arquivos SQL não criam o database nem fazem
troca automática de conexão. Eles devem ser executados somente depois de
confirmar o ambiente e o banco de destino.

## Arquivos

- `schema_postgresql.sql`: estrutura completa atual para uma instalação nova;
- `migrations/001_criar_estrutura_inicial.sql`: primeira alteração incremental,
  com as três tabelas aprovadas;
- `seeds/README.md`: regras para dados iniciais e importados.

## Regras

1. Não colocar senhas ou endereços privados nos arquivos SQL.
2. Não incluir dados da planilha no DDL.
3. Toda alteração futura deve receber uma nova migração numerada.
4. Nunca editar uma migração já aplicada em algum ambiente; criar a próxima.
5. Antes de executar, confirmar servidor, database, usuário e existência de
   backup quando houver dados importantes.

## Execução futura

Quando o PostgreSQL estiver configurado, a estrutura completa poderá ser
aplicada ao database `games` com um cliente PostgreSQL. A aplicação Python terá
posteriormente um executor que aplicará apenas migrações ainda não registradas.

Os arquivos não devem ser executados no banco local persistente nem no
PythonAnywhere antes da conclusão dos testes e da autorização correspondente.
