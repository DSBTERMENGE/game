# Evidência do Item 15.8 — simulação sombra de PD_003

Data: 2026-10-27.

Foram executadas duas amostras reproduzíveis de 5.000 combinações com a
hipótese **não aprovada** de tolerância de 3%.

| Semente | Avaliadas | Marcadas em sombra | Percentual | Saldo hipotético | Aprovadas reais | Excluídas reais | Tempo |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 11 | 0,22% | 4.989 | 5.000 | 0 | ~0,035 s |
| 42 | 5.000 | 5 | 0,10% | 4.995 | 5.000 | 0 | ~0,030 s |

O histórico observado é 5/3.069 = 0,162920%, situado entre os percentuais das
duas amostras. A diferença entre 0,10% e 0,22% mostra que 5.000 combinações são
sensíveis à semente para um evento raro. Nenhuma das amostras deve ser tratada
como prova da proporção nas 50.063.860 combinações.

Todos os exemplos marcados contêm um bloco de quatro ou cinco dezenas
consecutivas e foram preservados para a futura saída de validação humana.

## Segurança e testes

- As 10.000 combinações foram realmente aprovadas; exclusões reais: zero.
- A configuração padrão permaneceu desabilitada.
- 3 testes genéricos e 1 teste reproduzível da amostra foram aprovados.
- Regressão Python completa: 309 testes aprovados.
- Nenhum dado foi gravado no banco.
