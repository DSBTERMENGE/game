# Evidência da etapa 31.5 — Quadrantes

Data: 12/11/2026

## Regra implementada

A matriz de 60 dezenas foi dividida entre as colunas 05 e 06 e entre as linhas
21–30 e 31–40:

- Q1: região superior direita;
- Q2: região superior esquerda;
- Q3: região inferior esquerda;
- Q4: região inferior direita.

Cada resultado recebe quatro contagens na ordem Q1, Q2, Q3 e Q4. Assim, três
dezenas em Q1, nenhuma em Q2, duas em Q3 e uma em Q4 formam o código categórico
`3021`.

O resumo histórico conta a quantidade e o percentual de cada código. Média e
desvio-padrão populacional são calculados separadamente para Q1, Q2, Q3 e Q4;
o código completo não é tratado como número.

## Conferência do histórico atual

Consulta somente leitura dos 3.069 concursos:

| Quadrante | Média | Desvio-padrão | Mínimo | Máximo |
| --- | ---: | ---: | ---: | ---: |
| Q1 | 1,501466 | 0,983613 | 0 | 5 |
| Q2 | 1,472141 | 1,013893 | 0 | 5 |
| Q3 | 1,537309 | 1,007786 | 0 | 5 |
| Q4 | 1,489084 | 1,006153 | 0 | 6 |

Foram encontradas 80 categorias. A mais frequente foi `2112`, presente em 182
concursos, correspondendo a 5,930270% do histórico atual.

## Validação

- limites 05/06, 21/30 e 31/40 conferidos por testes;
- código `3021` conferido por caso explícito;
- resultado independente da ordem de entrada das dezenas;
- códigos tratados como categorias;
- médias e desvios calculados separadamente;
- entradas vazias, repetidas ou inválidas recusadas;
- nenhuma API, interface, tabela ou linha do banco foi alterada.

Esta etapa prepara os dados. A apresentação no Painel pertence às etapas de
organização e integração visual posteriores.
