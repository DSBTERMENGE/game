# Evidência — subetapa 22.16.11.4

Data: 2026-11-02

## Alteração validada

- Patamares projetados com menos de 8 pixels recebem marcador em losango com
  haste tracejada.
- O marcador não amplia nem desloca as coordenadas reais do intervalo.
- Mouse, foco pelo teclado e clique mostram `concurso anterior → concurso
  seguinte · intervalo N`.
- Patamares com largura igual ou superior ao limite não recebem o marcador
  auxiliar.

## Testes

```text
npm run test:frontend
59 testes aprovados

npm run test:browser
34 testes aprovados no Chrome
```
