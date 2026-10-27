# Item 15.12 — média aritmética em modo sombra

Data: 2026-10-27

## Regra experimental aprovada para teste

- Medida: média aritmética das seis dezenas.
- Limite inferior histórico P01: 15,000000.
- Limite superior histórico P99: 45,886666.
- Comparação estrita: marcar se média `< 15,000000` ou `> 45,886666`.
- Os valores exatamente iguais aos limites permanecem dentro da faixa.

## Simulação sombra

| Semente | Avaliadas | Marcadas | Percentual | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 108 | 2,16% | 4.892 |
| 42 | 5.000 | 96 | 1,92% | 4.904 |

Todas as 10.000 combinações continuaram realmente aprovadas. A política apenas
registrou `marcaria_exclusao` e não foi conectada ao funil ativo.

## Validações

- Média calculada com seis casas decimais e arredondamento `ROUND_HALF_UP`.
- Limites exatos testados como aceitos.
- Um milionésimo abaixo e acima dos limites testado como fora da faixa.
- Limites invertidos são rejeitados.
- Passaram 343 testes antes da inclusão do teste reproduzível da simulação.
- Processamento integral continua bloqueado e o banco não foi escrito.

Resultado: política experimental validada em sombra; qualquer ativação real
depende de nova autorização específica.

## Ativação experimental autorizada

O usuário escolheu a opção 3 e autorizou a ativação apenas na amostra protegida.
A média foi conectada como quinto filtro, depois dos padrões históricos:

- recebeu 4.712 combinações;
- excluiu 89 combinações;
- deixou saldo final de 4.623.

Das 108 marcações sombra, 19 já tinham sido excluídas pelos quatro filtros
anteriores. O funil contabilizou somente as 89 exclusões líquidas na média.
A contabilidade completa fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 4.623`.

Passaram 346 testes. O processamento integral continua bloqueado e nenhuma
escrita foi feita no banco.
