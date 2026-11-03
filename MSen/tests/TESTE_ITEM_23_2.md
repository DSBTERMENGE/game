# Evidência — subetapa 23.2

Data: 03/11/2026

## Objetivo

Definir a escolha da quantidade de dezenas, o custo combinatório e a separação
entre o screener de dezenas e o screener de combinações.

## Decisões verificadas

- seleção de dezenas baseada exclusivamente em ocorrências `SIMPLES`;
- 2VS e 3VS reservados ao screener das combinações;
- uso de todas as aprovadas, escolha manual ou quantidade automática;
- classificação por distância normalizada ao centro ajustado;
- redução pelas melhores aprovadas quando houver excesso;
- complementação pelas melhores não aprovadas quando houver falta;
- identificação explícita de complementares fora da faixa;
- contagem completa de jogos por `C(N,6)`;
- separação entre todas as combinações e lotes limitados;
- medição posterior do efeito dos filtros sobre os jogos.

## Casos manuais

O contrato cobre redução de 15 para 8 dezenas, complementação de 5 para 8,
custos de 8 e 10 dezenas e aplicação posterior do screener sobre 210
combinações brutas de 10 dezenas.

## Resultado

Subetapa 23.2 concluída no nível contratual. Não foram criados screeners,
tabelas, migrações, APIs ou páginas.
