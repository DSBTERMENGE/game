# Evidência da subetapa 30.5.2 — Validação final da etapa 30

Data: 12/11/2026

## Cobertura final

- navegação direta pelo submenu Cadastros;
- CRUD de Grupo com pesquisa, seleção e confirmações;
- escolha obrigatória do Grupo no cadastro de Padrões;
- filtragem dos Padrões conforme o Grupo;
- criação e alteração preservando `id_grupo`;
- exclusão confirmada;
- ausência de estatísticas no formulário de cadastro;
- comportamento com muitos registros;
- conteúdo atualizado da Ajuda.

## Resultados

- 126 testes unitários do frontend aprovados;
- 34 testes Python de API e repositório aprovados;
- 5 fluxos Playwright de navegação e cadastros aprovados;
- 1 fluxo Playwright integrado aprovado com aplicação Flask e PostgreSQL
  temporário;
- banco temporário removido ao final;
- banco efetivo do Game não recebeu gravações.

Durante a repetição do teste integrado, as esperas das requisições de criação,
alteração e exclusão foram explicitadas para impedir consultas antes do término
da operação. Essa correção pertence somente à sincronização do teste.
