# Evidência do Item 11.4 — integração e persistência de mesma coluna

Data: 2026-10-27.

## Integração

- catálogo unificado contém `PD_001`–`PD_006`;
- o serviço transacional calcula os dois grupos de padrões sobre a mesma série;
- somente padrões cadastrados e com estatística calculada são atualizados;
- a API reconhece `PD_004`–`PD_006` como detectores implementados;
- códigos futuros continuam sem receber estatísticas automaticamente.

O nome legado `recalcular_padroes_iniciais` foi preservado para não quebrar os
fluxos de importação, inclusão e edição que já chamam o serviço.

## Testes automatizados

- 43 testes direcionados aprovados durante a integração inicial;
- após o esclarecimento do Item 11.6, 44 testes direcionados e 205 testes
  Python foram aprovados com a regra de linhas subjacentes.

## PostgreSQL temporário

O database `games_test_7_1_1114` foi criado, recebeu as migrações, seis padrões
e sete resultados controlados. Duas execuções do recálculo produziram:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_004` | 2 | 15,000000 | 0,000000 |
| `PD_005` | 2 | 10,000000 | 0,000000 |
| `PD_006` | 2 | 20,000000 | 0,000000 |

O recálculo foi idempotente. O database temporário foi removido no bloco de
limpeza e a listagem final confirmou que nenhum database de teste permaneceu.

O database local `games` não foi lido nem alterado nesta subetapa.
