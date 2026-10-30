# Teste da subetapa 20.2 — catálogo e avaliações de validação

Data: 29/10/2026

## Escopo

Criação exclusiva do DDL de `criterios_validacao` e
`avaliacoes_validacao`. Não foram criados repositório, sincronização Python,
carga de critérios/amostras, API, frontend ou trava operacional no Screener.
O database local `games` e o PythonAnywhere não foram alterados.

## Arquivos

- `database/migrations/012_criar_catalogo_avaliacoes_validacao.sql`;
- `database/schema_postgresql.sql`;
- `database/README.md`;
- `MSen/tests/test_migracao_catalogo_avaliacoes_validacao_ddl.py`;
- `MSen/tests/validar_migracao_catalogo_avaliacoes_validacao.py`.

## Catálogo validado

- código estável e nome legível;
- categorias `ESTATISTICA`, `GEOMETRIA` e `PADRAO`;
- resultados `INTEIRO`, `DECIMAL` e `PADRAO`;
- precisão obrigatória somente para decimal;
- grupo obrigatório somente para classificador de padrões;
- assinatura SHA-256 obrigatória;
- estados `PENDENTE`, `APROVADO` e `REPROVADO`;
- exclusão do grupo remove seu critério por cascata.

## Avaliações validadas

- chave primária composta por amostra e critério;
- relações com amostra, critério, grupo e subgrupos esperado/calculado;
- valor esperado/calculado para critérios numéricos;
- estados `PADRAO_IDENTIFICADO` e `SEM_CORRESPONDENCIA` para classificadores;
- `NULL` em `aprovado` representa pendência, separado de `S` e `N`;
- referência conferida e execução são exigidas antes de `S/N`;
- assinatura e data são obrigatórias quando a função foi executada;
- subgrupo de outro grupo é rejeitado;
- exclusão da amostra ou critério remove suas avaliações por cascata.

## PostgreSQL temporário

A migração foi aplicada após 001 a 011 em database efêmero e repetida pelo
executor de migrações.

Resultados:

- somente a migração 012 foi aplicada na primeira execução;
- a segunda execução reconheceu 001 a 012 sem reaplicar nenhuma;
- avaliação numérica válida aprovada;
- avaliação de padrão válida aprovada;
- `SEM_CORRESPONDENCIA` válido e distinto de pendência;
- assinatura inválida rejeitada;
- combinação categoria/tipo inválida rejeitada;
- aprovação sem execução rejeitada;
- padrão pertencente a outro grupo rejeitado;
- cascatas de amostra e critério confirmadas;
- auditoria final de databases temporários: `[]`.

## Regressão

Resultado: **514 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.2 aprovada tecnicamente. As tabelas permanecem sem dados. A
migração ainda não foi aplicada ao `games`. A subetapa 20.3, aplicação
idempotente e controlada, permanece sem autorização.
