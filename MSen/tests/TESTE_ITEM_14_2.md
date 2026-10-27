# Evidência do Item 14.2 — gerador amostral repetível

Data: 2026-10-27.

## Comportamento validado

- A semente padrão `20261027` gera exatamente 5.000 combinações.
- Todas são distintas e possuem seis dezenas também distintas.
- Cada dezena está entre 01 e 60 e cada combinação está em ordem crescente.
- Repetir a mesma semente reproduz a mesma lista e a mesma ordem.
- Outra semente produz uma amostra diferente.
- O estado aleatório global do Python não é alterado.
- O gerador rejeita o modo integral e configurações não validadas.

Para a versão atual do Python, a primeira combinação foi
`(4, 9, 10, 13, 39, 52)`, a última `(20, 23, 32, 47, 51, 60)` e a representação
canônica da amostra produziu SHA-256
`dee454438e2c78232c466a76245e794884a5c029895776ee8f06494307289dac`.

## Testes

- 7 testes específicos: aprovados.
- Regressão Python completa: 267 testes aprovados.

Nenhum filtro foi executado, nenhuma combinação foi gravada e nenhum banco de
dados foi modificado.
