# Evidência da subetapa 23.11 — Proteção operacional

## Resultado

O backtest da página Seleção de dezenas passou a exigir prévia e confirmação
antes do processamento. O andamento usa o componente compartilhado já adotado
pelo sistema, evitando uma segunda implementação de modal.

## Prévia obrigatória

Antes de iniciar, o formulário informa:

- quantidade e período dos resultados disponíveis;
- concurso inicial e final do backtest;
- quantidade de concursos que serão processados;
- fatores `k` e `j` e modo de quantidade;
- operação que será executada e preservada.

Cancelar ou fechar a prévia não inicia o endpoint de execução.

## Andamento e cancelamento

Durante o backtest são apresentados:

- estado e etapa atual;
- quantidade concluída e total;
- percentual real;
- duração transcorrida;
- cancelamento em ponto seguro.

O modal não pode ser fechado enquanto a tarefa estiver ativa. Ao terminar, o
resultado persistido é carregado na página para consulta e comparação.

## Execução duplicada

A interface recusa nova solicitação enquanto seu modal está executando. A API
mantém uma segunda barreira no `GerenciadorBacktestsSelecao`, que aceita somente
uma execução ativa e responde `EXECUCAO_EM_ANDAMENTO` às duplicadas.

## Gravações extensas

A formação de jogos continua precedida pela contagem combinatória e confirmação.
Volumes elevados exigem uma segunda confirmação específica.

## Testes

- navegador automatizado da página: **2 aprovados**;
- frontend: **86 aprovados**;
- backend Python: **674 aprovados**;
- falhas: **0**.

Nenhum servidor foi iniciado, nenhuma porta foi aberta e nenhum commit ou push
foi realizado nesta subetapa.
