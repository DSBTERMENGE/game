# Teste da subetapa 22.7 — API da frequência das dezenas

Data: 2026-10-30.

## Contratos implementados

- `GET /api/frequencias/estado`: configuração e geração ativas, resumo da base
  e eventual execução em andamento.
- `GET /api/frequencias/fotografia-atual`: fotografia das 60 dezenas no último
  concurso da geração ativa.
- `GET /api/frequencias/serie`: uma dezena, um tipo de evento e um período por
  requisição, limitado a 5.000 concursos.
- `POST /api/frequencias/previa`: diagnóstico sem gravação.
- `POST /api/frequencias/execucoes`: inicia simulação ou gravação confirmada.
- `GET /api/frequencias/execucoes/<id>`: estado, progresso e resultado.
- `POST /api/frequencias/execucoes/<id>/cancelamento`: solicita cancelamento
  cooperativo.

A configuração deve conter exatamente os campos funcionais do contrato. Campos
desconhecidos, ausentes ou valores inválidos são recusados. Uma operação com
`salvar_dados=true` exige `confirmacao_gravacao=true` antes da criação da tarefa.
Somente uma execução pode permanecer ativa.

Os valores decimais são serializados como texto para não perder precisão. A
série histórica não duplica as seis dezenas armazenadas em `resultados`.
Indisponibilidade do banco nas consultas síncronas produz resposta JSON com HTTP
503.

## PostgreSQL efêmero

```text
python -m tests.validar_api_frequencias
```

Foram inseridos cinco resultados em banco temporário e confirmados:

- geração ativa até o concurso 5;
- fotografia atual com exatamente 60 dezenas;
- série simples da dezena 10 nos concursos 3, 4 e 5;
- ausência de cópia das dezenas dos resultados nos pontos da série.

O database temporário foi removido e o `games` não foi alterado.

## Regressão

- Python: **626 testes aprovados**.
- JavaScript: **42 testes aprovados**.

Permaneceram somente avisos preexistentes de arquivos abertos em testes do
Screener. Item de menu, página e gráficos continuam fora desta subetapa.
