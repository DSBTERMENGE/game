# Evidências do Item 10.13 — regressão completa da Etapa 10

Data: 2026-10-27.

## Suítes aprovadas

- 193 testes Python;
- 22 testes de frontend;
- 8 fluxos isolados no Google Chrome;
- 3 fluxos integrados Google Chrome/PostgreSQL.

## Migrações

O caminho normal partiu das versões `001`–`003` com seis padrões, aplicou `004`
e confirmou dois grupos, seis padrões, textos, estatísticas, restrições e
sequências preservados.

Um segundo database recebeu `PD_007` sem classificação aprovada. A migração
falhou como esperado e a transação foi integralmente revertida: somente a tabela
`padroes`, as versões `001`–`003` e os sete registros anteriores permaneceram.

O esquema canônico foi executado do zero, criando dois grupos e três padrões
iniciais. Todos os databases temporários foram removidos.

## Ambiente local

- `games`: 3.069 resultados, 60 frequências, 2 grupos e 6 padrões;
- associações: 3 padrões em `PG_001` e 3 em `PG_002`;
- servidor: `http://127.0.0.1:5050/`, PID 23176;
- backup pré-migração preservado e ignorado pelo Git;
- `git diff --check`: sem erros;
- PythonAnywhere: não acessado.

Estado final: Etapa 10 concluída localmente, sem pendência crítica conhecida no
escopo implementado.
