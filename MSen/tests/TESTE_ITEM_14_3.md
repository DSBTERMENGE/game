# Evidência do Item 14.3 — gerador integral protegido

Data: 2026-10-27.

## Implementação

O iterador definitivo usa
`itertools.combinations(range(1, 61), 6)`. O universo matemático foi confirmado
como 50.063.860 combinações.

No modo `amostra`, `itertools.islice` encerra o iterador exatamente no item
5.000. No modo `integral`, o iterador somente é devolvido quando:

1. a configuração validada usa `modo = "integral"`;
2. `confirmacao_processamento_integral` é verdadeira; e
3. a chamada fornece a frase `PROCESSAR_50063860_COMBINACOES`.

O iterador é preguiçoso: criá-lo não materializa nem percorre o universo.

## Testes

- 7 testes específicos aprovados.
- Regressão Python completa: 274 testes aprovados.
- O teste integral consumiu somente as duas primeiras combinações.

Nenhuma execução integral foi realizada, nenhuma combinação foi gravada e
nenhum banco de dados foi modificado.
