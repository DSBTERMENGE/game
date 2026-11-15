# Evidência da subetapa 30.3.3 — Validação do cadastro de Grupo

Data: 12/11/2026

## Falha relatada e correção

Ao abrir o formulário, ainda não existe registro selecionado. A função
configurada para identificar um Grupo tentou acessar `grupo_cod` nesse valor
nulo, interrompeu o carregamento e deixou a lista vazia.

O controlador passou a chamar a identificação somente depois que uma seleção
existir. Foi acrescentado um teste que abre o controlador com identificador
próprio e confirma que o primeiro registro é carregado normalmente.

## Fluxos conferidos

- carregamento da lista existente;
- localização e paginação;
- abertura de novo registro sem gravação antecipada;
- confirmação antes da criação e da alteração;
- validação dos campos obrigatórios depois da confirmação;
- preservação do rascunho quando ocorre falha;
- criação e alteração usando somente nome e descrição;
- confirmação antes da exclusão definitiva;
- exclusão de Grupo sem dependências;
- recusa da exclusão de Grupo que possui Subgrupos;
- proteção do código automático;
- comportamento em janela estreita.

## Resultados

- 11 testes da API de Grupo aprovados com `unittest`;
- 121 testes unitários do frontend aprovados;
- 11 fluxos principais em Chromium aprovados;
- nenhum registro criado, alterado ou excluído no banco real durante os testes.
