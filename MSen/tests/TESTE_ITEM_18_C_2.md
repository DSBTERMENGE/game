# Teste da subetapa 18-C.2 — migração dos percentuais

Data: 29/10/2026.

## Alteração estrutural

A migração `009_adicionar_percentual_ocorrencia_padroes.sql` adicionou à única
linha atual de cada padrão:

- `total_sorteios INTEGER`;
- `percentual_ocorrencia NUMERIC(9,6)`.

O campo físico `num_oco` foi preservado nesta subetapa. Renomeá-lo isoladamente
quebraria repositório, API, frontend e testes antes da adaptação coordenada. Ele
continua representando a quantidade de ocorrências.

Não foi criada tabela histórica nem outra linha por padrão.

## Integridade

As restrições exigem:

- denominador positivo quando preenchido;
- percentual entre 0% e 100%;
- quantidade menor ou igual ao denominador;
- percentual igual a `ROUND(num_oco * 100 / total_sorteios, 6)`;
- durante a transição, denominador e percentual podem permanecer ambos nulos.

## Testes

- 13 testes específicos de DDL e executor: aprovados;
- banco PostgreSQL temporário com migrações `001` a `009`: aprovado e removido;
- quantidade 0, total 3.069 e percentual 0%: aceito;
- 1 ocorrência em 3 sorteios e percentual 33,333333%: aceito;
- 1 ocorrência em 3 sorteios e percentual 40%: rejeitado pelo banco;
- regressão Python completa: **492 testes aprovados**.

## Banco local `games`

- migração `009` aplicada;
- nove padrões preservados;
- `total_sorteios` e `percentual_ocorrencia` ainda nulos nos nove padrões;
- `num_oco` e demais estatísticas anteriores preservados;
- as 1.780 linhas `SEM_CORRESPONDENCIA` permanecem intactas, pois sua remoção
  pertence à subetapa 18-C.4.

Os novos campos serão preenchidos pelo recálculo autorizado na 18-C.3.
