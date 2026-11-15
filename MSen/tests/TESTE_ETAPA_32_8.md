# Evidência — Etapa 32.8

Data: 14/11/2026

## Escopo

Validação final da implementação dos quadrantes com o histórico completo,
incluindo desempenho, redimensionamento, isolamento e sobreposição.

## Dados conferidos

- 3.069 concursos;
- 18.414 ocorrências;
- Q1: 4.608, segunda posição, lado 87,88269794721407 px;
- Q2: 4.518, quarta posição, lado 86,16623900293254 px;
- Q3: 4.718, primeira posição, lado 89,98059221244705 px;
- Q4: 4.570, terceira posição, lado 87,15797083740632 px.

## Geometria e redimensionamento

Na janela inicial, a origem calculada e o centro dos eixos coincidiram em:

- x: 300,3828125 px;
- y: 179,4765625 px.

Depois da mudança da largura da janela de 1.280 para 700 px, a camada foi
redesenhada. Os centros dos eixos continuaram coincidindo com a origem e as
quantidades, posições e dimensões dos quatro quadrados permaneceram corretas.

## Desempenho observado

- Quadrantes isolado: aproximadamente 278 ms;
- Dezenas, Média espacial, CG1, CG2 e Quadrantes sobrepostos: aproximadamente
  639 ms.

Os dois tempos ficaram abaixo do limite de segurança de 15 segundos usado no
ensaio automatizado.

## Isolamento e sobreposição

Com todas as camadas marcadas foram encontrados 4 quadrados, 2 eixos, 8 textos,
18.414 marcas de dezenas e 3.069 pontos para cada uma das três médias. Depois de
desmarcar Quadrantes, somente seus quadrados, eixos, textos e resumo foram
removidos; as demais manchas permaneceram.

## Resultado

- teste real integral aprovado;
- 155 testes do frontend aprovados;
- nenhum defeito encontrado;
- nenhum dado persistido.
