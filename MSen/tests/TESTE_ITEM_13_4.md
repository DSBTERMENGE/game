# Evidência do Item 13.4 — área total e centro de gravidade

Data: 2026-10-27.

Foi criado o módulo `msen.geometria.medidas`. Os cálculos usam
`fractions.Fraction` e não arredondam valores durante a análise. O módulo:

- calcula a área positiva e o centroide de cada região;
- aceita contornos horários e anti-horários;
- trata contornos degenerados com área zero e centroide nulo;
- soma todas as áreas componentes sem cancelamentos;
- calcula um único centro de gravidade ponderado pelas áreas;
- executa o fluxo completo diretamente a partir das seis dezenas crescentes.

Os 10 testes específicos confirmaram os exemplos do contrato: área 36 e CG
`(4,125; 2,5)` para a figura simples; duas áreas de 2,25, área total 4,5 e CG
`(4,5; 0,5)` para a figura cruzada; e área zero com CG nulo para a figura
colinear. Também foram testados polígono côncavo, orientação inversa, ponderação
de áreas diferentes e invariância da ordem de entrada.

Uma varredura de 5.000 combinações confirmou áreas não negativas, coerência
entre área zero e CG nulo e centros dentro da matriz. A regressão completa
aprovou 249 testes Python. Nenhum banco foi acessado e nenhum arredondamento de
persistência foi definido antecipadamente.
