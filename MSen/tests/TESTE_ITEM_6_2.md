# Teste do Item 6.2

Data: 2026-10-26

## Resultado

- 5 testes geométricos específicos aprovados;
- 10 testes de frontend acumulados aprovados;
- 137 testes Python de regressão aprovados;
- nenhuma alteração de banco ou acesso ao PythonAnywhere.

## Casos confirmados

- exatamente seis círculos de resultado e um círculo de média;
- centros de `01 = (0; 0)`, `10 = (9; 0)`, `51 = (0; 5)` e
  `60 = (9; 5)` convertidos corretamente para pixels;
- média inteira `(1; 1)` posicionada exatamente no centro correspondente;
- média decimal `(2; 4,333333...)` preservada sem arredondar a posição;
- apresentação textual da média decimal como `(2.00; 4.33)`;
- dezenas `01` e `60` continuam presentes e legíveis sob as marcas;
- camada SVG não captura eventos do mouse;
- marca de resultado usa opacidade de 0,5;
- redimensionamento de células de 40 para 50 pixels recalcula a marca da média
  e atualiza a `viewBox` para `0 0 500 300`.

## Execução

```text
node --test frontend/tests/painel_navegacao.test.mjs
```

O teste usa DOM e dimensões controladas para verificar numericamente as
coordenadas, sem instalar bibliotecas JavaScript adicionais.
