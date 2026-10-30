# API de Validação e auditoria

Estado vigente em 2026-10-30.

## Consultas

### `GET /api/validacao/quadro`

Retorna estado global, totais, filtros disponíveis e avaliações paginadas.
Aceita `categoria`, `criterio`, `grupo`, `subgrupo`, `situacao`, `pagina` e
`limite` de até 100.

### `GET /api/validacao/relatorio`

Retorna fechamento por função e detalhes dos registros `N`. O detalhe inclui
combinação, critério, grupo/subgrupo, esperado, calculado, diferença,
assinaturas e hipótese diagnóstica.

### `GET /api/validacao/exportacao?formato=json|csv`

Baixa a matriz ativa. O JSON é técnico e verificável por SHA-256; o CSV possui
BOM UTF-8 e neutraliza células interpretáveis como fórmulas.

## Atualização assíncrona

### `POST /api/validacao/execucoes`

Inicia uma única execução em segundo plano. Retorna `202` com identificador,
etapa, progresso e duração. Retorna conflito se outra execução estiver ativa.

### `GET /api/validacao/execucoes/<identificador>`

Consulta a tarefa. Estados terminais incluem resultado ou erro. O resultado
informa sincronização do catálogo, execuções e consolidação.

## Regra de segurança

A API não permite editar manualmente esperado, calculado ou aprovação pela
página. Referências e resultados são gravados pelos serviços Python validados.
