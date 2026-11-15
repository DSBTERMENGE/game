# Evidência da subetapa 31.9.1 — Correção do gradiente das dezenas

Data: 12/11/2026

## Escopo verificado

- círculos de 2 mm, um para cada ocorrência histórica;
- distribuição das ocorrências em matriz 10 × 10;
- reutilização e sobreposição das posições após 100 ocorrências;
- tamanho fixo dos círculos;
- gradiente escuro para frequências próximas da média das 60 dezenas;
- gradiente claro para frequências distantes da média;
- opção `Dezenas` dentro do quadro `Manchas`;
- exibição isolada ou combinada das camadas;
- cores-base distintas para Dezenas, Média espacial, CG1, CG2 e Quadrantes.

## Resultados

1. `npm run test:frontend`
   - 129 testes aprovados.
2. `npx playwright test frontend/tests/browser/fluxos_principais.spec.mjs --grep "seleciona Excel, importa, desenha mancha e limpa"`
   - 1 fluxo Chromium aprovado.

## Persistência

A subetapa alterou somente HTML, JavaScript e testes do frontend, além desta
documentação. Nenhuma API, tabela ou linha do banco de dados foi modificada.
