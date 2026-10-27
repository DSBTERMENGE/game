# API de padrões

## Contrato geral

Todas as rotas usam JSON. `grupo_cod`, `padrao_nome` e `padrao_descr` são
obrigatórios nas operações de escrita. `id_padrao`, `id_grupo`, `grupo_nome`,
`padrao_cod`, `num_oco`, `intervalo_medio` e `desv_padrao` são controlados pelo
sistema e uma tentativa de enviá-los retorna `400 CAMPOS_PROTEGIDOS`.

## Listar

```http
GET /api/padroes
```

A listagem pode ser filtrada com `GET /api/padroes?grupo_cod=PG_001`.

Resposta `200`:

```json
{
  "total": 1,
  "padroes": [
    {
      "id_padrao": 1,
      "id_grupo": 1,
      "grupo_cod": "PG_001",
      "grupo_nome": "Dezenas sequenciais",
      "padrao_cod": "PD_001",
      "padrao_nome": "Duas dezenas sequenciais",
      "padrao_descr": "Descrição da regra",
      "num_oco": 1192,
      "intervalo_medio": "2.575147",
      "desv_padrao": "1.995592",
      "detector_implementado": true
    }
  ]
}
```

Valores decimais são textos para preservar precisão. Estatísticas ainda não
calculadas são `null`. `detector_implementado` é calculado pela aplicação;
atualmente os códigos `PD_001`–`PD_006` possuem detector.

## Criar

```http
POST /api/padroes
Content-Type: application/json

{
  "grupo_cod": "PG_001",
  "padrao_nome": "Novo padrão",
  "padrao_descr": "Descrição detalhada"
}
```

Retorna `201` com o código automático. Os códigos `PD_001`–`PD_006` são
reservados para os detectores oficiais. Portanto, o primeiro padrão livre recebe
`PD_007`; enquanto não possuir função Python, terá estatísticas nulas e
`detector_implementado: false`.

## Editar grupo e textos

```http
PUT /api/padroes/PD_001
Content-Type: application/json

{
  "grupo_cod": "PG_001",
  "padrao_nome": "Nome revisto",
  "padrao_descr": "Descrição revista"
}
```

Retorna `200`. O padrão pode ser transferido para outro grupo válido. Código e
estatísticas permanecem inalterados.

## Excluir

```http
DELETE /api/padroes/PD_001
```

Retorna `200` com o registro removido. O frontend deverá pedir confirmação. O
código excluído não será reutilizado e o recálculo não recriará o cadastro.

## Erros principais

- `400`: JSON, código, textos ou campos inválidos;
- `404 PADRAO_NAO_ENCONTRADO`;
- `404 GRUPO_NAO_ENCONTRADO`;
- `409 PADRAO_DUPLICADO`;
- `503 BANCO_INDISPONIVEL`, sem detalhes internos ou credenciais.
