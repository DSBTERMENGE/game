# Teste da subetapa 22.17.5-B.1

Data: 02/11/2026

## Implementação

O gráfico **Ocorrências em ordem crescente** passou a apresentar:

- eixo X fixo de 0% a 100%;
- eixo Y fixo de 0% a 100%;
- 21 marcas em cada eixo: 0%, 5%, 10%, …, 100%;
- linhas finas verticais e horizontais formando a grade de referência;
- pontos calculados por `X(i) = i/N × 100`;
- pontos calculados por
  `Y(i) = intervalo(i)/maior_intervalo × 100`;
- ordenação crescente e repetições preservadas;
- coordenadas sem arredondamento ou encaixe na grade.

Os títulos agora são:

- `Ocorrências ordenadas do menor para o maior (%)`;
- `Duração do intervalo (% do maior)`.

O detalhe interativo informa a ordem e o total de ocorrências, o percentual
horizontal, a duração real em concursos e o percentual do maior intervalo.

## Testes

```text
npm run test:frontend
tests 75
pass 75
fail 0
```

Foram confirmadas a grade completa, as coordenadas percentuais, a preservação
de repetições, o último ponto em `(100%,100%)`, a ausência de `NaN` e o estado
vazio.

## Resultado

Subetapa 22.17.5-B.1 concluída. A validação visual no Chrome, as amostras de
20, 14 e 17 pontos e os dados reais ficam reservados à subetapa 22.17.5-B.2.
