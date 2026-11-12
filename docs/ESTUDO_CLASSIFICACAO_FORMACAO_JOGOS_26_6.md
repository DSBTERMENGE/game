# Estudo da classificação das combinações — etapa 26.6

## Conclusão

As medidas existentes permitem ordenar combinações por semelhança com o
histórico, mas não sustentam a afirmação de que uma combinação aprovada seja
mais provável de ser sorteada que outra. Em uma loteria regular, todas as
combinações distintas de seis dezenas continuam com a mesma probabilidade
teórica.

## Medidas disponíveis

O sistema possui três medidas estatísticas independentes no Screener:

- soma (a média é equivalente e não deve ser contada novamente);
- mediana;
- desvio-padrão populacional.

Possui também cinco decisões geométricas:

- extensão aberta;
- perímetro fechado;
- área total;
- quantidade de regiões;
- centro de gravidade, com X e Y avaliados conjuntamente.

Os padrões históricos são decisões categóricas de aprovação ou reprovação. Sua
frequência não deve ser somada como se fosse probabilidade individual do jogo.

## Critério candidato avaliado

Foi avaliado um índice de centralidade histórica. Para evitar que uma família
com mais campos dominasse a outra, estatística e geometria receberam metade do
índice cada. Dentro de cada família, as medidas tiveram participação igual.

Para cada medida foi calculada a distância padronizada:

`z = (valor da combinação - média histórica) / desvio histórico`

Em seguida:

`D = 0,5 × média(z² estatísticos) + 0,5 × média(z² geométricos)`

`índice de centralidade = 1 / (1 + D)`

Um índice maior significa somente maior proximidade do centro histórico. Não é
uma probabilidade.

## Avaliação sem dados futuros

Foram avaliados os concursos 500 a 3.069. Para cada concurso, médias e desvios
foram calculados exclusivamente com concursos anteriores. O resultado real foi
comparado com 20 combinações-controle determinísticas, totalizando 2.570 alvos.

Resultados:

- percentil médio do resultado real: `50,2179%`;
- resultados reais acima da mediana dos controles: `47,3541%`.

O comportamento é compatível com acaso e não demonstra poder preditivo. Além
disso, o Screener integral permanece sem homologação; portanto ainda não é
possível avaliar o índice somente entre combinações aprovadas pelo funil final.

## Alternativas para decisão

### A — Ordem neutra reproduzível (recomendada)

Todas as combinações aprovadas são tratadas como equivalentes. A ordem é
produzida por SHA-256 sobre concurso, assinatura do Screener e seis dezenas. O
menor hash vem primeiro; um eventual empate usa as dezenas em ordem crescente.

Vantagens: não cria falsa probabilidade, não favorece dezenas pequenas e é
integralmente reproduzível. O nome sugerido é `ORDEM_NEUTRA_SHA256_V1`.

### B — Aderência histórica

Usar o índice avaliado para colocar primeiro as combinações mais centrais. O
nome deve ser `ADERENCIA_HISTORICA_V1`, nunca “probabilidade”. O desempate seria
pela menor distância máxima entre as medidas e, persistindo, pelas dezenas em
ordem crescente.

Esta alternativa é explicável, mas o ensaio não mostrou vantagem preditiva.

### C — Não ordenar

Exibir as aprovadas em ordem lexicográfica. É simples e reproduzível, mas ao
aplicar um teto financeiro favorece sistematicamente combinações com dezenas
menores.

## Recomendação

Adotar a alternativa A. A alternativa B pode permanecer apenas como informação
analítica opcional, depois de o Screener estar homologado e de nova avaliação.
Nenhum classificador definitivo foi implementado antes da decisão do usuário.
