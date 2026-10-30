# Evidência — subetapa 20.14

Data: 2026-10-30.

## Resultado

- `GET /api/validacao/relatorio` fecha as verificações por função em
  exigidas, executadas, aprovadas, divergentes e pendentes.
- O estado do catálogo distingue função atual, implementação alterada,
  referência pendente e critério novo/regra alterada.
- A resposta terminal do motor informa inclusões, exclusões, mudanças de
  implementação/regra e quantidade de avaliações criadas na atualização.
- Cada `N` apresenta combinação, função/filtro, categoria, grupo/subgrupo,
  esperado, calculado, diferença e assinaturas atual e executada.
- A hipótese diagnóstica é somente informativa: não escreve no gabarito, na
  função nem no campo de aprovação.

## Conferência no banco `games`

- 19 critérios ativos.
- 3.800 verificações exigidas e executadas.
- 3.800 aprovações `S`, zero divergências `N` e zero pendências.
- Fechamento válido: `3.800 = 3.800 + 0 + 0`.

## Testes

- 559 testes Python: aprovados.
- 37 testes Node: aprovados.
- 2 fluxos Chromium, incluindo relatório divergente simulado nas larguras
  normal e estreita: aprovados.
- A verificação local seguiu a skill Sites; nada foi publicado.

Próxima subetapa: 20.15, somente após autorização específica.
