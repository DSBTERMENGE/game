# Evidência do Item 13.3 — interseções e regiões fechadas

Data: 2026-10-27.

Foi criado o módulo `msen.geometria.regioes`, com aritmética exata baseada em
`fractions.Fraction`. Ele:

- encontra cruzamentos internos, contatos e limites de sobreposição;
- não confunde junções consecutivas normais com cruzamentos;
- divide segmentos em trechos atômicos nos nós encontrados;
- normaliza trechos coincidentes sem duplicá-los;
- ordena direções sem ângulos de ponto flutuante;
- percorre a rede planar e retorna somente faces fechadas e limitadas;
- remove vértices colineares redundantes dos contornos.

Passaram 12 testes específicos cobrindo figura simples, um cruzamento com duas
regiões, vários cruzamentos com três regiões, figura colinear, sobreposição,
contato em vértice e três segmentos no mesmo nó. Uma varredura adicional de
5.000 combinações terminou sem erro. A regressão completa aprovou 239 testes
Python.

Área e centro de gravidade ainda não possuem funções públicas e serão tratados
somente no Item 13.4. O banco `games` e o PythonAnywhere não foram acessados.
