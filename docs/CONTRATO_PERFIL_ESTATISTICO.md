# Contrato do perfil estatístico genérico

O perfil recebe uma série numérica não vazia, normalmente extraída por meio da
janela histórica, e calcula:

- quantidade;
- média;
- desvio-padrão populacional;
- mínimo e máximo;
- distribuição empírica: valor distinto, frequência e percentual.

Os cálculos usam `Decimal`. Inteiros são aceitos sem conversão intermediária
para ponto flutuante. Valores booleanos, não numéricos, infinitos e `NaN` são
rejeitados.

O desvio é populacional porque o perfil descreve toda a janela histórica
selecionada. Ele não representa uma estimativa obtida de parte dessa janela.

## Faixas configuráveis

Há dois métodos independentes:

1. percentual da média: `média - margem inferior` até
   `média + margem superior`;
2. múltiplos do desvio: `média - k inferior × desvio` até
   `média + k superior × desvio`.

As margens inferior e superior podem ser diferentes. Os limites são inclusivos.
Nesta subetapa, estar fora da faixa é apenas uma informação matemática: nenhuma
combinação é excluída e nenhuma regra do screener é alterada.

## Distribuição e curva normal

A distribuição registrada é a frequência real observada, sem presumir
normalidade. O histograma por classes e uma eventual curva normal de referência
serão construídos nas subetapas de API e visualização.
