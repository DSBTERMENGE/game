# Teste da subetapa 22.17.5-B.0

Data: 02/11/2026

## Contrato consolidado

Para uma lista de `N` intervalos, ordenada do menor para o maior e contada de
`i = 1` até `N`:

```text
X(i) = i / N × 100
Y(i) = intervalo(i) / maior_intervalo × 100
```

Os dois eixos terão domínio fixo de 0% a 100%. A grade visual será desenhada de
5% em 5%, mas não participará dos cálculos nem deslocará pontos.

## Casos verificados

- 20 ocorrências: passo horizontal de 5%; todos os pontos coincidem com marcas
  verticais da grade.
- 14 ocorrências: passo horizontal de aproximadamente 7,142857%; existem
  pontos entre as marcas da grade.
- 17 ocorrências: passo horizontal de aproximadamente 5,882353%; existem
  pontos entre as marcas da grade.
- Em todos os casos, o último ponto é `(100%, 100%)`.
- As repetições permanecem como ocorrências independentes e recebem a mesma
  coordenada vertical quando possuem a mesma duração.

## Testes

```text
node --test frontend/tests/frequencia_intervalos_auxiliares.test.mjs
tests 6
pass 6
fail 0
```

```text
npm run test:frontend
tests 75
pass 75
fail 0
```

## Resultado

Contrato aprovado. Nenhum código do desenho exibido foi alterado. A aplicação
do contrato ao SVG e à grade pertence à subetapa 22.17.5-B.1.
