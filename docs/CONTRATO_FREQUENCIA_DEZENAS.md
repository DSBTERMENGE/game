# Contrato matemático — Frequência das dezenas

Este documento fecha a subetapa 22.0. Ele define somente as regras matemáticas
que serão usadas posteriormente. Não cria tabelas nem autoriza implementação.

## 1. Série analisada e corte temporal

- Os resultados são ordenados por `numero_ap` crescente.
- Toda fotografia do concurso `C` usa exclusivamente resultados com
  `numero_ap <= C`.
- O período inicial aprovado é inclusivo, do concurso 1 ao concurso 500.
- Não se consulta resultado posterior a `C` para classificar um evento ou
  calcular uma estatística da fotografia `C`.
- Cada dezena de 01 a 60 é analisada separadamente.

## 2. Ocorrência simples

Uma ocorrência simples da dezena `D` é a presença de `D` entre as seis dezenas
de um concurso. O evento é representado pelo próprio número do concurso.

Exemplo: ocorrências nos concursos 35 e 50 formam os eventos `(35, 50)` e o
intervalo observado é `50 - 35 = 15` concursos.

## 3. Eventos 2VS e 3VS

`2VS` significa que a mesma dezena ocorreu em dois concursos consecutivos.
O evento é concluído e representado pelo segundo concurso.

```text
dezena presente em 210 e 211 -> evento 2VS concluído em 211
```

`3VS` significa que a mesma dezena ocorreu em três concursos consecutivos.
O evento é concluído e representado pelo terceiro concurso.

```text
dezena presente em 615, 616 e 617 -> evento 3VS concluído em 617
```

As sequências usam janelas consecutivas e sobrepostas. Assim, uma sequência
com três ou mais ocorrências também produz os eventos menores que já estavam
completos naquele momento. Essa regra evita depender de informação futura.

| Sequência consecutiva | Eventos 2VS concluídos em | Eventos 3VS concluídos em |
|---|---|---|
| 210, 211 | 211 | nenhum |
| 615, 616, 617 | 616 e 617 | 617 |
| 700, 701, 702, 703 | 701, 702 e 703 | 702 e 703 |

Portanto, uma sequência de comprimento `L` produz:

- `max(L - 1, 0)` eventos 2VS;
- `max(L - 2, 0)` eventos 3VS.

Uma interrupção encerra a sequência. Por exemplo, ocorrências em 800, 801 e
803 produzem um 2VS concluído em 801; o concurso 803 inicia outra sequência.

## 4. Intervalos entre eventos

Para qualquer tipo — simples, 2VS ou 3VS — primeiro se forma a lista crescente
dos concursos de conclusão dos eventos equivalentes:

```text
E = (e1, e2, ..., en)
```

Os intervalos são:

```text
I = (e2 - e1, e3 - e2, ..., en - e(n-1))
```

Não se mistura tipo de evento: intervalos simples são calculados entre eventos
simples; intervalos 2VS, entre conclusões 2VS; e intervalos 3VS, entre
conclusões 3VS.

## 5. Quantidades mínimas e estados estatísticos

| Quantidade de eventos | Quantidade de intervalos | Média/mediana/desvio |
|---:|---:|---|
| 0 | 0 | `NULL` — sem eventos |
| 1 | 0 | `NULL` — sem intervalo observado |
| 2 | 1 | média e mediana iguais ao intervalo; desvio `0` |
| 3 ou mais | eventos menos 1 | calculados normalmente |

Um valor `NULL` significa ausência de base matemática e nunca será substituído
por zero. O estado sem base não conta como acerto nem como erro em futura
avaliação de assertividade.

## 6. Estatísticas e unidades

- Média e mediana são calculadas sobre os intervalos observados.
- O desvio-padrão é populacional, com divisor igual à quantidade de intervalos.
- Média, mediana e desvio permanecem na unidade **concurso**.
- O cálculo usa `Decimal`; valores intermediários não são arredondados.
- O valor persistido ou intercambiado terá inicialmente seis casas decimais e
  `ROUND_HALF_UP`, preservando o contrato já adotado pelo sistema.
- Nesta etapa o desvio não é percentual e não existe conversão implícita entre
  unidade e percentual.

## 7. Faixa inicial de retorno

Existindo ao menos um intervalo, para o último evento concluído `U`:

```text
previsao_central = U + media_intervalos
limite_inferior_exato = previsao_central - desvio_padrao
limite_superior_exato = previsao_central + desvio_padrao
```

Como concursos são inteiros, a faixa operacional usa arredondamento externo:

```text
limite_inferior = floor(limite_inferior_exato)
limite_superior = ceil(limite_superior_exato)
```

Os dois limites são inclusivos. Os valores exatos permanecem disponíveis para
gráficos e conferência. Se o limite inferior resultar anterior ou igual ao
último evento, ele será limitado a `U + 1`, pois um retorno futuro não pode
anteceder nem coincidir com o evento que originou a previsão.

## 8. Casos manuais obrigatórios para a implementação futura

1. **Simples:** eventos 10, 20, 35 e 50; intervalos 10, 15 e 15; média
   `13,333333`; mediana `15`; desvio populacional `2,357023`.
2. **2VS isolado:** presença em 210 e 211; um evento 2VS em 211, nenhum
   intervalo e estatísticas `NULL`.
3. **3VS sobreposto:** presença em 615, 616 e 617; eventos 2VS em 616 e 617,
   intervalo 2VS igual a 1; evento 3VS em 617 sem intervalo.
4. **Quatro seguidos:** presença em 700 a 703; eventos 2VS em 701, 702 e 703 e
   eventos 3VS em 702 e 703; todos os intervalos iguais a 1 e desvios iguais a
   zero.
5. **Interrupção:** presença em 800, 801 e 803; somente um evento 2VS em 801 e
   nenhum evento 3VS.
6. **Sem vazamento futuro:** a fotografia 616 conhece o 2VS concluído em 616,
   mas não pode conhecer o 3VS que somente será concluído em 617.
7. **Limites inclusivos:** ocorrência exatamente no limite inferior ou superior
   deverá ser considerada dentro da faixa na futura avaliação.

## 9. Fora do escopo desta subetapa

- tabelas e migrações;
- funções de cálculo e persistência;
- API, página, menu e gráficos;
- escolha de percentuais na página Distribuições;
- fórmula definitiva do percentual de erro da avaliação posterior.

Esses assuntos permanecem nas subetapas seguintes da Etapa 22.
