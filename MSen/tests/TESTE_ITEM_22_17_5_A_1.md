# Teste da subetapa 22.17.5-A.1

Data: 02/11/2026

## Alteração realizada

O gráfico **Ocorrências em ordem crescente** passou a usar:

- eixo X: ordem dos intervalos, de 1 a N;
- eixo Y: duração do intervalo em concursos;
- ponto: `(posição ordinal, duração real)`;
- espaçamento horizontal uniforme entre posições consecutivas;
- ordenação crescente com repetições preservadas;
- percentuais somente no detalhe interativo de cada ponto.

Os títulos dos eixos agora são:

- `Ordem dos intervalos (menor para o maior)`;
- `Duração do intervalo (concursos)`.

## Testes automatizados

Foram conferidos:

- crescimento da posição X;
- crescimento visual da duração Y;
- associação direta entre ordem e intervalo;
- repetições em posições distintas e na mesma altura;
- primeiro ponto na posição 1 e último ponto na posição N;
- ausência de coordenadas inválidas;
- tratamento de conjunto vazio.

```text
npm run test:frontend
tests 74
pass 74
fail 0
```

## Resultado

Subetapa 22.17.5-A.1 concluída. A amostra exata `4, 1, 2, 2`, as dezenas reais
08, 10 e 17 e a regressão no Chrome permanecem reservadas à subetapa
22.17.5-A.2.
