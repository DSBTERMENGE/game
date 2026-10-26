# Teste do Item 5.2 — `GET /api/resultados`

Data: 2026-10-26.

## Testes automatizados

- seis testes específicos aprovados;
- 121 testes acumulados aprovados;
- banco vazio retorna lista vazia e total zero;
- resultado válido segue o contrato do frontend;
- datas usam `AAAA-MM-DD`;
- decimais preservam precisão como texto;
- resultados são ordenados por `numero_ap` crescente;
- erro do banco retorna HTTP 503 sem revelar a credencial;
- resposta usa `application/json`.

## Integração local real

A rota foi chamada com o cliente Flask contra o PostgreSQL local `games`:

- HTTP 200;
- total: 3.069;
- primeiro: concurso 1, data 1996-03-11;
- último: concurso 3069, data 2026-10-11;
- ordem estritamente crescente;
- contagem antes e depois: 3.069.

Também foi iniciado temporariamente o servidor de desenvolvimento em
`127.0.0.1:5052`. Requisições HTTP reais a `/api/saude` e `/api/resultados`
retornaram `ok` e 3.069 resultados. O servidor foi encerrado após o teste.

Nenhum dado foi inserido, atualizado ou excluído.
