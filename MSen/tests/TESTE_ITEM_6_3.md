# Teste do Item 6.3

Data: 2026-10-26

## Resultado

- 5 testes específicos do voo aprovados;
- 15 testes de frontend acumulados aprovados;
- 137 testes Python de regressão aprovados;
- nenhum banco alterado e nenhum acesso ao PythonAnywhere.

## Casos confirmados com relógio controlado

- intervalo padrão de 0,5 segundo agenda exatamente 500 ms;
- resultados avançam em ordem e continuam circularmente;
- pausa remove o temporizador ativo sem deixar tarefa órfã;
- mudança de 0,5 para 1,2 segundo passa a valer no passo seguinte;
- valores abaixo de 0,1, acima de 30 e não numéricos não iniciam o voo;
- redimensionamento redesenha a posição atual sem cancelar ou duplicar o
  temporizador;
- textos do botão e mensagens de início, pausa e erro permanecem coerentes.

## Execução

```text
node --test frontend/tests/painel_navegacao.test.mjs
```

O relógio falso executa cada callback sob controle do teste, sem esperas reais.
