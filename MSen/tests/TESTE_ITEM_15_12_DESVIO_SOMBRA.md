# Item 15.12 — desvio-padrão em modo sombra

Data: 2026-10-27

## Regra experimental aprovada para teste

- Medida: desvio-padrão populacional das seis dezenas.
- Limite inferior P01: 7,145546.
- Limite superior P99: 22,774694.
- Comparação estrita: marcar se `< 7,145546` ou `> 22,774694`.
- Valores exatamente iguais aos limites permanecem aceitos.

## Simulação sombra

| Semente | Avaliadas | Marcadas | Percentual | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 132 | 2,64% | 4.868 |
| 42 | 5.000 | 122 | 2,44% | 4.878 |

Todas as 10.000 combinações continuaram realmente aprovadas. O cálculo usado
é a mesma função populacional que produz `resultados.desvio_padrao_media`.

## Validações

- Limites exatos aceitos.
- Um milionésimo além de cada limite marcado.
- Combinação de baixa dispersão marcada sem reprovação real.
- Combinação dentro da faixa aprovada.
- Passaram 350 testes antes do teste reproduzível da simulação.
- Funil ativo, processamento integral e banco não foram alterados.

Resultado: desvio-padrão validado em sombra; ativação depende de autorização
específica.

## Ativação somente para teste da engrenagem

O usuário autorizou a ativação experimental, deixando explícito que os limites
não são definitivos. O desvio foi conectado como sexto filtro:

- recebeu 4.623 combinações;
- excluiu 95 combinações;
- deixou saldo final 4.528.

Das 132 marcações sombra, 37 já tinham sido excluídas pelos filtros anteriores.
A contabilidade completa fechou em
`5.000 = 11 + 162 + 5 + 110 + 89 + 95 + 4.528`.

Passaram 353 testes. O processamento integral permanece bloqueado, o banco não
foi escrito e a faixa continua identificada como experimental.
