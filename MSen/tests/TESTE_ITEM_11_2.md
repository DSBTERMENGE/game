# Evidência do Item 11.2 — detectores de mesma coluna

Data: 2026-10-27.

## Implementação

- módulo puro `msen/padroes/mesma_coluna.py`;
- três detectores exclusivos pela maior sequência vertical subjacente;
- validação de quantidade, tipo, limites e repetição;
- funções públicas documentadas em português.

As funções foram exportadas pelo pacote, mas ainda não foram associadas aos
códigos `PD_004`–`PD_006`. Não houve cálculo histórico, persistência nem acesso
ao PostgreSQL.

## Testes

Com `PYTHONPATH=src`, foram executados os testes de mesma coluna e a regressão
dos padrões sequenciais. Resultado: 18 testes aprovados, incluindo 6 testes
novos e 12 testes de regressão.

A tentativa inicial sem `PYTHONPATH=src` não localizou o pacote `msen`; o
comando foi corrigido e a suíte passou integralmente.

No Item 11.6, os detectores foram corrigidos após o esclarecimento sobre linhas
subjacentes e novamente validados pela regressão completa.
