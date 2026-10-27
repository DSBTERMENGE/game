# Evidências do Item 10.4 — repositório de grupos de padrões

Data: 2026-10-27.

## Implementação

Foi criado `msen.database.grupos_padroes_repository`, separado do repositório
de padrões. O módulo oferece:

- listagem ordenada por código;
- criação com código automático não reutilizável;
- edição somente de nome e descrição;
- consulta da existência de padrões associados;
- exclusão somente de grupo vazio;
- erros funcionais seguros, sem SQL ou credenciais;
- docstrings em português nas funções, métodos e tipos públicos.

## Testes

- 5 testes unitários de mapeamento, validação e contrato: aprovados;
- CRUD real em PostgreSQL temporário: aprovado;
- grupos iniciais `PG_001` e `PG_002` encontrados;
- duplicidade normalizada rejeitada como `GRUPO_DUPLICADO`;
- exclusão do grupo ocupado rejeitada como `GRUPO_EM_USO`;
- grupo ausente informado como `GRUPO_NAO_ENCONTRADO`;
- após excluir `PG_003` e consumir uma tentativa duplicada, o próximo código
  foi `PG_005`, confirmando que códigos não são reutilizados.

O database temporário foi removido e a auditoria final retornou lista vazia. O
database `games`, a API, o frontend e o PythonAnywhere não foram alterados.
