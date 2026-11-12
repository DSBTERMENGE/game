# API da Gestão do desenvolvimento

Base: `/api/gestao-desenvolvimento`.

## Operações

- `GET /api/gestao-desenvolvimento`: pesquisa paginada. Aceita `busca`, `tipo`,
  `status_trabalho`, `status_publicacao`, `arquivados`, `pagina` e
  `por_pagina`. A ordem é fixa pela criação do registro.
- `GET /api/gestao-desenvolvimento/{id}`: consulta um registro técnico.
- `GET /api/gestao-desenvolvimento/{id}/historico`: consulta seu histórico
  imutável.
- `POST /api/gestao-desenvolvimento`: cria um registro depois da confirmação
  realizada pela futura interface. Exige `dados` e `chave_idempotencia` SHA-256.
- `PUT /api/gestao-desenvolvimento/{id}`: atualiza os dados. Exige
  `versao_registro`; uma versão ultrapassada produz conflito HTTP 409.
- `POST /api/gestao-desenvolvimento/{id}/arquivamento`: arquiva sem excluir.
- `DELETE /api/gestao-desenvolvimento/{id}/arquivamento`: desarquiva.

O identificador é técnico e não deve ser apresentado como numeração funcional.
Não existe endpoint de exclusão física.

## Idempotência e concorrência

A mesma chave de idempotência devolve o registro já criado sem criar outro. A
primeira criação responde HTTP 201; a repetição segura responde HTTP 200 com
`criado: false`. Atualização, arquivamento e desarquivamento usam concorrência
otimista por `versao_registro`.

## Ordem da consulta

Os registros seguem sempre a ordem de criação. Não há parâmetro de ordenação.

Erros de validação não expõem SQL, credenciais ou mensagens internas do banco.
