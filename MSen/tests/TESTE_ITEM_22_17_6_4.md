# Teste da subetapa 22.17.6.4

Data: 02/11/2026

## Conteúdo implementado

A ajuda contextual de **Ocorrências em ordem crescente** agora explica:

- finalidade da ordenação crescente com repetições;
- percentual acumulado no eixo horizontal;
- duração como percentual do maior intervalo no eixo vertical;
- quadriculado de referência de 5% em 5%;
- cálculo das duas coordenadas em linguagem simples;
- significado de cada ponto vermelho;
- espaçamento horizontal igual entre ocorrências;
- patamares produzidos por durações repetidas;
- saltos causados por durações intermediárias ausentes;
- último ponto em `(100%,100%)`;
- consulta por mouse, teclado ou clique;
- exemplo completo da ocorrência 32 de 253;
- limitações da interpretação histórica.

## Testes

Durante a primeira execução, uma verificação textual tratou incorretamente os
parênteses como expressão regular. O teste foi corrigido para comparar o texto
literal; nenhum conteúdo da ajuda ou cálculo do gráfico foi alterado.

```text
npm run test:frontend
tests 79
pass 79
fail 0
```

## Resultado

Subetapa 22.17.6.4 concluída. As três ajudas possuem conteúdo completo. A
validação funcional no Chrome e a liberação para análise do usuário pertencem
à subetapa 22.17.6.5.
