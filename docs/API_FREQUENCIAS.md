# API — Frequência das dezenas

Base: `/api/frequencias`.

## Consultas

### `GET /estado`

Devolve configuração ativa, resumo de `resultados`, geração ativa e quantidade
de linhas históricas.

### `GET /fotografia-atual`

Aceita `tipo_evento=SIMPLES|2VS|3VS` (padrão `SIMPLES`) e devolve exatamente as
60 dezenas desse tipo na última fotografia da geração ativa, com quantidades,
mínimo, máximo, média, mediana e desvio na unidade concurso.

### `GET /serie`

Parâmetros:

- `dezena`: obrigatório, inteiro de 1 a 60;
- `tipo_evento`: obrigatório, `SIMPLES`, `2VS` ou `3VS`;
- `concurso_inicial` e `concurso_final`: opcionais e inclusivos.

Cada requisição devolve uma única série. O período é limitado a 5.000 concursos
e nunca inclui cópia das seis dezenas dos resultados. `ocorrencias_reais`
contém somente os números dos concursos em que o evento selecionado terminou,
consultados diretamente de `resultados`: presença para `SIMPLES`, segunda
presença consecutiva para `2VS` e terceira para `3VS`.

`assertividade` avalia cada fotografia contra o próximo evento conhecido. Os
limites são inclusivos. O erro absoluto é a distância entre ocorrência real e
previsão central; o erro percentual divide essa distância pelo intervalo real
entre o evento anterior e o próximo. Casos sem evento anterior, estatística
completa ou próximo evento conhecido são censurados e ficam fora do denominador.

## Prévia

### `POST /previa`

Recebe:

```json
{
  "configuracao": { "...": "campos completos da configuração" },
  "salvar_dados": true
}
```

Informa primeira carga, ausência de alteração, incremental ou reconstrução.
Quando incremental, lista os concursos novos. Quando a configuração diverge,
lista campo, valor gravado e valor calculado.

## Execuções assíncronas

### `POST /execucoes`

Recebe configuração, `salvar_dados`, `confirmacao_gravacao` e
`reconstruir_origem`. Se `salvar_dados=true`, a confirmação precisa ser `true`
antes de a tarefa ser criada.

### `GET /execucoes/{id}`

Devolve estado, etapa, concluído, total, percentual, duração, resultado ou erro.

### `POST /execucoes/{id}/cancelamento`

Solicita cancelamento. A tarefa muda para `CANCELAMENTO_SOLICITADO` até alcançar
um ponto seguro e termina como `CANCELADA`; gravações parciais são revertidas.

Somente uma execução pode estar ativa. Nova tentativa recebe HTTP 409.

## Erros principais

- `PARAMETRO_INVALIDO` e `CONFIGURACAO_INVALIDA`: HTTP 400;
- `CONFIRMACAO_OBRIGATORIA`: HTTP 400;
- `EXECUCAO_EM_ANDAMENTO`: HTTP 409;
- `EXECUCAO_NAO_ENCONTRADA`: HTTP 404;
- `BANCO_INDISPONIVEL`: HTTP 503 nas consultas síncronas.
