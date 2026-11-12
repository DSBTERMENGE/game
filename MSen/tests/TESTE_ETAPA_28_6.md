# Evidência — subetapa 28.6

Data: 11/11/2026

## Escopo

- integração dos acessos contextuais com a Ajuda central;
- links diretos para tópicos de páginas e gráficos;
- retorno seguro à página de origem;
- desativação dos antigos modais locais;
- nenhuma alteração em cálculos, banco ou regras de negócio.

## Validação

- `npm run test:frontend`: 116 testes aprovados;
- `npx playwright test frontend/tests/browser/ajuda.spec.mjs`: 2 testes Chromium aprovados.
