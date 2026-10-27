# Evidência do Item 12.4 — integração e persistência de mesma linha

Data: 2026-10-27.

## Integração

- o serviço transacional calcula os nove padrões aprovados sobre a mesma série;
- somente padrões cadastrados e com estatística calculada são atualizados;
- o catálogo unificado reconhece `PD_001`–`PD_009`;
- a migração `006` reserva `PG_003` e `PD_007`–`PD_009` em instalações novas;
- o esquema canônico inicializa três grupos e nove padrões;
- o primeiro código livre passa a ser `PD_010`.

## Testes

O database temporário `games_test_7_1_124` recebeu sete resultados controlados.
Duas execuções idempotentes produziram:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_007` | 2 | 15,000000 | 0,000000 |
| `PD_008` | 2 | 10,000000 | 0,000000 |
| `PD_009` | 2 | 20,000000 | 0,000000 |

Também foram validadas as migrações `001`–`006` sobre uma estrutura anterior e
o esquema canônico criado do zero, resultando em três grupos, nove padrões e
sequências posicionadas em `PG_003` e `PD_009`.

Passaram 216 testes Python. Todos os databases temporários foram removidos. O
database local `games` não foi acessado ou alterado nesta subetapa.
