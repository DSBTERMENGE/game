# Teste do Item 16.4 — modelo e repositório de classificações

Data: 28/10/2026

## Implementação

- modelo imutável `ClassificacaoPadrao`;
- enumeração explícita `EstadoClassificacaoPadrao`;
- validação de identificadores, estado, versão e data com fuso horário;
- repositório `RepositorioClassificacoesPadrao`;
- salvamento por `INSERT ... ON CONFLICT`, preservando a identidade no
  recálculo;
- consultas ordenadas por resultado e por grupo;
- SQL de classificação restrito ao módulo do repositório.

Todas as funções e classes novas possuem descrição do seu propósito.

## Testes unitários

Foram executados oito testes direcionados. Eles confirmaram:

- mapeamento das sete colunas;
- imutabilidade do modelo;
- padrão obrigatório para `PADRAO_IDENTIFICADO`;
- padrão proibido para `SEM_CORRESPONDENCIA`;
- rejeição de estado textual não tipado;
- exigência de data com fuso horário;
- validação de identificadores e versão;
- exigência de conexão Psycopg real pelo repositório.

## Integração PostgreSQL

O database temporário `games_test_7_1_164` recebeu as migrações `001` a `008`.
O ensaio confirmou:

```text
insercao: confirmada
atualizacao_idempotente: confirmada
classificacoes_do_resultado: 2
classificacoes_do_grupo: 2
estado_sem_correspondencia: SEM_CORRESPONDENCIA
versao_atualizada: 2
```

O recálculo preservou `id_classificacao` e atualizou padrão e versão. O database
temporário foi removido; a auditoria final de remanescentes retornou `[]`.

## Regressão

Foram executados 392 testes Python, todos aprovados. Permaneceram somente os
avisos já conhecidos de arquivos do frontend do screener não fechados nos
próprios testes. O database principal `games` e o PythonAnywhere não foram
alterados.
