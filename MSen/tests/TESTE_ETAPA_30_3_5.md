# Evidência da subetapa 30.3.5 — Consulta padronizada por seleção

Data: 12/11/2026

## Comportamento conferido

- o cadastro de Grupo não exibe mais tabela nem paginação;
- a caixa `Registro` apresenta os nomes disponíveis;
- a escolha de um nome carrega o registro correspondente;
- `Localizar` filtra por parte do nome;
- o contador permanece ao lado da seleção e informa quantos registros foram encontrados;
- o adaptador fornece todos os Grupos encontrados, sem recorte visual por página;
- inclusão, alteração, confirmação e exclusão continuam disponíveis;
- o cadastro de Subgrupo não foi alterado.

## Resultados

- 122 testes unitários do frontend aprovados;
- fluxo Playwright específico do cadastro de Grupo aprovado em porta isolada;
- nenhum registro do banco real foi criado, alterado ou excluído.
