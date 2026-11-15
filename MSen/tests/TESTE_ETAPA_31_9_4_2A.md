# Evidência da subetapa 31.9.4.2A — Contrato matemático

Data: 14/11/2026

## Contrato

- centro: média das coordenadas históricas;
- distância à origem: `hipot(centro.x, centro.y)`;
- distância de cada ponto: Euclidiana até o centro;
- raios: 20%, 40% e 60% da distância máxima;
- faixas: 0–20%, acima de 20–40%, acima de 40–60% e acima de 60–100%;
- intensidade: fator mínimo visível, crescendo linearmente até duas vezes o
  fator no centro;
- nenhum arredondamento, agrupamento ou descarte de coordenadas.

## Histórico atual

- centro: `(4,497284674704; 2,501846421201)`;
- distância do centro à origem: `5,146338986173`;
- distância máxima: `3,678916009485`;
- raio de 20%: `0,735783201897`;
- raio de 40%: `1,471566403794`;
- raio de 60%: `2,207349605691`;
- concursos por faixa: 923, 1.306, 658 e 182.

## Validação

- cinco testes matemáticos específicos aprovados;
- 134 testes do frontend aprovados;
- módulo ainda não importado pela página;
- nenhum desenho, API, tabela ou linha do banco foi alterado.
