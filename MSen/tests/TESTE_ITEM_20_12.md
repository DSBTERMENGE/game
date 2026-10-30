# Teste da subetapa 20.12 — modal reutilizável de andamento

Data: 30/10/2026

## Estado

**Concluída.** A Validação e auditoria possui execução assíncrona identificada e
modal reutilizável com progresso real.

## Backend

O `GerenciadorExecucoesValidacao` mantém instantâneos protegidos por trava e
permite somente uma execução ativa. Cada execução informa:

- identificador único;
- estado `AGUARDANDO`, `EXECUTANDO`, `CONCLUIDA` ou `FALHOU`;
- etapa atual;
- quantidade concluída e total;
- percentual derivado dessas quantidades;
- duração real em segundos;
- horário inicial e final;
- erro ou resultado consolidado.

Rotas:

- `POST /api/validacao/execucoes`: inicia e retorna HTTP 202;
- `GET /api/validacao/execucoes/<id>`: consulta o instantâneo;
- início concorrente: HTTP 409 `EXECUCAO_EM_ANDAMENTO`;
- identificador ausente: HTTP 404 `EXECUCAO_NAO_ENCONTRADA`.

O motor emite quatro marcos reais: sincronização, estatística, geometria e
padrões, seguidos da consolidação. Exceções ficam consultáveis e não deixam a
trava de execução ativa presa.

## Frontend

O componente `criarModalAndamento` é independente da página consumidora e
recebe funções de início e consulta. Ele mostra etapa, barra, concluído/total,
percentual, duração e erro. O botão e o fechamento por `Esc` permanecem
bloqueados enquanto a tarefa está ativa. Não foi implementado cancelamento
porque o motor ainda não possui ponto seguro de interrupção.

A página reservada `auditoria.html` ganhou somente o botão necessário para
acionar o modal. Grade, filtros e relatório detalhado continuam reservados para
a subetapa 20.13. HTML, CSS e JavaScript permanecem em seus diretórios próprios.

## Testes

- **554 testes Python aprovados**;
- **35 testes Node aprovados**;
- **1 fluxo Chromium aprovado**.

Os testes cobriram sucesso, falha consultável, progresso intermediário de 50%,
conclusão em 100%, duração, identificador ausente, prevenção de execução dupla e
fechamento permitido somente após o término. Permaneceram apenas os três
`ResourceWarning` conhecidos dos testes de frontend e avisos Node preexistentes
sobre módulos sem `type: module`.

## Resultado

A subetapa 20.12 está encerrada. A 20.13 poderá construir a página completa de
Validação e auditoria reutilizando esta API e este modal, mediante autorização
separada.
