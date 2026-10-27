# Banco de dados do Game / MSen

Esta pasta contém a estrutura PostgreSQL versionada do projeto. O banco
planejado chama-se `games`, mas os arquivos SQL não criam o database nem fazem
troca automática de conexão. Eles devem ser executados somente depois de
confirmar o ambiente e o banco de destino.

## Arquivos

- `schema_postgresql.sql`: estrutura completa atual para uma instalação nova;
- `migrations/001_criar_estrutura_inicial.sql`: primeira alteração incremental,
  com as três tabelas aprovadas;
- `migrations/002_criar_tabela_padroes.sql`: cadastro e resumo estatístico dos
  padrões;
- `migrations/003_inicializar_catalogo_padroes.sql`: três registros iniciais e
  sequência de códigos que não reutiliza exclusões;
- `migrations/003_inicializar_catalogo_padroes.sql`: três registros iniciais e
  sequência de códigos que não reutiliza exclusões;
- `seeds/README.md`: regras para dados iniciais e importados.

## Regras

1. Não colocar senhas ou endereços privados nos arquivos SQL.
2. Não incluir dados da planilha no DDL.
3. Toda alteração futura deve receber uma nova migração numerada.
4. Nunca editar uma migração já aplicada em algum ambiente; criar a próxima.
5. Antes de executar, confirmar servidor, database, usuário e existência de
   backup quando houver dados importantes.

## Execução

O executor Python aplica, em ordem, somente as migrações ainda não registradas e
confere o checksum das já executadas. `schema_postgresql.sql` representa a
estrutura completa para uma instalação nova.

O banco local persistente só pode receber uma migração depois dos testes e da
autorização correspondente. O PythonAnywhere permanece fora do escopo até a
conclusão de todo o desenvolvimento local.
