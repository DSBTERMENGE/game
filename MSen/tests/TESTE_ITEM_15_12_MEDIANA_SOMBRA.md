# Item 15.12 — mediana em modo sombra

Data: 2026-10-27

## Regra experimental aprovada para teste

- Medida: mediana das seis dezenas ordenadas.
- Limite inferior P01: 10,5.
- Limite superior P99: 50,5.
- Comparação estrita: marcar se `< 10,5` ou `> 50,5`.
- Valores exatamente iguais aos limites permanecem aceitos.

## Simulação sombra

| Semente | Avaliadas | Marcadas | Percentual | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 92 | 1,84% | 4.908 |
| 42 | 5.000 | 91 | 1,82% | 4.909 |

Todas as 10.000 combinações continuaram realmente aprovadas. O cálculo usa a
média entre a terceira e a quarta dezena ordenada, igual ao campo persistido.

## Validações

- Limites exatos aceitos.
- Valores de meia unidade fora dos limites marcados.
- Entrada fora de ordem produz a mesma mediana.
- Passaram 359 testes antes do teste reproduzível da simulação.
- Funil ativo, processamento integral e banco não foram alterados.

Resultado: mediana validada em sombra; ativação experimental depende de
autorização específica.

## Ativação somente para teste da engrenagem

O usuário autorizou a mediana como sétimo filtro da amostra protegida:

- recebeu 4.528 combinações;
- excluiu 44 combinações;
- deixou saldo final 4.484.

Das 92 marcações sombra, 48 já haviam sido excluídas pelos seis filtros
anteriores. A contabilidade completa fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 44 + 4.484`.

Passaram 362 testes. A faixa permanece experimental, o processamento integral
continua bloqueado e o banco não foi escrito.
