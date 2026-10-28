# Teste do Item 16.2 — DDL da classificação por grupos

Data: 28/10/2026

## Escopo

Foi criada a migração `008_criar_classificacao_resultado_padrao.sql` e o
esquema PostgreSQL consolidado foi atualizado. A migração não foi aplicada ao
database local principal `games`.

## Estrutura preparada

- uma classificação por `id_resultado` e `id_grupo`;
- referência obrigatória ao resultado e ao grupo;
- referência opcional ao padrão, validando que ele pertence ao mesmo grupo;
- estados permitidos: `PADRAO_IDENTIFICADO` e `SEM_CORRESPONDENCIA`;
- padrão obrigatório no primeiro estado e proibido no segundo;
- versão e data do cálculo;
- índice para contagens por grupo e padrão.

## Validação executada

Com `PYTHONPATH=src`:

```text
python -m unittest tests.test_migracao_classificacao_padrao_ddl tests.test_migrations -v
Ran 13 tests
OK
```

Os testes confirmaram a descoberta da versão `008` após a `007`, os elementos
essenciais do DDL, as três relações, a coerência dos estados e a equivalência
estrutural do esquema consolidado.

A regressão completa executou 384 testes Python em seguida, todos aprovados.
Foram emitidos apenas avisos já existentes de arquivos não fechados nos testes
do frontend do screener; eles não causaram falha.

## Limite desta subetapa

Esta foi uma validação estática e isolada. A execução real, as restrições em
PostgreSQL, a segunda execução pelo controlador de migrações e o rollback serão
testados em database temporário somente na subetapa 16.3.
