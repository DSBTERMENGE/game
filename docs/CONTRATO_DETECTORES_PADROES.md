# Contrato das funções detectoras de padrões

Este documento define a interface comum das funções associadas ao campo
`padroes_subgrupo.funcao_detectora`. Ele vale para os detectores existentes e
para os novos padrões geométricos.

## Assinatura

Cada detector é uma função pura com a seguinte forma:

```python
def detectar_padrao(dezenas: tuple[int, ...]) -> bool:
    ...
```

- o único argumento contém as seis dezenas do resultado ou da combinação;
- a ordem recebida não altera a resposta;
- o retorno deve ser exatamente `True` ou `False`;
- valores apenas equivalentes a booleanos, como `0` e `1`, não são aceitos;
- `True` significa que a combinação corresponde ao padrão específico da
  função, e não que o padrão é raro.

A raridade é decidida posteriormente pela incidência histórica e pelo limite
configurado. O detector não consulta nem aplica esse limite.

## Validação da entrada

Uma entrada válida possui:

- exatamente seis elementos;
- somente números inteiros, sem aceitar valores booleanos;
- dezenas entre 1 e 60;
- seis dezenas diferentes.

Tipo de coleção inválido ou elemento de tipo inválido produz `TypeError`.
Quantidade, faixa ou repetição inválida produz `ValueError`. Entrada inválida
não pode ser interpretada silenciosamente como ausência do padrão.

## Pureza e reprodutibilidade

Um detector:

- não altera a coleção recebida;
- não grava no banco;
- não depende da data, de aleatoriedade ou de configuração global mutável;
- devolve sempre a mesma resposta para as mesmas seis dezenas;
- conta cada concurso no máximo uma vez, mesmo que encontre mais de uma
  formação interna equivalente.

Auxiliares podem produzir evidências geométricas para auditoria, mas a função
persistida em `funcao_detectora` mantém o retorno booleano.

## Sistema de coordenadas

O volante possui dez colunas e seis linhas. A dezena `01` é a origem `(0,0)`.
A conversão oficial já existente é:

```text
x = (dezena - 1) % 10
y = (dezena - 1) // 10
```

Exemplos:

| Dezena | Coordenada |
|---:|:---|
| 01 | `(0,0)` |
| 10 | `(9,0)` |
| 11 | `(0,1)` |
| 15 | `(4,1)` |
| 42 | `(1,4)` |
| 60 | `(9,5)` |

Avançar uma casa horizontal incrementa `x`. Avançar uma linha incrementa `y`.
Os detectores devem reutilizar `msen.calculos.calcular_coordenada`, evitando
uma segunda convenção de coordenadas.

## Convenção das diagonais

- `PG_004` representa o passo numérico `+11`, deslocamento `(1,1)` ao descer
  uma linha. Exemplo: `04, 15, 26, 37`.
- `PG_006` representa o passo numérico `+9`, deslocamento `(-1,1)` ao descer
  uma linha. Exemplo: `07, 16, 25, 34`.

Somar ou subtrair o passo não é suficiente sem respeitar os limites da grade.
A identificação definitiva deve comparar as coordenadas, impedindo que uma
sequência atravesse indevidamente uma borda do volante.

## Exatidão e tolerância

Relações próprias da grade inteira, como linha, coluna, diagonal e
colinearidade, usam comparações exatas. Deve-se preferir produto vetorial,
distância ao quadrado e outros cálculos inteiros, sem arredondamento.

Somente padrões declarados como aproximados podem usar tolerância. Cada
tolerância deverá ser definida e aprovada junto com o respectivo padrão; não
existirá uma tolerância implícita comum a círculos, arcos e elipses.

## Resolução e execução

O nome persistido deve ser completo, por exemplo:

```text
msen.padroes.diagonais.detectar_duas_dezenas_passo_11
```

Somente funções dentro de `msen.padroes` podem ser resolvidas. Função ausente,
módulo ausente, objeto não chamável ou retorno não booleano interrompe a
execução com erro explícito; nenhum desses casos significa `False`.

Um padrão novo permanece fora do screener enquanto não possuir detector,
testes, homologação e estatística histórica aprovados.
