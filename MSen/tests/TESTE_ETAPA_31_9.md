# Evidência da etapa 31.9 — Gradiente das dezenas

Data: 12/11/2026

## Escopo verificado

- uma única marca por dezena, independentemente da quantidade de concursos;
- intensidade visual proporcional à frequência histórica;
- cor, opacidade e tamanho variáveis;
- controle independente para ocultar ou exibir ocorrências;
- combinação das ocorrências com Média espacial, CG1, CG2 e Quadrantes;
- desempenho com aproximadamente 3.000 resultados;
- importação, desenho e limpeza no navegador.

## Resultados

1. `node --test frontend/tests/painel_navegacao.test.mjs`
   - 28 testes aprovados.
2. `npm run test:frontend`
   - 129 testes aprovados.
3. `npx playwright test frontend/tests/browser/fluxos_principais.spec.mjs --grep "seleciona Excel, importa, desenha mancha e limpa"`
   - 1 fluxo Chromium aprovado.

## Persistência

A etapa alterou somente HTML, CSS, JavaScript e testes do frontend. Nenhuma API,
tabela ou linha do banco de dados foi modificada.
