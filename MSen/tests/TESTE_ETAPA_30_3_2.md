# Evidência da subetapa 30.3.2 — Adaptação do cadastro de Grupo

Data: 12/11/2026

## Resultado

- a edição direta dentro da antiga grade foi removida;
- o formulário navegável apresenta localização, lista e registro selecionado;
- `Novo registro` inicia uma inclusão sem gravar dados;
- `Salvar registro` abre a confirmação antes da chamada à API;
- edição e cancelamento usam a proteção comum contra perda de alterações;
- exclusão definitiva possui confirmação separada;
- o código `PG_NNN` continua controlado pelo sistema;
- nome e descrição continuam sendo os únicos dados enviados na criação e na
  alteração;
- a API, as consultas e as tabelas do banco não foram modificadas.

## Arquivos principais

- `frontend/grupos-padroes.html`;
- `frontend/css/grupos-padroes.css`;
- `frontend/js/grupos-padroes.js`;
- `frontend/js/grupos-padroes-api.js`;
- `frontend/tests/grupos_padroes_api.test.mjs`.

## Validação

- tradução de listagem, criação, alteração e exclusão aprovada;
- localização parcial pelo nome e paginação aprovadas;
- preservação da mensagem de conflito aprovada;
- compatibilidade com Gestão do desenvolvimento aprovada;
- 120 testes unitários do frontend aprovados.

A validação do fluxo completo no navegador e das proteções do banco pertence à
subetapa 30.3.3.
