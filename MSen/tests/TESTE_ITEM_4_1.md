# Teste do Item 4.1 — configuração e conexão PostgreSQL

Data: 2026-10-26.

## Dependência

Foi adotado `psycopg[binary]>=3.3.6,<4`, registrado em `pyproject.toml`. A versão
3.3.6 foi instalada no ambiente local de teste.

## Testes automatizados

- nove testes específicos aprovados;
- 92 testes acumulados aprovados;
- configuração válida;
- senha ausente ou vazia rejeitada;
- porta, tempo limite e `sslmode` inválidos rejeitados;
- senha ocultada na representação da configuração;
- parâmetros enviados separadamente ao driver;
- mensagem de falha sem exposição da credencial;
- conexão rejeita configuração não validada.

## Teste real isolado

Foi criado um cluster PostgreSQL 16.11 temporário na porta 55441, com database
`games_test`. Uma credencial fictícia foi fornecida ao código, embora o cluster
descartável usasse autenticação `trust`.

Resultados:

- conexão válida: database `games_test`, usuário `postgres`, versão de servidor
  `160011`;
- database inexistente: rejeitado com código `FALHA_CONEXAO` e mensagem sem
  credenciais;
- cluster temporário: parado e removido ao final;
- PostgreSQL local persistente 16 e 18: não alterados;
- PythonAnywhere: não acessado.

Nenhuma migração, tabela ou dado foi criado em ambiente persistente.
