# Teste da subetapa 22.13 — Ajuda de Frequência das dezenas

Data: 2026-10-30

## Entrega validada

- botão `Ajuda` no topo de `frequencias.html`;
- diálogo acessível e rolável, independente das APIs;
- explicação dos sete blocos na ordem visual da página;
- finalidade do estudo, fluxo recomendado e cuidados operacionais;
- fechamento por cabeçalho, rodapé, tecla `Esc` e clique fora;
- adaptação da lista descritiva para telas estreitas.

## Testes executados

```powershell
node --test frontend/tests/frequencias_pagina.test.mjs
npx playwright test frontend/tests/browser/frequencias.spec.mjs
```

Resultados:

- 4 testes unitários aprovados;
- 4 fluxos no Google Chrome aprovados;
- modal aberto, conteúdo conferido e fechamento validado;
- página utilizável em 1280 px e 520 px.

Nenhum dado do PostgreSQL foi alterado por estes testes.
