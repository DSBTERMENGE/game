# Teste da subetapa 20.1 — DDL das amostras de validação

Data: 29/10/2026

## Escopo

Criação exclusiva da estrutura `amostras_validacao`. Não foram criados catálogo
de critérios, avaliações, repositório, API, frontend ou carga dos 200 registros.
O database local persistente `games` e o PythonAnywhere não foram alterados.

## Arquivos

- `database/migrations/011_criar_amostras_validacao.sql`;
- `database/schema_postgresql.sql`;
- `database/README.md`;
- `MSen/tests/test_migracao_amostras_validacao_ddl.py`;
- `MSen/tests/validar_migracao_amostras_validacao.py`.

## Contrato estrutural validado

- `id_resultado BIGINT` é simultaneamente PK e FK para `resultados`;
- exclusão do resultado remove a amostra por `ON DELETE CASCADE`;
- `ordem SMALLINT` é obrigatória, positiva e única;
- `ativo` inicia como `TRUE`;
- `incluido_em` recebe o instante corrente;
- nenhuma coluna `res_01` a `res_06` foi duplicada;
- as dezenas são obtidas por `INNER JOIN` com `resultados`.

## PostgreSQL temporário

A migração foi ensaiada em database efêmero e o database foi removido ao final.

Resultados:

- migrações 001 a 010 aplicadas como estrutura anterior;
- migração 011 aplicada isoladamente na primeira execução;
- segunda execução não reaplicou nenhuma migração e reconheceu 001 a 011;
- PK duplicada rejeitada;
- ordem duplicada rejeitada;
- ordem zero rejeitada;
- FK inexistente rejeitada;
- leitura das seis dezenas por `INNER JOIN` confirmada;
- cascata da exclusão de `resultados` confirmada;
- auditoria final de databases temporários: `[]`.

## Regressão

Comando:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py'
```

Resultado: **508 testes aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.1 aprovada tecnicamente. A tabela permanece vazia; a carga dos 200
resultados pertence à subetapa 20.6. A subetapa 20.2, catálogo e avaliações,
permanece sem autorização.
