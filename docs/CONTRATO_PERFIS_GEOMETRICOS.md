# Contrato dos perfis geométricos

O serviço recebe linhas de `analise_geometrica_resultado` representadas por
`AnaliseGeometricaPersistida` e aplica o perfil estatístico genérico a:

1. extensão aberta;
2. perímetro fechado;
3. quantidade de regiões;
4. área total;
5. centro de gravidade X;
6. centro de gravidade Y.

Cada parâmetro informa quantidade total de análises, quantidade com valor e
quantidade ausente. Centro X e centro Y são tratados como parâmetros separados.

## Ausência não é zero

Uma figura sem área tem quantidade de regiões e área iguais a zero, que são
valores matemáticos válidos e participam dos respectivos perfis. Ela não possui
centro de gravidade de área: X e Y ficam nulos, contam como ausentes e não
participam da média nem do desvio das coordenadas.

Se nenhuma linha possuir determinada coordenada, seu perfil estatístico será
nulo e a ausência será informada. O sistema não inventará média zero.

## Integridade

- um `id_resultado` não pode aparecer duas vezes;
- X e Y devem existir ou faltar juntos;
- área zero exige centro ausente e área positiva exige centro presente;
- uma coleção vazia produz perfis vazios com contagens zero;
- esta subetapa apenas calcula perfis em memória: não grava no banco e não
  ativa exclusões no screener.
