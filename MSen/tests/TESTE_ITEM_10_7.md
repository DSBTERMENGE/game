# Evidências do Item 10.7 — API de padrões vinculados a grupos

Data: 2026-10-27.

## Implementação

A API `/api/padroes` agora:

- exige `grupo_cod` na criação e edição;
- retorna `id_grupo`, `grupo_cod` e `grupo_nome`;
- permite filtrar `GET /api/padroes?grupo_cod=PG_001`;
- permite transferir um padrão para outro grupo;
- protege `id_grupo` e `grupo_nome` contra escrita;
- distingue grupo inválido de grupo válido inexistente.

## Testes

- 13 testes simulados da API de padrões: aprovados;
- 11 testes simulados da API de grupos: aprovados;
- 7 testes da fábrica Flask: aprovados;
- 5 testes unitários do repositório de padrões: aprovados;
- fluxo HTTP real em PostgreSQL temporário: aprovado.

O fluxo real criou `PG_002`, criou `PD_004` associado, filtrou pelo grupo,
transferiu o padrão para `PG_001` e excluiu `PG_002` depois de vazio. O database
temporário foi removido e a auditoria final retornou lista vazia.

O database `games` não foi alterado. A interface atual ainda não envia
`grupo_cod`; por isso, a aplicação local da migração deve ocorrer somente após
a adaptação do frontend.
