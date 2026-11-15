# Evidência da Etapa 30.1 — Navegação direta dos Cadastros

Data: 12/11/2026

## Escopo validado

- o submenu `Cadastros` aparece acima do corpo da página e não é recortado;
- `Grupo` abre diretamente o formulário de grupos;
- `Subgrupo` abre diretamente o formulário de subgrupos;
- os mesmos dois acessos estão disponíveis em todas as páginas do menu;
- a página intermediária antiga não apresenta mais os dois botões e redireciona
  para Grupo;
- formulários, APIs e regras de negócio de Grupo e Subgrupo não foram alterados.

## Testes executados

- `npm run test:frontend`: 115 testes aprovados;
- `npx playwright test frontend/tests/browser/fluxos_principais.spec.mjs`:
  11 fluxos Chromium aprovados;
- o fluxo de navegação confirmou também que o submenu ultrapassa a barra do
  menu sem ser ocultado pelo conteúdo.

## Resultado

A etapa 30.1 foi concluída. A próxima atividade planejada é a etapa 30.2,
dependente de autorização específica.
