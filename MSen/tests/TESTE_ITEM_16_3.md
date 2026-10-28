# Teste do Item 16.3 — migração 008 em PostgreSQL temporário

Data: 28/10/2026

## Escopo protegido

O ensaio utilizou exclusivamente o database efêmero
`games_test_7_1_163`. O database principal `games` e o PythonAnywhere não foram
alterados.

## Sequência executada

1. Criação do database temporário vazio.
2. Aplicação das migrações `001` a `007`, simulando a estrutura anterior.
3. Aplicação normal das migrações atuais: somente a `008` ficou pendente.
4. Segunda execução do controlador: versões `001` a `008` reconhecidas como já
   aplicadas, sem nova alteração.
5. Gravação dos dois estados válidos.
6. Tentativas controladas de violar as restrições.
7. Execução de uma migração `009` propositalmente defeituosa.
8. Confirmação do rollback e remoção do database temporário.

## Resultado

- `PADRAO_IDENTIFICADO` com padrão do próprio grupo: aceito;
- `SEM_CORRESPONDENCIA` sem padrão: aceito;
- duplicidade do par resultado/grupo: rejeitada;
- `PADRAO_IDENTIFICADO` sem padrão: rejeitado;
- `SEM_CORRESPONDENCIA` com padrão: rejeitado;
- padrão pertencente a outro grupo: rejeitado;
- versão de cálculo igual a zero: rejeitada;
- exclusão do resultado removeu suas classificações em cascata;
- a migração defeituosa não deixou tabela nem registro da versão `009`.

Saída resumida do ensaio:

```text
aplicadas_primeira_execucao: [008]
ja_aplicadas_segunda_execucao: [001, 002, 003, 004, 005, 006, 007, 008]
restricoes_rejeitadas: 5
rollback: tabela_e_versao_009_ausentes
```

Após o bloco de limpeza, a listagem de databases `games_test_7_1_%` retornou
`[]`, confirmando que nenhum database temporário permaneceu.
