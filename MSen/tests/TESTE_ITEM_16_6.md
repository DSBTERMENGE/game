# Teste do Item 16.6 — recálculo histórico do grupo piloto

Data: 28/10/2026

## Serviço implementado

`recalcular_classificacoes_grupo_sequenciais` executa em uma única transação:

1. resolve `PG_001` e `PD_001`–`PD_003` pelos códigos estáveis;
2. lê todos os resultados em páginas de até 10.000 e em ordem de concurso;
3. chama o classificador aprovado na subetapa 16.5;
4. grava uma classificação por resultado/grupo;
5. devolve um relatório imutável com as quatro contagens.

Uma nova execução atualiza as mesmas linhas. A versão do cálculo pode ser
elevada sem substituir `id_classificacao`.

## Subconjunto controlado

O database temporário `games_test_7_1_1661` recebeu quatro resultados, um de
cada classe. Uma função/gatilho temporário provocou uma falha na terceira
gravação. A transação foi revertida e a tabela permaneceu com zero linhas.

Depois da remoção do gatilho, o resultado foi:

```text
PD_001: 1
PD_002: 1
PD_003: 1
SEM_CORRESPONDENCIA: 1
```

Três execuções preservaram os mesmos quatro identificadores; a última elevou
todas as linhas para a versão 2.

## Histórico completo clonado

O backup do histórico real foi restaurado em `games_test_7_1_1662`, recebeu as
migrações atuais e foi classificado duas vezes:

```text
Resultados analisados: 3.069
PD_001: 1.192
PD_002: 92
PD_003: 5
SEM_CORRESPONDENCIA: 1.780
Total reconciliado: 3.069
```

A segunda execução preservou as 3.069 identidades persistidas. Os dois
databases temporários foram removidos e a auditoria final retornou `[]`.

## Regressão e proteção

Foram executados 400 testes Python, todos aprovados. Permaneceram apenas os
avisos já conhecidos dos testes do frontend do screener. O database principal
`games` não recebeu a migração nem as classificações; o PythonAnywhere também
permaneceu intocado.
