# Evidência do Item 11.1 — contrato de dezenas na mesma coluna

Data: 2026-10-27.

## Escopo concluído

- matriz de seis linhas e dez colunas formalizada;
- fórmula de identificação da coluna definida;
- classificação exclusiva de `PD_004`, `PD_005` e `PD_006` definida pela maior
  sequência vertical em linhas subjacentes;
- vários grupos iguais contam uma única ocorrência por resultado;
- comportamento estatístico mantido compatível com os padrões sequenciais;
- casos válidos, limites e entradas inválidas relacionados para os testes.

## Conferência documental

O contrato foi comparado com os códigos e nomes já cadastrados no PostgreSQL e
com a regra exclusiva existente para `PD_001`–`PD_003`. Nenhum código Python,
dado, tabela, API ou interface foi alterado nesta subetapa.

Documento: `docs/CONTRATO_PADROES_MESMA_COLUNA.md`.

Correção posterior: no Item 11.6, o usuário esclareceu que estar na mesma coluna
não basta; as linhas precisam ser imediatamente consecutivas. O contrato e os
casos de teste foram corrigidos para refletir essa definição.
