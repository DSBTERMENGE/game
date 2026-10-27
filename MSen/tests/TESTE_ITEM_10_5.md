# Evidências do Item 10.5 — repositório de padrões por grupo

Data: 2026-10-27.

## Implementação

O `RepositorioPadroes` passou a usar `padroes_subgrupo` e a sequência
`padroes_subgrupo_codigo_seq`. Cada linha recuperada contém também
`id_grupo`, `grupo_cod` e `grupo_nome`.

As operações agora:

- exigem grupo válido na criação;
- permitem transferir o padrão ao editar seus textos;
- listam todos os padrões ou filtram por grupo;
- preservam código e estatísticas durante a transferência;
- mantêm recálculo, exclusão e códigos não reutilizáveis;
- informam `GRUPO_NAO_ENCONTRADO` sem expor detalhes do banco.

## Testes

- 10 testes unitários dos dois repositórios: aprovados;
- 10 testes direcionados da API simulada: aprovados;
- 7 testes da estrutura e documentação dos padrões: aprovados;
- fluxo real em PostgreSQL temporário: aprovado;
- estatísticas esperadas dos detectores preservadas;
- recálculo idempotente e texto editado preservado;
- associação inicial a `PG_002`, filtro por grupo e transferência a `PG_001`
  confirmados;
- grupo inexistente rejeitado;
- exclusão respeitada e códigos de padrão não reutilizados.

O database temporário foi removido e a auditoria final não encontrou databases
de teste. `games` e PythonAnywhere não foram alterados.
