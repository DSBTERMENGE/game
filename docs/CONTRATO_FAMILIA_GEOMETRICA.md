# Contrato da família geométrica

A família geométrica inicial possui cinco filtros ordenados:

1. extensão aberta;
2. perímetro fechado;
3. área total das regiões;
4. quantidade de regiões;
5. centro de gravidade, avaliando X e Y em uma única decisão.

Uma combinação é analisada uma vez pelas funções geométricas oficiais. O
resultado compartilhado alimenta todos os filtros alcançados pelo funil. Cada
faixa é fechada, portanto seus limites são aceitos.

Se um filtro excluir, os filtros seguintes não avaliam aquela combinação. As
exclusões do subtotal geométrico são, assim, líquidas e atribuídas somente ao
primeiro filtro decisivo.

## Centro de gravidade ausente

Uma figura sem área positiva não possui centro de gravidade. Esse caso nunca é
decidido silenciosamente: `politica_centro_ausente` deve ser `aprovar` ou
`excluir`. A política escolhida precisa integrar a fotografia da execução quando
a família for ligada ao screener completo.
