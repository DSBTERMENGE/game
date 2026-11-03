# Conteúdo aprovado para implementação — subetapa 22.17.6.0

Data: 02/11/2026

Os textos abaixo serão usados nos modais de ajuda. Nesta subetapa nenhum botão,
modal ou gráfico foi alterado.

## Ajuda — Evolução dos intervalos

### Finalidade

Este gráfico mostra como os intervalos entre ocorrências consecutivas da dezena
e suas estatísticas acumuladas evoluíram ao longo dos concursos. Ele permite
observar estabilidade, mudanças de comportamento e intervalos excepcionalmente
curtos ou longos.

### Como ler os eixos

- **Eixo horizontal:** número do concurso.
- **Eixo vertical:** duração do intervalo, medida em concursos.

### Linhas e marcadores

- **Intervalos:** cada trecho horizontal representa a distância entre duas
  ocorrências consecutivas da dezena. A transição vertical tracejada indica a
  passagem para o próximo intervalo.
- **Média dos intervalos:** média acumulada dos intervalos conhecidos até
  aquele momento.
- **Média menos desvio-padrão:** referência inferior de dispersão.
- **Média mais desvio-padrão:** referência superior de dispersão.
- **Losango com haste tracejada:** identifica um intervalo curto demais para
  aparecer claramente na escala horizontal.

Passe o mouse, use o teclado ou clique nos marcadores para consultar os
concursos inicial e final e a duração exata do intervalo.

### Exemplo de leitura

Se o detalhe informar `Concursos 1246 → 1261 · intervalo 15`, a dezena ocorreu
nos concursos 1246 e 1261, ficando 15 concursos entre essas duas ocorrências.
Compare a altura desse intervalo com a média e com as duas linhas de
desvio-padrão para avaliar se ele foi comum ou distante do comportamento
acumulado.

### Cuidados

O gráfico descreve o histórico. Média e desvio-padrão mudam quando novos
intervalos são concluídos e não garantem quando acontecerá a próxima
ocorrência.

## Ajuda — Curva de distribuição

### Finalidade

Este gráfico mostra com que frequência cada duração de intervalo ocorreu. Ele
ajuda a identificar onde as ocorrências estão concentradas e a partir de qual
duração os intervalos se tornam raros.

### Como ler os eixos

- **Eixo horizontal:** duração do intervalo em concursos.
- **Eixo vertical:** percentual das ocorrências que tiveram aquela duração.

### Curvas e referências

- **Distribuição observada:** frequência percentual realmente encontrada para
  cada duração.
- **Curva normal teórica:** referência matemática calculada com a mesma média e
  o mesmo desvio-padrão dos intervalos observados.
- **Média:** duração média dos intervalos.
- **Média ± desvio-padrão:** duas referências verticais que delimitam um desvio
  abaixo e acima da média.

Ao selecionar um ponto da distribuição observada, o detalhe informa a duração,
a quantidade de ocorrências e o percentual exato.

### Exemplo de leitura

`Intervalo 4: 28 ocorrências · 11,07%` significa que 28 dos intervalos
analisados duraram quatro concursos, representando 11,07% do total.

### Cuidados

A curva normal é apenas uma comparação. Intervalos são valores inteiros e sua
distribuição pode ser assimétrica e concentrada nas durações pequenas; por isso
a curva observada não precisa acompanhar a curva normal.

## Ajuda — Ocorrências em ordem crescente

### Finalidade

Este gráfico ordena todos os intervalos do menor para o maior, preservando cada
ocorrência repetida. Ele permite estimar visualmente qual percentual dos
intervalos está concentrado até determinada proporção do maior intervalo.

### Como ler os eixos

- **Eixo horizontal:** percentual acumulado das ocorrências ordenadas.
- **Eixo vertical:** duração do intervalo como percentual do maior intervalo
  observado.

Os dois eixos vão de 0% a 100%. As linhas finas de 5% em 5% formam apenas um
quadriculado de referência. Os pontos usam seus percentuais exatos e podem
ficar entre as linhas da grade.

### Como os pontos são calculados

Depois de ordenar `N` intervalos, a posição horizontal do item `i` é
`i ÷ N × 100`. Sua altura é a duração daquele intervalo dividida pelo maior
intervalo e multiplicada por 100.

### Pontos, patamares e saltos

- Cada ponto vermelho representa uma ocorrência de intervalo.
- Pontos igualmente espaçados na horizontal representam ocorrências
  consecutivas da lista ordenada.
- Vários intervalos com a mesma duração ficam na mesma altura e formam um
  patamar horizontal. Quanto maior o patamar, mais vezes essa duração ocorreu.
- Um salto vertical maior não indica erro de ordenação: pode significar que as
  durações intermediárias não ocorreram.
- O último ponto é sempre `(100%, 100%)`, pois representa a última ocorrência
  ordenada e o maior intervalo observado.

### Detalhe ao selecionar um ponto

Exemplo:

```text
Ocorrência 32 de 253 · 12,65% acumulado · intervalo 2 · 4% do maior
```

Isso significa:

- é o 32º intervalo depois da ordenação;
- ele completa 12,65% das 253 ocorrências;
- sua duração real foi de dois concursos;
- dois concursos correspondem a 4% do maior intervalo da amostra.

### Cuidados

Este gráfico descreve concentração e dispersão dos intervalos históricos. Ele
não classifica automaticamente as dezenas nem garante maior probabilidade no
próximo concurso.

## Resultado

Os três textos estão prontos para implementação no modal reutilizável da
subetapa 22.17.6.1 e para posterior análise visual do usuário.
