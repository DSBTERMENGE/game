# Teste da subetapa 23.4 — migração e repositório de pesquisas

Data: 03/11/2026.

## Escopo concluído

- migração 021 com configurações, execuções, alvos e avaliações das 60
  dezenas;
- configuração tipada, validada e identificada por assinatura SHA-256;
- persistência transacional e idempotente;
- proteção de configurações usadas contra alteração retroativa;
- referência a `resultados` por `id_resultado`, sem copiar as seis dezenas;
- cascata somente de execução para alvos e de alvo para avaliações;
- índices de configuração, execução, situação, ranking e histórico.

## Testes unitários e estruturais

Executado:

```text
python -m unittest tests.test_configuracao_selecao_dezenas \
  tests.test_migracao_pesquisa_selecao_ddl \
  tests.test_repositorio_pesquisa_selecao tests.test_migrations -v
```

Resultado: **19 testes aprovados**.

## PostgreSQL efêmero

Executado:

```text
python -m tests.validar_repositorio_pesquisa_selecao
```

O ensaio criou um database temporário, aplicou todas as migrações, gravou a
mesma configuração duas vezes sem duplicá-la e repetiu a gravação de um alvo
sem duplicar suas 60 avaliações. O database temporário foi removido ao final.

## Banco local

O executor aplicou somente a migração `021` no banco local `games` e informou
as migrações `001` a `020` como já aplicadas.

## Regressão

Executado:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **644 testes aprovados**. Permaneceram apenas três avisos
preexistentes de arquivos do Screener abertos durante testes.
