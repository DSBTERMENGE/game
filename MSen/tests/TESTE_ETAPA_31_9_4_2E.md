# Evidência — subetapa 31.9.4.2E

Data: 14/11/2026

## Escopo autorizado

Aplicar o mecanismo comum somente à mancha da Média espacial. CG1, CG2,
Quadrantes e Dezenas não poderiam ser migrados nesta subetapa.

## Implementação

- cada concurso produz um círculo individual;
- a coordenada decimal é convertida diretamente, sem arredondamento;
- cor marrom, diâmetro e fator de intensidade vêm da configuração visual v3;
- o diâmetro não varia conforme frequência ou coincidência;
- a intensidade varia pela distância à média das médias;
- a média das médias é indicada por um círculo amarelo;
- círculos amarelos finos marcam os níveis de 20%, 40% e 60%;
- os percentuais são escritos em percursos curvos associados aos círculos;
- o resumo lateral mostra a média das médias e as quantidades acumuladas até
  20%, 40%, 60% e 100%.

## Validação

Testes direcionados:

```text
node --test frontend/tests/manchas_medias.test.mjs frontend/tests/plotagem_manchas.test.mjs frontend/tests/painel_navegacao.test.mjs
```

Resultado: 40 testes aprovados, 0 falhas.

Suíte completa:

```text
npm run test:frontend
```

Resultado: 144 testes aprovados, 0 falhas.

## Ajuste visual posterior

- espessura das referências aumentada de 1 para 1,5;
- relatório alterado para parcelas não acumuladas;
- cada parcela apresenta `1:N`, calculado por
  `arredondar(total de concursos / quantidade da faixa)`;
- faixa sem resultados informa `sem ocorrência`;
- teste adicional comprova que um fator configurado, como 0,18, substitui o
  padrão 0,12 e altera proporcionalmente todas as intensidades.

Resultado final: 145 testes do frontend aprovados, 0 falhas.
