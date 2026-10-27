# Contrato da API de resultados

## `GET /api/resultados`

## Resposta de sucesso

HTTP 200 com:

```json
{
  "total": 1,
  "resultados": [
    {
      "id_resultado": 1,
      "data_resultado": "2026-10-11",
      "numero_ap": 3069,
      "dezenas": [47, 5, 22, 44, 57, 19],
      "res_01": 47,
      "res_02": 5,
      "res_03": 22,
      "res_04": 44,
      "res_05": 57,
      "res_06": 19,
      "soma_res": 194,
      "media_aritmetica_res": "32.333333",
      "mediana_res": "33.0",
      "desvio_padrao_media": "18.217818",
      "media_coordenada_x": "4.666667",
      "media_coordenada_y": "2.666667",
      "versao_calculo": 1
    }
  ]
}
```

Os resultados são ordenados por `numero_ap` crescente. Datas usam ISO 8601.
Decimais são enviados como texto para preservar exatamente a precisão do
PostgreSQL; o frontend pode convertê-los para número apenas quando precisar
desenhá-los.

Banco vazio retorna HTTP 200 com `total: 0` e lista vazia.

O parâmetro opcional `incluir_geometria=0` omite `analise_geometrica` da
lista. O painel usa essa forma leve e consulta a geometria apenas do resultado
selecionado em `GET /api/resultados/<numero_ap>/geometria`. Essa rota retorna
`numero_ap` e `analise_geometrica`, ou HTTP 404 quando o concurso não existe.

## Falha de acesso ao banco

HTTP 503 com código `BANCO_INDISPONIVEL` e mensagem genérica. A resposta não
inclui host, usuário, senha, string de conexão nem mensagem bruta do driver.

## `POST /api/resultados/importar`

Recebe `multipart/form-data` com a planilha no campo `arquivo`. Somente a
extensão `.xlsx` é aceita e o corpo completo pode ter no máximo 10 MiB. O
arquivo é processado numa pasta temporária e apagado ao fim da requisição.

O sucesso retorna HTTP 200 com uma mensagem e o relatório incremental:

```json
{
  "mensagem": "Importação concluída: 1 resultado(s) inserido(s).",
  "relatorio": {
    "arquivo": "resultados.xlsx",
    "registros_antes": 3069,
    "registros_depois": 3070,
    "linhas_analisadas": 3070,
    "novas": 1,
    "inseridas": 1,
    "iguais": 3069,
    "alteradas": 0,
    "invalidas": 0
  }
}
```

O relatório também inclui hash SHA-256, horários, concursos inseridos e
alterados e números das linhas inválidas. Concursos iguais não são duplicados;
divergências antigas são relatadas sem sobrescrita silenciosa.

Erros usam sempre `erro.codigo` e `erro.mensagem`:

- HTTP 400: arquivo ausente ou vazio;
- HTTP 415: extensão diferente de `.xlsx`;
- HTTP 422: conteúdo que não forma uma planilha XLSX válida;
- HTTP 413: limite de tamanho excedido;
- HTTP 503: banco ou importação indisponível, sem detalhes internos.

## `POST /api/resultados`

Inclui um resultado individual. O corpo é JSON:

```json
{
  "numero_ap": 3070,
  "data_resultado": "2026-10-20",
  "dezenas": [1, 10, 20, 30, 40, 60]
}
```

A data aceita `AAAA-MM-DD` ou `DD/MM/AAAA`. Em lugar de `dezenas`, também é
possível informar `res_01` a `res_06`. Campos derivados eventualmente enviados
são ignorados: o servidor sempre recalcula soma, médias, mediana, desvio-padrão
e coordenadas. O sucesso retorna HTTP 201 e `resultado` com o registro completo.

## `PUT /api/resultados/<numero_ap>`

Edita um resultado existente e recalcula todos os campos derivados. O corpo usa
o mesmo formato da inclusão; `numero_ap` pode ser omitido, pois vem da URL. Se
for informado, deverá ser idêntico ao número da URL. O sucesso retorna HTTP 200.

Inclusão, edição e recálculo das 60 frequências pertencem à mesma transação.
Os erros previstos são:

- HTTP 400: JSON ou dados de entrada inválidos;
- HTTP 404: concurso a editar inexistente;
- HTTP 409: concurso duplicado ou número divergente entre URL e corpo;
- HTTP 503: falha de banco, sem confirmação parcial nem detalhes internos.
