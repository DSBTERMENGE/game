# API de grupos de padrões

Base local: `/api/grupos-padroes`.

## Operações

- `GET /api/grupos-padroes`: lista os grupos por código;
- `POST /api/grupos-padroes`: cria um grupo;
- `PUT /api/grupos-padroes/PG_001`: edita nome e descrição;
- `DELETE /api/grupos-padroes/PG_001`: exclui somente um grupo vazio.

Corpo permitido na criação e edição:

```json
{
  "grupo_nome": "Dezenas sequenciais",
  "grupo_descr": "Padrões baseados em dezenas consecutivas."
}
```

`id_grupo` e `grupo_cod` são gerados pelo sistema e rejeitados quando enviados
pelo usuário. Nome e descrição são obrigatórios; o nome aceita até 200
caracteres e a descrição até 4.000.

## Respostas funcionais

- `400`: JSON, código, campo ou texto inválido;
- `404 GRUPO_NAO_ENCONTRADO`: código válido, mas ausente;
- `409 GRUPO_DUPLICADO`: nome normalizado já cadastrado;
- `409 GRUPO_EM_USO`: grupo ainda possui padrões associados;
- `503 BANCO_INDISPONIVEL`: falha técnica apresentada sem SQL ou credenciais.
