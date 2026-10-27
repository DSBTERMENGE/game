# Evidências do Item 10.2 — migração isolada de grupos de padrões

Data: 2026-10-27.

## Escopo

- migração `004_organizar_grupos_de_padroes.sql`;
- esquema canônico atualizado para instalações novas;
- PostgreSQL temporário, sem acesso ao database local `games`;
- nenhuma alteração no PythonAnywhere.

## Cenário migrado

O database efêmero recebeu primeiro somente as migrações `001`, `002` e `003`.
Antes da migração `004`, o padrão `PD_001` recebeu valores conhecidos:

```text
num_oco = 2
intervalo_medio = 15
desv_padrao = 0
```

Depois foi executado o mecanismo normal de migrações, aplicando apenas a versão
`004` pendente.

## Resultado

- tabelas finais: `padroes_grupo` e `padroes_subgrupo`;
- tabela antiga `padroes` ausente;
- versões registradas: `001`, `002`, `003` e `004`;
- `PG_001 — Dezenas sequenciais` e `PG_002 — Dezenas na mesma coluna` criados;
- `PD_001`–`PD_003` preservados em `PG_001`;
- `PD_004`–`PD_006` preservados em `PG_002` no ensaio ampliado do Item 10.3;
- valores estatísticos conhecidos de `PD_001` preservados;
- sequências de códigos posicionadas no maior código existente;
- duplicidade normalizada de grupo rejeitada;
- duplicidade normalizada de padrão dentro do grupo rejeitada;
- grupo inexistente rejeitado;
- exclusão de grupo ocupado rejeitada pela chave estrangeira.
- esquema canônico executado do zero, criando dois grupos e três padrões;
- 10 testes unitários direcionados do mecanismo e suporte de migrações
  aprovados.

O database temporário foi removido. A auditoria final retornou lista vazia de
databases de teste.
