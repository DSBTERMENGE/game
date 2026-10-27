# API de padrões

## Contrato geral

Todas as rotas usam JSON. Somente `padrao_nome` e `padrao_descr` são aceitos em
operações de escrita. `id_padrao`, `padrao_cod`, `num_oco`, `intervalo_medio` e
`desv_padrao` são controlados pelo sistema e uma tentativa de enviá-los retorna
erro `400 CAMPOS_PROTEGIDOS`.

## Listar

```http
GET /api/padroes
```

Resposta `200`:

```json
{
  "total": 1,
  "padroes": [
    {
      "id_padrao": 1,
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
calculadas são `null`. `detector_implementado` é calculado pela aplicação.

## Criar

```http
POST /api/padroes
Content-Type: application/json

{
  "padrao_nome": "Novo padrão",
  "padrao_descr": "Descrição detalhada"
}
```

Retorna `201` com o código automático. Um cadastro novo sem função Python tem
estatísticas nulas e `detector_implementado: false`.

## Editar textos

```http
PUT /api/padroes/PD_001
Content-Type: application/json

{
  "padrao_nome": "Nome revisto",
  "padrao_descr": "Descrição revista"
}
```

Retorna `200`. Código e estatísticas permanecem inalterados.

## Excluir

```http
DELETE /api/padroes/PD_001
```

Retorna `200` com o registro removido. O frontend deverá pedir confirmação. O
código excluído não será reutilizado e o recálculo não recriará o cadastro.

## Erros principais

- `400`: JSON, código, textos ou campos inválidos;
- `404 PADRAO_NAO_ENCONTRADO`;
- `409 PADRAO_DUPLICADO`;
- `503 BANCO_INDISPONIVEL`, sem detalhes internos ou credenciais.
