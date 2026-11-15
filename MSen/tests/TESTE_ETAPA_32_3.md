# Evidência — Etapa 32.3

Data: 14/11/2026

## Objetivo

Desenhar os dois eixos ortogonais dos quadrantes com base nas bordas reais das
células do painel, de uma borda à outra, e calcular o afastamento que será usado
posteriormente pelos quadrados.

## Resultado

- origem vertical localizada entre as dezenas 05 e 06;
- origem horizontal localizada entre as dezenas 21 e 31;
- espessura obtida do intervalo real entre as células, com mínimo de 1 px;
- afastamento calculado como metade da espessura mais 2 px;
- dois retângulos SVG verdes, um vertical e um horizontal;
- exibição condicionada ao marcador Quadrantes durante o desenho da mancha;
- remoção correta ao limpar o gráfico ou exibir um concurso;
- realinhamento pelo redesenho depois de redimensionar a página.

## Verificações

- 6 testes matemáticos do módulo de quadrantes aprovados;
- 34 testes direcionados do Painel e dos quadrantes aprovados;
- 151 testes do frontend aprovados;
- inspeção automatizada no servidor real `127.0.0.1:5050` aprovada;
- inspeção visual confirmou as linhas nos intervalos corretos e atravessando
  toda a largura e toda a altura do painel das dezenas.

Nenhum quadrado foi desenhado nesta etapa e nenhum dado foi persistido.
