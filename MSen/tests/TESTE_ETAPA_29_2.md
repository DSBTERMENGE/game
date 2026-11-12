# Evidência — Etapa 29.2

Data: 11/11/2026

## Escopo autorizado

- organizar visualmente os dois comandos;
- explicar a finalidade de teste e aplicação;
- esclarecer o limite de raridade;
- melhorar mensagens sem alterar o motor do Screener.

## Resultado

- Teste e Aplicação possuem blocos próprios e informam seus limites;
- a aplicação continua explicitamente indisponível;
- o limite de raridade explica seu efeito sobre padrões históricos;
- estados iniciais, andamento e conclusão usam linguagem operacional;
- o layout se adapta a telas estreitas.

## Validação

- `npm run test:frontend`: 114 testes aprovados;
- `npx playwright test frontend/tests/browser/screener_extensivel.spec.mjs frontend/tests/browser/screener_real.spec.mjs`: 6 testes aprovados.

Motor, API, banco, processamento integral, commit e push não foram alterados ou
executados.
