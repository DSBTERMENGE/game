# Teste da subetapa 22.17.3

Data: 02/11/2026

## Objetivo

Validar o gráfico **Ocorrências em ordem crescente** antes de sua integração ao
modal da página.

## Implementação verificada

- intervalos ordenados do menor para o maior, sem eliminar repetições;
- eixo X como percentual acumulado das ocorrências, de 0% a 100%;
- eixo Y como percentual do maior intervalo, de 0% a 100%;
- grade visual independente, dividida de 5% em 5%;
- pontos mantidos em suas posições percentuais exatas, sem encaixe na grade;
- inspeção dos pontos por mouse, teclado e clique;
- tratamento explícito de conjunto vazio.

## Arquivos principais

- `frontend/js/frequencia-grafico-ordenado.js`
- `frontend/css/graficos-frequencias.css`
- `frontend/tests/frequencia_grafico_ordenado.test.mjs`

## Testes executados

Comando:

```text
npm run test:frontend
```

Resultado final:

```text
tests 73
pass 73
fail 0
```

Durante a primeira execução, uma asserção estrita revelou somente a diferença
binária entre duas representações equivalentes de um terço. A verificação foi
corrigida para tolerância de `1e-12`; nenhuma fórmula ou coordenada do gráfico
foi alterada.

## Resultado

Subetapa 22.17.3 aprovada. A integração dos dois renderizadores ao único modal
reutilizável permanece reservada à subetapa 22.17.4.
