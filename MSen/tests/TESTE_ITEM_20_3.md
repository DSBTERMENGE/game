# Teste da subetapa 20.3 — aplicação local controlada

Data: 30/10/2026

## Escopo

Aplicação das migrações 011, 012 e 013 exclusivamente ao PostgreSQL local
`games`, depois de backup e validação do estado inicial. Não houve carga das 200
amostras, cadastro de critérios, API, frontend, sincronização ou alteração no
PythonAnywhere.

## Proteção anterior

Backup customizado criado antes das migrações:

- arquivo: `MSen/dados/backups/games_pre_validacao_20_3_20261030_034347.dump`;
- tamanho: 241.429 bytes;
- SHA-256: `8FB22487F55AD1EF39A19C0039B81E877713094184DDA5D5EA78074BF390DF51`;
- catálogo validado com 117 itens, incluindo `resultados`, `padroes_grupo` e
  `schema_migrations`.

## Estado anterior

- migrações registradas: 001–010;
- resultados: 3.069;
- grupos: 3;
- subgrupos: 9;
- classificações de padrões: 1.289.

## Aplicação e idempotência

- primeira execução: aplicou somente 011, 012 e 013;
- segunda execução: nenhuma migração aplicada;
- estado final registrado: 001–013.

## Auditoria final

Os totais preexistentes permaneceram iguais:

- resultados: 3.069;
- grupos: 3;
- subgrupos: 9;
- classificações de padrões: 1.289.

Estado das tabelas novas:

- `amostras_validacao`: 0 linhas;
- `criterios_validacao`: 0 linhas;
- `avaliacoes_validacao`: 0 linhas;
- `estado_algoritmo_selecao`: uma linha, `atualizado = FALSE`, motivo
  `AGUARDANDO_HOMOLOGACAO_INICIAL` e quantidade de resultados do perfil igual
  a zero.

## Regressão

Resultado: **520 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.3 aprovada. O PostgreSQL local possui agora as estruturas vazias de
validação e o estado global bloqueado. A carga ou manipulação dessas estruturas
pertence às próximas subetapas e não foi antecipada.
