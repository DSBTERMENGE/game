# Evidência — subetapa 31.9.4.2D

Data: 14/11/2026

## Escopo autorizado

Criar o cálculo comum das manchas de Média espacial, CG1 e CG2, sem conectá-lo
ao desenho do Painel e sem incluir Quadrantes ou Dezenas.

## Implementação

A função `prepararManchaDeMedia` foi acrescentada ao módulo
`frontend/js/manchas-medias.js`. Para qualquer uma das três médias, ela produz:

- identificação independente da camada;
- centro médio e distância do centro à origem;
- distância máxima observada;
- um ponto de saída para cada ponto decimal de entrada;
- intensidade individual calculada pelo fator configurado;
- cor e diâmetro próprios da camada;
- referências circulares de 20%, 40% e 60%;
- quantidades nas quatro faixas de concentração.

Pontos coincidentes mantêm índices diferentes. Não existe arredondamento,
agrupamento, alteração do diâmetro pela frequência nem descarte de pontos.

## Validação

Teste específico:

```text
node --test frontend/tests/manchas_medias.test.mjs
```

Resultado: 8 testes aprovados, 0 falhas.

Suíte completa:

```text
npm run test:frontend
```

Resultado: 144 testes aprovados, 0 falhas.
