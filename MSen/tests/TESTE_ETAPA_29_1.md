# Evidência — Etapa 29.1

Data: 11/11/2026

## Escopo autorizado

- adotar o nome `Preparação do Screener`;
- criar os comandos `Teste do Screener` e `Aplicação do Screener`;
- exigir confirmação anterior ao teste;
- manter a aplicação integral desabilitada;
- atualizar a Ajuda central afetada.

## Comportamento validado

- o teste não chama a API antes da confirmação positiva;
- cancelar a confirmação não inicia processamento;
- o teste continua usando a rota vigente das 5.000 combinações;
- a aplicação integral permanece desabilitada;
- página, menu e Ajuda usam a nomenclatura aprovada.

## Testes

- `npm run test:frontend`: 114 testes aprovados;
- `npx playwright test frontend/tests/browser/screener_extensivel.spec.mjs frontend/tests/browser/screener_real.spec.mjs`: 6 testes aprovados;
- `git diff --check`: nenhuma falha de espaço em branco.

Nenhuma migração, gravação no banco, execução integral, commit ou push foi
realizado.
