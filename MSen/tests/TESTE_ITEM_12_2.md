# Evidência do Item 12.2 — detectores de mesma linha

Data: 2026-10-27.

## Implementação

- módulo puro `msen/padroes/mesma_linha.py`;
- detector da maior ocupação igual a duas dezenas;
- detector da maior ocupação igual a três dezenas;
- detector da maior ocupação igual a quatro, cinco ou seis dezenas;
- classificação exclusiva, sem exigir sequencialidade;
- validação de quantidade, tipo, limites e repetição;
- funções públicas documentadas em português.

As funções foram exportadas pelo pacote, mas ainda não foram associadas aos
códigos `PD_007`–`PD_009`. Não houve cálculo histórico, persistência nem acesso
ao PostgreSQL.

## Testes

Foram aprovados 38 testes direcionados, abrangendo os 7 testes novos e a
regressão dos detectores de sequências, colunas e da infraestrutura pública de
padrões.
