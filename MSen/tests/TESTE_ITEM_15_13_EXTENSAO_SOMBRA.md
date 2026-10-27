# Item 15.13 — extensão aberta em modo sombra

Data: 2026-10-27

## Regra experimental aprovada para teste

- Medida: extensão euclidiana dos cinco segmentos do caminho aberto.
- Limite inferior: 8,650282.
- Limite superior: 32,300058.
- Comparação estrita; limites exatos permanecem aceitos.

Os limites aprovados têm seis casas. Ao reaplicar exatamente esses valores ao
histórico, 33 resultados ficam abaixo e 31 acima, total 64 (`2,085370%`). Isso
corrige a estimativa inicial de 61, que havia usado internamente o percentil
bruto com mais casas antes de exibir os limites arredondados.

## Simulação sombra

| Semente | Avaliadas | Marcadas | Percentual | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 106 | 2,12% | 4.894 |
| 42 | 5.000 | 115 | 2,30% | 4.885 |

Todas continuaram realmente aprovadas. A política não integra o funil ativo.

## Validações

- Função geométrica de produção com precisão persistida de 12 casas.
- Limites exatos aceitos; um milionésimo além marcado.
- Contagens reproduzíveis nas duas sementes.
- Passaram 366 testes antes do teste reproduzível da simulação.
- Banco e processamento integral não foram alterados.

Resultado: extensão validada em sombra; ativação experimental depende de
autorização específica.
