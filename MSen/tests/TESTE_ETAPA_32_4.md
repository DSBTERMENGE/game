# Evidência — Etapa 32.4

Data: 14/11/2026

## Objetivo

Calcular a escala dinâmica e o lado dos quatro quadrados a partir da contagem
histórica e das dimensões reais do painel, sem desenhar elementos.

## Regra implementada

1. Descontar da distância entre a origem e cada borda o afastamento definido na
   etapa 32.3.
2. Adotar a menor das extensões esquerda, direita, superior e inferior.
3. Calcular `referência = total de ocorrências ÷ 4`.
4. Calcular `passo = menor extensão ÷ referência ÷ 2`.
5. Calcular `lado = quantidade do quadrante × passo`.

Entradas inválidas, ausência de espaço e quantidades negativas são recusadas.

## Conferência no Painel real

Com 3.069 concursos e 18.414 ocorrências:

- extensões horizontais: 296,5 px para cada lado;
- extensões verticais: 175,59375 px para cada lado;
- extensão adotada: 175,59375 px;
- referência: 4.603,5 ocorrências;
- passo: 0,0190717660475725 px por ocorrência;
- Q1: 4.608 ocorrências e lado de 87,88269794721407 px;
- Q2: 4.518 ocorrências e lado de 86,16623900293254 px;
- Q3: 4.718 ocorrências e lado de 89,98059221244705 px;
- Q4: 4.570 ocorrências e lado de 87,15797083740632 px.

## Testes

- 8 testes matemáticos do módulo de quadrantes aprovados;
- 36 testes direcionados aprovados;
- 153 testes do frontend aprovados;
- cálculo no servidor real aprovado.

Nenhum elemento visual foi acrescentado e nenhum dado foi persistido.
