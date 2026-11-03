# Contrato da quantidade de dezenas e formação de jogos

Este documento fecha a subetapa 23.2. Ele separa o screener de dezenas do
screener de combinações e define como obter uma quantidade desejada de dezenas
antes de formar jogos de seis.

## 1. Dois screeners sucessivos

### 1.1. Screener de dezenas

Usa as ocorrências `SIMPLES`, `k`, `j`, média e desvio-padrão para:

1. avaliar as 60 dezenas para o concurso-alvo;
2. aprovar as dezenas cuja faixa contém o alvo;
3. classificar todas as dezenas com base matemática;
4. formar o conjunto final na quantidade escolhida.

O acerto do backtest é sempre a presença da dezena no resultado, sem posição.

### 1.2. Screener de combinações

Recebe somente o conjunto final de dezenas e forma combinações de seis. Depois
aplica critérios próprios para aprovar ou rejeitar cada jogo. `2VS` e `3VS`
pertencem a este segundo screener: medem repetição consecutiva e podem eliminar
combinações consideradas inadequadas ou raras.

A aprovação de uma dezena não garante a aprovação de todas as combinações que
a contenham.

## 2. Classificação das dezenas

Para uma dezena com desvio `σ > 0`:

```text
distancia_normalizada =
    abs(concurso_alvo - centro_ajustado) / σ
```

Menor distância significa maior aderência ao retorno previsto. A dezena é
aprovada pela faixa operacional conforme o contrato da subetapa 23.0. O ranking
é aplicado somente às aprovadas quando for necessário reduzir sua quantidade e
não deve ser apresentado como probabilidade matemática garantida.

Para desempatar:

1. menor distância normalizada;
2. menor distância absoluta em concursos;
3. menor número da dezena, somente para produzir resultado determinístico.

Com `σ = 0`, o alvo igual ao centro recebe distância zero. Se o alvo for
diferente, a dezena não é aprovada. Dezena `SEM_BASE` não entra no conjunto.

## 3. Formas de escolher a quantidade

A quantidade faz parte da configuração e possui dois modos:

- **`MAX`:** retorna todas as dezenas aprovadas pela faixa;
- **`FIXA`:** recebe um inteiro `N` e retorna no máximo `N` aprovadas, escolhidas
  pelo ranking quando houver excesso.

No modo `FIXA`:

- se houver mais de `N` aprovadas, conservar as `N` mais bem classificadas;
- se houver exatamente `N`, conservar todas;
- se houver menos de `N`, retornar somente as aprovadas existentes;
- nunca acrescentar dezena fora da faixa para completar `N`;
- registrar no log que o máximo atingido pelo critério foi `M`, quando `M < N`.

O relatório por concurso deve distinguir:

- modo e quantidade configurada (`MAX` ou `N`);
- quantidade aprovada pela faixa (`M`);
- quantidade efetivamente retornada (`R`);
- indicação de limite não atingido quando `M < N`.

No modo `MAX`, `R = M`. No modo `FIXA`, `R = min(M, N)`. Para configurações
destinadas à formação de jogos, `N` deve ficar entre 6 e 60.

Para gerar ao menos um jogo de seis, o conjunto final precisa ter `N >= 6`.
Para apenas estudar a seleção, conjuntos menores podem ser exibidos, mas não
geram combinação.

## 4. Quantidade de jogos completos

Se forem geradas todas as combinações de seis dentre `N` dezenas:

```text
C(N,6) = N! / (6! × (N-6)!)
```

| N | Jogos de seis |
|---:|---:|
| 6 | 1 |
| 7 | 7 |
| 8 | 28 |
| 9 | 84 |
| 10 | 210 |
| 11 | 462 |
| 12 | 924 |
| 13 | 1.716 |
| 14 | 3.003 |
| 15 | 5.005 |
| 20 | 38.760 |
| 30 | 593.775 |
| 40 | 3.838.380 |
| 50 | 15.890.700 |
| 60 | 50.063.860 |

O sistema deve calcular e mostrar esse volume antes da geração. A quantidade
máxima permitida será uma configuração operacional posterior, pois depende do
custo que o usuário aceitar.

## 5. Relação entre acertos e jogos

Se o conjunto de `N` dezenas contiver `H` das seis sorteadas, o maior número de
acertos possível em um jogo formado somente por esse conjunto é `H`.

Quando todas as combinações são geradas, a quantidade de jogos que contém as
`H` dezenas corretas disponíveis é:

```text
C(N-H, 6-H)
```

Exemplos:

- `H = 6`: existe exatamente 1 jogo com seis acertos;
- `H = 5`: existem `N - 5` jogos contendo as cinco dezenas corretas;
- `H = 4`: existem `C(N - 4, 2)` jogos contendo as quatro corretas.

Esses valores são anteriores ao screener de combinações. Um filtro posterior
pode rejeitar alguns desses jogos, inclusive o que coincidiria com o resultado;
esse efeito deverá ser medido separadamente no backtest do segundo screener.

## 6. Todas as combinações e lotes limitados

Gerar `C(N,6)` significa materializar todas as combinações. Gerar somente uma
quantidade limitada de jogos é outro problema: exige estratégia de cobertura,
critério de escolha e backtest próprios. Nenhum subconjunto limitado será
apresentado como equivalente ao conjunto completo.

## 7. Casos manuais obrigatórios

### 7.1. Redução

Se 15 dezenas forem aprovadas e o usuário solicitar 8, o modo automático usa
as 8 aprovadas mais bem classificadas. O modo manual permite escolher entre as
15 apresentadas.

### 7.2. Quantidade solicitada não atingida

Se 5 dezenas forem aprovadas e a configuração solicitar 8, o sistema retorna
as 5 aprovadas e registra: `O máximo possível para este concurso e configuração
é 5 dezenas.` Nenhuma dezena fora da faixa é acrescentada.

### 7.3. Custo

Oito dezenas produzem 28 combinações completas; dez dezenas produzem 210. O
usuário deve conhecer esse custo antes de confirmar a geração.

### 7.4. Separação dos screeners

Uma seleção final com 10 dezenas produz 210 combinações brutas. O screener de
combinações pode aprovar apenas parte delas devido a 2VS, 3VS e demais critérios;
as 10 dezenas originais continuam sendo a saída do primeiro screener.

## 8. Fora do escopo da subetapa 23.2

- fórmula e limites definitivos dos filtros 2VS e 3VS nas combinações;
- demais filtros do screener de combinações;
- limite financeiro ou operacional máximo;
- escolha manual de dezenas e estratégia de lotes incompletos;
- DDL, persistência, API e página.
