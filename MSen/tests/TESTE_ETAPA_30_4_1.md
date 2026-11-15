# Evidência da subetapa 30.4.1 — Consulta dependente Grupo → Padrão

Data: 12/11/2026

## Comportamento conferido

- um filtro pode ser configurado como obrigatório no CRUD comum;
- sem Grupo escolhido, nenhuma consulta de Padrões é enviada;
- a interface orienta o usuário a escolher o Grupo;
- ao escolher o Grupo, `grupo_cod` integra a consulta;
- a localização não sugere Padrões antes da escolha do Grupo;
- o cadastro de Grupo continua funcionando sem filtro obrigatório;
- a página atual de Padrões não foi modificada nesta subetapa.

## Resultados

- 123 testes unitários do frontend aprovados;
- fluxo Playwright específico do cadastro de Grupo aprovado em porta isolada;
- nenhum registro do banco real foi criado, alterado ou excluído.
