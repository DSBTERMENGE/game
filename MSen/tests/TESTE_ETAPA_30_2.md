# Evidência da Etapa 30.2 — Estrutura reutilizável do CRUD

Data: 12/11/2026

## Diagnóstico

O Game já possui uma base reutilizável em `frontend/js/crud-navegavel.js`. Ela
controla consulta, novo registro, edição, conferência antes da gravação,
cancelamento com proteção contra perda de dados e mensagens de erro.

Essa base ainda não pode ser aplicada diretamente a Grupo e Subgrupo porque:

- exige operações de arquivar e desarquivar em todos os adaptadores;
- pressupõe que todos os registros tenham um título para localização;
- sempre apresenta controles de arquivamento;
- não possui exclusão definitiva configurável;
- não distingue campos editáveis de dados calculados exibidos somente para
  consulta;
- contém opções de ordenação próprias do primeiro módulo que a utilizou.

Os cadastros atuais de Grupo e Subgrupo repetem funções de requisição,
carregamento, mensagem, criação de campos e tratamento de ações. Além disso,
editam os registros diretamente dentro da grade, sem a sequência uniforme de
consulta, edição, confirmação e gravação.

## Estrutura aprovada para a migração

O componente comum será evoluído por capacidades opcionais, sem criar um
segundo motor CRUD:

1. `listar`, `criar` e `atualizar` permanecem como operações básicas;
2. `excluir`, `arquivar` e `desarquivar` serão opcionais e mutuamente adequadas
   à regra de cada cadastro;
3. pesquisa, paginação, filtros e ordenação poderão ser ativados ou ocultados
   pela configuração;
4. o campo usado para localizar e identificar uma linha será configurável, sem
   exigir o nome `titulo`;
5. campos poderão ser editáveis, protegidos ou calculados;
6. gravações usarão modal de confirmação e validação antes da chamada à API;
7. cancelamento de edição preservará a confirmação contra perda de alterações;
8. mensagens serão apresentadas em linguagem operacional, sem expor detalhes
   internos do banco de dados.

## Regras de Grupo que devem permanecer

- o código `PG_NNN` e o identificador são gerados e protegidos pelo sistema;
- nome e descrição são obrigatórios;
- nomes repetidos são recusados;
- somente nome e descrição podem ser alterados;
- a exclusão é definitiva, exige confirmação e é recusada quando o grupo possui
  Subgrupos dependentes.

## Regras de Subgrupo que devem permanecer

- o código `PD_NNN`, identificadores e valores estatísticos são protegidos;
- Grupo, nome e descrição são obrigatórios e editáveis;
- nomes repetidos são recusados;
- a troca de Grupo continua permitida;
- o filtro por Grupo continua disponível;
- ocorrências, intervalo médio, desvio-padrão e situação da função Python são
  apresentados somente para leitura;
- a consulta do perfil histórico continua sendo uma ferramenta independente do
  formulário CRUD e não será incorporada ao salvamento do Subgrupo.

## Proteção da implementação

As etapas seguintes deverão conservar a aprovação destes conjuntos:

- testes da API de Grupos;
- testes da API de Subgrupos;
- testes unitários do componente CRUD;
- fluxo Chromium de criar, editar e excluir Grupo;
- fluxo Chromium de filtrar, criar, transferir e excluir Subgrupo;
- conferência de que valores estatísticos não são enviados como campos
  editáveis.

Nenhuma API, tabela, consulta ou regra de negócio foi alterada nesta etapa.
