# Evidência da subetapa 30.3.4 — Organização do cadastro de Grupo

Data: 12/11/2026

## Organização conferida

- a lista de Grupos aparece antes do formulário;
- as linhas da lista possuem altura inferior a 40 pixels;
- a paginação permanece logo abaixo da lista;
- o botão `Novo registro` aparece abaixo da lista e alinhado à esquerda;
- o formulário aparece abaixo do botão, sem divisão lateral;
- mensagens de falha usam apresentação discreta e compreensível;
- mensagens técnicas de JavaScript não são expostas ao usuário.

## Resultados

- 122 testes unitários do frontend aprovados;
- fluxo Playwright específico do cadastro de Grupo aprovado;
- `git diff --check` aprovado;
- nenhum registro do banco real foi criado, alterado ou excluído.

A tentativa de executar toda a suíte Playwright encontrou a porta 4173 já
ocupada por outro servidor. Os casos interrompidos registraram `EADDRINUSE`;
essa ocorrência é ambiental e não indica falha no cadastro de Grupo.
