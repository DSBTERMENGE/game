# Teste da subetapa 29.4.3 — validação integrada do Screener

Data: 11/11/2026

## Banco local

A liberação controlada confirmou 3.069 resultados e alterou o estado global
para `TODAS_AS_CONDICOES_CONFIRMADAS`. Os critérios e perfis permaneceram
coerentes com esse mesmo conjunto de resultados.

## Motor real

- combinações analisadas: 5.000;
- combinações excluídas: 4.586;
- combinações aprovadas: 414;
- fechamento reconciliado: sim;
- duração observada: 4,343 segundos.

O endpoint assíncrono respondeu HTTP 202, alcançou `CONCLUIDA`, informou 100%
e devolveu os mesmos totais, sem erro.

## Navegador

```powershell
npx playwright test frontend/tests/browser/screener_extensivel.spec.mjs frontend/tests/browser/screener_real.spec.mjs
```

Resultado: 7 testes Chromium aprovados, cobrindo confirmação, progresso,
conclusão, falha controlada, trava de validação e cancelamento com descarte do
resultado parcial.

## Limites preservados

A Aplicação do Screener sobre 50.063.860 combinações permaneceu desabilitada.
Nenhuma alteração foi realizada no PythonAnywhere.
