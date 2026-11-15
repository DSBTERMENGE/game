# Evidência — Etapa 32.7

Data: 14/11/2026

## Objetivo

Integrar a visualização dos quadrantes ao controle do Painel, permitir sua
sobreposição com as demais manchas e apresentar Q1 a Q4 no resumo lateral.

## Resultado

- o marcador Quadrantes controla os dois eixos, quatro quadrados, oito textos e
  o resumo correspondente;
- Quadrantes pode ser exibido simultaneamente com Dezenas, Média espacial, CG1
  e CG2;
- os resumos das camadas marcadas são concatenados, sem substituição;
- Q1 a Q4 exibem quantidade, percentual e posição classificatória;
- ao desmarcar Quadrantes e redesenhar, somente seus elementos e seu resumo
  desaparecem.

## Integração real

Com todas as camadas marcadas foram conferidos:

- 4 quadrados, 2 eixos e 8 textos dos quadrantes;
- 18.414 marcas de ocorrências das dezenas;
- 3.069 pontos da Média espacial;
- 3.069 pontos do CG1;
- 3.069 pontos do CG2;
- os quatro blocos de informação no resumo lateral.

Depois de desmarcar Quadrantes, seus elementos chegaram a zero e as três
manchas de médias permaneceram desenhadas.

## Testes

- 38 testes direcionados aprovados;
- 155 testes do frontend aprovados;
- teste de integração no servidor real aprovado.

Nenhum dado foi persistido.
