# API — Frequência das dezenas

As páginas `frequencias.html` e `graficos-frequencias.html` consomem as mesmas
rotas. A página auxiliar reutiliza `GET /api/frequencias/serie`; escalas X/Y,
marcações de centenas, degraus e retorno são operações exclusivamente visuais
e não criam novos parâmetros nem persistência.

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

`intervalos_individuais` relaciona ocorrências consecutivas cujo segmento
intercepta o período consultado. Isso inclui o intervalo que atravessa o limite
inicial e, quando já concluído no histórico, o que atravessa o limite final.
Cada item contém `concurso_anterior`, `numero_do_concurso`, `intervalo`,
`concurso_inicial_visivel` e `concurso_final_visivel`. Os dois últimos campos
são o recorte para desenho; os concursos reais permanecem inalterados. Nenhum
retorno futuro é inventado e nenhuma nova estatística é persistida.

Os campos históricos `media_intervalos` e `desvio_padrao_intervalos` são
acumulados desde o primeiro intervalo efetivamente formado entre duas
ocorrências. Não existe intervalo artificial a partir do concurso zero. O
recorte visual de `intervalos_individuais` não modifica esses campos.

`assertividade` avalia cada fotografia somente quando o limite superior da
faixa está coberto pelo histórico disponível. Os limites são inclusivos. Ao
encontrar a primeira faixa que ultrapassa o último concurso armazenado, o
backtest encerra aquela dezena; pontos posteriores não são avaliados. A resposta
informa `intervalo_backtest` e `aguardando_historico`. Faixa observável com
retorno dentro dos limites é acerto; retorno anterior, posterior ou ausência de
retorno dentro da faixa é erro.

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
lista campo, valor gravado e valor calculado. A resposta também inclui:

- `concurso_inicial` e `concurso_final`: período abrangido pela operação;
- `quantidade_concursos`: cortes que efetivamente serão calculados;
- `linhas_estimadas`: fotografias previstas para dezenas e tipos de evento;
- `motivo`: explicação da decisão;
- `salvar_dados`, `exige_confirmacao` e `substitui_geracao`: efeitos da operação.

A prévia é somente leitura: não cria tarefa e não grava histórico.

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
