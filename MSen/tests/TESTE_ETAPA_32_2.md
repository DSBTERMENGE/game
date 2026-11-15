# Evidência — etapa 32.2

Data: 14/11/2026

## Implementação

Foi criado o módulo isolado `frontend/js/quadrantes-painel.js` com:

- `classificarDezenaNoQuadrante`, para dezenas de 1 a 60;
- `contarQuadrantes`, para percorrer integralmente os resultados;
- validação de seis dezenas distintas por concurso;
- suporte ao vetor `dezenas` e aos campos `res_01` a `res_06`;
- retorno de concursos, total, referência média, quantidades e percentuais.

O módulo não está importado pelo Painel, não desenha elementos e não grava
dados.

## Testes

```text
node --test frontend/tests/quadrantes_painel.test.mjs
```

Resultado: 4 testes aprovados, 0 falhas.

```text
npm run test:frontend
```

Resultado: 149 testes aprovados, 0 falhas.

## Conferência com o histórico real

A função foi executada diretamente sobre os 3.069 resultados da API real e
retornou:

- total: 18.414;
- referência média: 4.603,5;
- Q1: 4.608 — 25,0244379277%;
- Q2: 4.518 — 24,5356793744%;
- Q3: 4.718 — 25,6218094928%;
- Q4: 4.570 — 24,8180732052%.

Os valores reproduzem a conferência independente da etapa 32.1.
