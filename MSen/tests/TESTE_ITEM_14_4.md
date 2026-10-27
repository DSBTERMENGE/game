# Evidência do Item 14.4 — estrutura do funil e contadores

Data: 2026-10-27.

## Estrutura entregue

O funil recebe combinações e uma sequência ordenada de critérios. Para cada
combinação, os critérios são consultados nessa ordem. A primeira reprovação:

1. incrementa somente o contador daquele critério;
2. impede a avaliação pelos critérios seguintes; e
3. avança imediatamente para a próxima combinação.

O relatório informa total recebido, total aprovado, ordem, quantidade de
avaliações, exclusões por critério, saldo após cada critério e combinações
aprovadas. Códigos vazios, duplicados ou divergentes na decisão são rejeitados.

## Testes

- Sem filtros reais, as 5.000 combinações foram preservadas.
- Filtros artificiais comprovaram contadores, saldos e salto imediato.
- 5 testes específicos aprovados.
- Regressão Python completa: 279 testes aprovados.

Os filtros artificiais existem somente no teste. Nenhum critério real foi
ativado, nenhuma combinação foi gravada e nenhum banco foi modificado.
