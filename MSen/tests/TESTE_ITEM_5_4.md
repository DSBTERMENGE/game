# Teste do Item 5.4

Data: 2026-10-26

## Resultado automatizado

- 9 testes específicos aprovados;
- 137 testes acumulados aprovados;
- inclusão válida retorna HTTP 201;
- edição válida retorna HTTP 200;
- data em ISO e em formato brasileiro aceita;
- vetor `dezenas` ou campos `res_01` a `res_06` aceitos;
- campos derivados enviados pelo cliente ignorados e recalculados;
- entrada inválida rejeitada antes da persistência;
- duplicidade e divergência entre URL e corpo retornam HTTP 409;
- edição inexistente retorna HTTP 404;
- falha de banco retorna mensagem segura.

## Homologação PostgreSQL local

Em uma transação controlada, o concurso 3070 foi incluído e depois editado:

- contagem inicial: 3.069;
- contagem durante a transação: 3.070;
- soma calculada na inclusão: 161;
- soma recalculada na edição: 162;
- média recalculada na edição: 27,000000.

A transação foi deliberadamente revertida. Depois do rollback, a contagem
voltou a 3.069, o concurso 3070 não existia e as 60 linhas de frequência estavam
exatamente iguais ao estado anterior.

O script temporário foi removido, o PythonAnywhere não foi acessado e nenhum
commit foi criado.
