# Teste da etapa 34.2 — Ajuda da página Distribuições

Data: 14/11/2026.

## Conteúdo conferido

A Ajuda de Distribuições passou a apresentar, em ordem operacional:

1. finalidade da página e relação dos dez perfis;
2. leitura das barras, curva de referência, média, faixa e limites;
3. diferença entre extremos observados e limites calculados;
4. resumo da janela histórica;
5. campos do formulário de configuração;
6. fórmulas e exemplos dos dois métodos;
7. funcionamento da prévia, salvamento, cancelamento e atualização;
8. ausência de alteração no PostgreSQL e de ativação do Screener.

## Exemplos protegidos pelos testes

- média 30, desvio 5 e margens 1/1: faixa de 25 a 35;
- média 30, desvio 5 e margens 0,5/1,5: faixa de 27,5 a 37,5;
- média 30 e percentuais 10%/20%: faixa de 27 a 36.

## Testes executados

- `node --test frontend/tests/ajuda.test.mjs frontend/tests/distribuicoes.test.mjs frontend/tests/configuracao_distribuicoes.test.mjs`
  — 20 testes aprovados.
- `npm run test:frontend` — 164 testes aprovados, nenhuma falha.

A etapa alterou somente o conteúdo da Ajuda e seus testes; não houve gravação
no banco de dados nem ativação do Screener.
