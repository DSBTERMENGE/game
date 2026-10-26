# Plano do banco de dados PostgreSQL

> O modelo revisado mais recente está em `docs/MODELO_POSTGRESQL.md`. O resumo
> abaixo contém partes históricas e não deve ser usado para executar o DDL atual
> antes da conclusão dos Itens 1.3 e 1.4.

## Situação atual

O banco ainda não foi criado pelo projeto. O nome planejado é `games`. A
planilha atual possui as colunas `Concurso`, `Data` e `bola 1` a `bola 6`, com
dados a partir da linha 8.

O FinCtl serve apenas como referência de organização. Seu esquema financeiro
não deve ser copiado para este banco.

## Modelo inicial histórico

### `resultados`

- `numero_concurso`: inteiro positivo, chave primária e número oficial;
- `data_sorteio`: data obrigatória;
- `bola_1` a `bola_6`: inteiros pequenos obrigatórios, entre 1 e 60.

As seis bolas permanecem na ordem original do sorteio. Uma restrição impede a
repetição de uma dezena dentro do mesmo concurso. Não serão criados campos
genéricos de reserva; novos campos receberão nome, tipo e regras por migrações
futuras quando seu significado estiver definido.

### `schema_migrations`

- `versao`: identificador único da migração;
- `nome`: descrição curta;
- `aplicada_em`: data e hora da aplicação.

## Objetos derivados inicialmente previstos

- índice pela data do sorteio;
- consultas de frequência e última ocorrência, inicialmente pelo código Python.

Views adicionais serão criadas somente quando houver uma consulta real que as
justifique.

## Organização planejada dos arquivos

```text
database/
├── README.md
├── schema_postgresql.sql
├── migrations/
│   └── 001_criar_estrutura_inicial.sql
└── seeds/
    └── README.md
```

`schema_postgresql.sql` representará a estrutura completa para instalações
novas. `migrations` conterá alterações incrementais para bancos existentes.
Dados históricos importados da planilha não serão misturados ao DDL.

## Inicialização e migrações

Ao iniciar, o Python deverá:

1. obter a configuração pelas variáveis de ambiente;
2. conectar ao banco já provisionado;
3. adquirir uma trava PostgreSQL para evitar migrações simultâneas;
4. criar o controle de migrações se ele ainda não existir;
5. aplicar, em ordem e dentro de transações, apenas arquivos pendentes;
6. registrar cada migração concluída;
7. interromper a inicialização e preservar o banco se houver erro.

O executor desses passos foi implementado no Item 4.2 em
`MSen/src/msen/database/migrations.py`. A trava consultiva é mantida durante toda
a verificação e aplicação. Cada arquivo e sua linha em `schema_migrations`
pertencem à mesma transação. Arquivos já aplicados precisam conservar exatamente
o SHA-256 original; uma divergência interrompe a execução.

Os invólucros `BEGIN` e `COMMIT` existentes nos arquivos SQL são retirados em
memória antes da execução, deixando a transação sob controle do Python. Os
arquivos versionados não são reescritos por esse processo.

No PythonAnywhere, a criação do banco e as alterações de produção deverão ser
uma etapa controlada da publicação. O carregamento do WSGI poderá conferir a
versão, mas não deverá recriar tabelas, apagar objetos ou importar a planilha a
cada acesso.

## Configuração prevista

- `GAME_DB_HOST`;
- `GAME_DB_PORT`;
- `GAME_DB_NAME`;
- `GAME_DB_USER`;
- `GAME_DB_PASSWORD`;
- `GAME_DB_SSLMODE`, quando necessário.
- `GAME_DB_CONNECT_TIMEOUT`, opcional, entre 1 e 60 segundos.

O arquivo `.env` local será ignorado. Um `.env.example`, sem valores secretos,
poderá documentar as variáveis obrigatórias.

A camada de configuração e conexão foi implementada no Item 4.1 com Psycopg 3.
Ela não lê automaticamente arquivos `.env`: o sistema operacional, o processo
de inicialização ou o painel de hospedagem deve fornecer as variáveis. O arquivo
`MSen/.env.example` serve somente como modelo sem credenciais reais.

## Validações essenciais

- concurso positivo e único;
- data válida;
- exatamente seis dezenas por concurso;
- dezenas entre 1 e 60;
- nenhuma dezena repetida no mesmo concurso;
- importação repetida sem duplicações;
- rollback integral quando uma operação falhar.

## Estado da execução

O DDL e a migração inicial foram criados em 2026-10-25. Eles ainda não foram
executados em um servidor PostgreSQL porque `psql` não está disponível no
ambiente local atual. Depois disso foram definidos novos campos calculados e um
identificador próprio; portanto, o DDL deverá ser revisado antes de qualquer
execução. Nada foi alterado no PythonAnywhere.

Em 2026-10-26 o modelo foi aprovado e traduzido para o DDL da migração
`001_criar_estrutura_inicial.sql`. O SQL foi executado duas vezes em um cluster
PostgreSQL 16.11 temporário, com testes de restrição e reversão aprovados. O
cluster foi removido. Nenhum banco persistente ou remoto foi alterado.

Ainda em 2026-10-26 foi criado o database local e exclusivo `games` no
PostgreSQL 16.11 (`127.0.0.1:5432`). A migração `001` foi aplicada e a fonte
inicial foi importada com 3.069 resultados e 60 linhas de frequência. A
reimportação não criou duplicações. O database `financas` e os demais projetos
não participaram da operação.

## Backup e segurança

- não versionar dumps, senhas ou arquivos `.env`;
- gerar backup antes de migrações de produção;
- manter procedimento documentado de restauração;
- usar usuário de aplicação com apenas os privilégios necessários;
- nunca aceitar nomes de tabela ou trechos SQL vindos diretamente da interface.
