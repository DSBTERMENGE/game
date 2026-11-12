# Contrato do CRUD interno reutilizável do Game

Data do contrato: 11/11/2026.

## Finalidade

O Game terá um mecanismo comum para cadastros, começando pela Gestão do
desenvolvimento. O componente reutiliza comportamento de interface, não acesso
genérico ao banco. Cada área continuará possuindo API, serviço, repositório e
regras próprios.

O contrato substitui dois padrões que têm causado confusão:

- formulários de inclusão misturados com tabelas permanentemente editáveis;
- repetição de lógica de carregamento, mensagens, bloqueio e gravação em cada
  página.

Não fazem parte deste contrato nomes de tabelas enviados pelo navegador, SQL
recebido da interface, geração automática de endpoints ou dependência do CRUD
do FinCtl.

## Identidade e numeração

O identificador do banco é técnico, não é posição nem quantidade de registros.
Sequências PostgreSQL podem apresentar intervalos depois de transações
canceladas ou recusadas; isso não representa linha vazia nem perda de dados.

O CRUD obedecerá às seguintes regras:

1. abrir, preencher ou cancelar um formulário não chama a API de criação;
2. o `POST` ocorre somente depois da conferência e confirmação do usuário;
3. o comando fica bloqueado enquanto a requisição estiver em andamento;
4. uma chave de idempotência impede duplicação por repetição da mesma
   solicitação;
5. identificadores técnicos não são usados como numeração visual;
6. listas mostram título ou código semântico e, quando necessário, uma posição
   calculada apenas para exibição.

Essas regras evitam registros acidentais, mas não prometem sequências técnicas
sem intervalos.

## Componente por instância

Cada CRUD possuirá estado próprio. Não haverá variáveis globais compartilhadas
entre cadastros. Uma instância recebe:

- elemento raiz;
- título e descrição;
- definição dos campos em objetos independentes;
- colunas da lista;
- campo principal de pesquisa;
- filtros e ordenações permitidos;
- adaptador de API;
- ações disponíveis para aquele cadastro.

Exemplo conceitual:

```javascript
criarCrudNavegavel({
  raiz,
  pesquisa: { campo: "titulo", rotulo: "Pesquisar pelo título" },
  campos: [
    { nome: "titulo", rotulo: "Título", tipo: "texto", obrigatorio: true },
    { nome: "descricao", rotulo: "Descrição", tipo: "texto-longo", obrigatorio: true }
  ],
  api: { listar, consultar, criar, atualizar, arquivar }
});
```

Cada campo reúne suas propriedades no mesmo objeto. Não serão usados arrays
paralelos de tipos, rótulos, nomes e posições.

## Estados da interface

A instância possui estados explícitos:

- `CARREGANDO_LISTA`;
- `CONSULTA`;
- `NOVO`;
- `EDICAO`;
- `CONFERENCIA`;
- `SALVANDO`;
- `ERRO`.

Somente `NOVO` e `EDICAO` permitem alterar campos. `CONFERENCIA` mostra os
valores que serão enviados, mas ainda não grava. `SALVANDO` bloqueia repetição.

Sair de `NOVO` ou `EDICAO` com alterações exige a escolha entre continuar
editando ou descartar. Fechar a conferência retorna ao formulário sem gravar.

## Lista, pesquisa e navegação

A lista e o formulário são regiões distintas. A lista oferece:

- caixa textual de pesquisa parcial pelo título;
- filtros combináveis;
- ordenação explícita;
- paginação no servidor;
- total encontrado e intervalo exibido;
- estado vazio com orientação;
- abertura por clique ou teclado.

A pesquisa não será uma caixa de seleção contendo todos os registros. O padrão
inicial será 20 itens por página. Alterar busca, filtro ou ordenação retorna à
primeira página.

## Inclusão

O fluxo obrigatório é:

```text
Novo registro → preencher → validar → conferir → confirmar → POST → resposta
```

O servidor repete todas as validações. Em sucesso, a lista é atualizada e o
registro criado é aberto em consulta. Em erro, os dados digitados permanecem no
formulário e a mensagem explica o que precisa ser corrigido.

## Edição e concorrência

O formulário de consulta é protegido. `Editar` cria uma cópia de trabalho. O
salvamento envia a versão lida do registro; se ele tiver sido alterado depois,
o servidor responde conflito e não sobrescreve silenciosamente.

Uma edição sem mudanças não chama a API. Campos técnicos e calculados não são
editáveis.

## Arquivamento

O mecanismo comum não oferecerá exclusão física normal. `Arquivar` exige
confirmação, preserva o registro e o remove das listas ativas. Registros
arquivados podem ser consultados por filtro e desarquivados conforme as regras
da área.

Uma exclusão física futura exigirá contrato e autorização próprios.

## Adaptador de API

O componente conhece somente operações de domínio:

- `listar(consulta)`;
- `consultar(identificador)`;
- `criar(dados, chaveIdempotencia)`;
- `atualizar(identificador, dados, versao)`;
- `arquivar(identificador, versao)`;
- `desarquivar(identificador, versao)`.

Ele não recebe tabela, view, banco ou expressão SQL. Cada módulo traduz as
respostas da sua API para um formato comum de dados, paginação, mensagem e erro.

## Mensagens e acessibilidade

- Mensagens informam ação, resultado e próxima providência.
- Erros técnicos não são apresentados como orientação ao usuário.
- Estados usam `aria-live` sem depender somente de cor.
- Modais mantêm foco, aceitam Escape como cancelamento sem gravação e devolvem
  o foco ao comando de origem.
- Todos os comandos têm texto ou nome acessível.

## Limite da reutilização inicial

A Gestão do desenvolvimento será o piloto. Configurações, grupos, subgrupos e
padrões não serão migrados automaticamente. Cada migração futura terá auditoria,
autorização e teste de não regressão próprios.

## Primeira reutilização validada

Na etapa 27.7, a inclusão de configurações da Seleção de dezenas passou a usar
o fluxo comum de gravação confirmada. Como essas configurações são imutáveis,
não foram incorporadas edição ou arquivamento. A reutilização ficou restrita à
validação, conferência, confirmação, cancelamento sem POST, proteção contra
repetição e recuperação após falha. A análise da configuração permanece uma
operação específica da Seleção de dezenas.

## Localização dos registros

O campo comum chama-se `Localizar`. Ele oferece os títulos disponíveis e
também aceita texto livre, enviado como busca parcial por `contém`. Ao carregar
uma consulta, o primeiro resultado é apresentado automaticamente; uma
correspondência exata de título é escolhida primeiro.

Filtros e ordenação ficam na mesma linha em telas largas. `Consultar
arquivados` troca a lista ativa pela lista arquivada; não representa arquivos
externos.

Os campos de formulário podem declarar largura `curta`, `média`, `larga` ou
`total`. Campos de catálogo e valores breves não devem herdar automaticamente
a largura dos títulos, descrições e demais textos longos. Em telas estreitas,
todos retornam a uma coluna para preservar a leitura.
