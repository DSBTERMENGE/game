# Evidências do Item 10.10 — grade de padrões por grupo

Data: 2026-10-27.

## Implementação

A página `/padroes.html` recebeu a grade CRUD de padrões. O grupo é obrigatório
na inclusão e pode ser alterado na própria linha. A página oferece filtro por
grupo e consulta as APIs de grupos e padrões separadamente.

Para aproveitar o espaço:

- inclusão ocupa uma barra horizontal;
- filtro e mensagem compartilham uma segunda linha curta;
- a grade ocupa todo o espaço restante;
- cabeçalho é fixo e as rolagens ficam dentro da grade;
- ocorrência usa 5,5 rem;
- nome usa 17 rem e descrição 24 rem;
- grupo, nome e descrição possuem campos com a mesma altura;
- estatísticas e disponibilidade da função Python são somente leitura.

## Testes

- 22 testes de frontend: aprovados;
- 6 fluxos completos no Google Chrome: aprovados;
- inclusão com grupo obrigatório, filtro e transferência entre grupos: aprovados;
- estatísticas permaneceram somente para leitura;
- exclusão confirmada: aprovada;
- Painel, navegação e grade de grupos permaneceram funcionais;
- PostgreSQL não foi acessado.

Um primeiro ensaio do fluxo Chrome revelou que a massa simulada não continha
`PG_002`. A massa foi corrigida e o fluxo passou; não houve defeito na aplicação.
