# Contrato dos padrões de dezenas na mesma coluna

Data de definição: 2026-10-27.

## 1. Matriz de referência

As 60 dezenas são organizadas em seis linhas e dez colunas:

```text
01 02 03 04 05 06 07 08 09 10
11 12 13 14 15 16 17 18 19 20
21 22 23 24 25 26 27 28 29 30
31 32 33 34 35 36 37 38 39 40
41 42 43 44 45 46 47 48 49 50
51 52 53 54 55 56 57 58 59 60
```

A coluna de uma dezena é calculada por `((dezena - 1) % 10) + 1`. Assim,
`05`, `15`, `25`, `35`, `45` e `55` pertencem à coluna 5; `10`, `20`, `30`,
`40`, `50` e `60` pertencem à coluna 10. O padrão exige também linhas
subjacentes: cada dezena da sequência vertical deve estar imediatamente abaixo
da anterior, portanto a diferença entre dezenas consecutivas deve ser `10`.
Dezenas na mesma coluna separadas por uma linha não formam sequência entre si.

## 2. Classificação exclusiva

O sistema localizará a maior sequência de linhas subjacentes em uma mesma
coluna. Cada resultado poderá pertencer a apenas um dos três padrões deste
grupo:

| Código | Regra |
|---|---|
| `PD_004` | a maior sequência vertical possui exatamente duas dezenas |
| `PD_005` | a maior sequência vertical possui exatamente três dezenas |
| `PD_006` | a maior sequência vertical possui quatro, cinco ou seis dezenas |

Um resultado classificado em `PD_005` ou `PD_006` não será também contado em
`PD_004`, embora contenha pares verticais. A regra acompanha a
classificação exclusiva já adotada para dezenas sequenciais.

Se houver dois ou mais grupos com o mesmo tamanho máximo, haverá somente uma
ocorrência do padrão naquele resultado. Por exemplo, um resultado com dois
pares em colunas diferentes conta uma vez em `PD_004`.

## 3. Casos de referência

| Resultado | Maior sequência vertical | Classificação |
|---|---:|---|
| `01, 12, 23, 34, 45, 56` | 1 | nenhum padrão do grupo |
| `10, 25, 38, 45, 51, 59` | 1 (`25` e `45` não são subjacentes) | nenhum padrão |
| `10, 25, 35, 48, 51, 59` | 2 (`25`, `35`) | somente `PD_004` |
| `05, 15, 22, 32, 48, 59` | 2 em duas colunas | somente `PD_004`, uma ocorrência |
| `07, 17, 27, 34, 45, 56` | 3 | somente `PD_005` |
| `05, 15, 25, 35, 48, 59` | 4 | somente `PD_006` |
| `10, 20, 30, 40, 50, 60` | 6 | somente `PD_006` |

A ordem em que as dezenas forem recebidas não mudará a classificação. As seis
dezenas deverão continuar diferentes, inteiras e contidas entre 1 e 60.

## 4. Estatísticas históricas

Cada concurso que atender ao detector contará como uma ocorrência, não importando
quantas colunas tenham sequência com o mesmo tamanho máximo. Os intervalos serão calculados
pela diferença entre os números dos concursos consecutivos classificados no
mesmo padrão. A média e o desvio-padrão populacional seguirão as funções
estatísticas já usadas pelos padrões sequenciais.

Com nenhuma ou uma ocorrência, `intervalo_medio` e `desv_padrao` permanecerão
nulos, pois ainda não existe intervalo observável.

## 5. Casos obrigatórios para os testes da implementação

- nenhuma sequência vertical;
- dezenas na mesma coluna, porém não subjacentes;
- exatamente duas, exatamente três e mais de três linhas subjacentes;
- dois pares em colunas diferentes, contados uma única vez;
- uma tripla acompanhada de um par, classificada somente como tripla;
- colunas 1 e 10, incluindo os limites `01` e `60`;
- entrada fora de ordem;
- quantidade diferente de seis, repetição, tipo inválido e valores fora de
  `01` a `60`;
- histórico vazio, uma ocorrência e várias ocorrências com intervalos conhecidos.

## 6. Limite da subetapa 11.1

Este documento define a regra e os testes esperados. Detectores, registro das
funções, recálculo estatístico e gravação no PostgreSQL serão implementados nas
subetapas posteriores, após autorização expressa.
