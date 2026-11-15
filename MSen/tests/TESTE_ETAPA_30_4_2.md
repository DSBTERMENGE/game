# Evidência da subetapa 30.4.2 — Cadastro de Padrões

Data: 12/11/2026

## Comportamento conferido

- o Grupo deve ser escolhido antes de consultar ou criar Padrões;
- a caixa de Padrões contém somente registros do Grupo selecionado;
- mudar o Grupo atualiza imediatamente a caixa de Padrões;
- a criação envia o `grupo_cod` escolhido;
- a alteração preserva o vínculo com o Grupo escolhido;
- o formulário apresenta Nome do padrão e Descrição;
- estatísticas e perfil histórico não aparecem no cadastro;
- inclusão, edição e exclusão usam confirmação.

## Resultados

- 125 testes unitários do frontend aprovados;
- três fluxos Playwright específicos aprovados em porta isolada;
- nenhum registro do banco real foi criado, alterado ou excluído.
