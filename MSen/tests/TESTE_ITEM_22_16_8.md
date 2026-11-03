# Teste do item 22.16.8 — Cobertura histórica integral do backtest

Data: 2026-10-31

## Regra

- A faixa somente é avaliada quando seu limite superior está coberto pelo
  último concurso armazenado.
- A primeira faixa incompleta encerra a dezena.
- Pontos posteriores não são retomados.
- Retorno dentro da faixa é acerto; antes, depois ou ausência dentro de uma
  faixa já observável é erro.

## Verificações

- 16 testes unitários da API aprovados.
- Teste específico confirmou encerramento na primeira faixa incompleta.
- Teste específico confirmou erro de faixa completamente observada sem retorno.
- Validador PostgreSQL de estado, fotografias e séries aprovado.
- Servidor reiniciado com uma única instância na porta 5050, PID 24932.

## Caso real — dezena 17, evento simples

- Histórico solicitado: concursos 500–3.069.
- Intervalo efetivamente avaliado: 500–3.053.
- Concursos avaliados: 2.554.
- Acertos: 1.697.
- Erros: 857.
- Percentual de acerto: 66,44%.
- Primeira faixa aguardando histórico: corte 3.054, limite superior 3.073.
- Último concurso disponível: 3.069.
