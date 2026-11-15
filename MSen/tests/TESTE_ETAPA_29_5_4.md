# Teste da subetapa 29.5.4 — comando integral da interface

Data: 11/11/2026

## Interface

- o botão `Iniciar aplicação` foi habilitado;
- a primeira confirmação informa 50.063.860 combinações e possível duração de
  várias horas;
- voltar da confirmação não inicia nenhuma requisição;
- a confirmação positiva envia `escopo=integral` e a confirmação técnica
  exigida pelo servidor;
- o andamento reutiliza progresso, duração e cancelamento confirmado;
- cancelamento e falha possuem mensagens específicas da aplicação integral.

## Testes

```powershell
npm run test:frontend
npx playwright test frontend/tests/browser/screener_extensivel.spec.mjs frontend/tests/browser/screener_real.spec.mjs
```

Resultados: 114 testes unitários do frontend e 7 testes Chromium aprovados.
Nenhuma execução das 50.063.860 combinações foi iniciada.
