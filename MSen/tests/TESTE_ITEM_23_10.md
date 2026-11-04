# Evidência da subetapa 23.10 — Página Seleção de dezenas

## Resultado

A página `frontend/selecao-dezenas.html` foi criada e ligada à navegação comum.
Ela utiliza a API `/api/selecao-dezenas` no mesmo servidor já existente, sem
abrir nova porta.

## Blocos entregues

- configuração da pesquisa com `k`, `j`, modo e quantidade de dezenas,
  horizonte e versão do cálculo;
- prévia sem iniciar processamento;
- previsões futuras preservadas, com parâmetros e indicação explícita de
  resultado ainda pendente;
- backtest com classes exclusivas de zero a seis acertos;
- período efetivamente avaliado, quantidade de concursos e faixa de tamanho
  dos conjuntos candidatos;
- comparação de pesquisas persistidas;
- detalhe por concurso;
- prévia e formação autorizada dos jogos de seis dezenas;
- ajuda modal inicial da página.

## Navegador automatizado

O ensaio `frontend/tests/browser/selecao_dezenas.spec.mjs` aprovou **2 testes**:

1. previsão futura com dezenas, quantidade, parâmetros e o rótulo
   “Aguardando resultado”;
2. consolidação do período, tamanho dos conjuntos, sete classes exclusivas e
   detalhe do backtest.

## Regressão

- frontend: **86 testes aprovados**;
- backend Python: **674 testes aprovados**;
- falhas: **0**.

## Observação operacional

Nenhum commit ou push faz parte desta subetapa. Nenhum servidor foi iniciado ou
reiniciado e nenhuma porta adicional foi criada.
