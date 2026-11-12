# Evidência da etapa 27.6

Data: 11/11/2026.

## Entregas

- orientação de retomada de sessão para consultar registros relacionados sem
  confundir memória operacional com autorização de trabalho;
- validação integrada da API e do PostgreSQL dentro de transação revertida;
- cobertura de criação, repetição idempotente, conflito de versão, conclusão,
  reabertura, arquivamento e desarquivamento;
- validação no navegador de cancelamento, conferência, retorno por `Escape`,
  foco e confirmação anterior ao único envio;
- roteiro separado para uma futura publicação local/PythonAnywhere, sem
  executar publicação, commit ou push;
- correção dos nomes `iniciado_em` e `concluido_em` usados pelo repositório,
  alinhando-os à migração 028.

## Validação

- 723 testes Python aprovados;
- 110 testes unitários do frontend aprovados;
- 1 teste Playwright aprovado no Chromium;
- o teste integrado obteve HTTP 201 na criação, HTTP 200 na repetição
  idempotente e HTTP 409 no conflito de versão;
- o histórico integrado preservou, em ordem, `CRIADO`, `STATUS_ALTERADO`,
  `REABERTO`, `ARQUIVADO`, `DESARQUIVADO` e `ARQUIVADO`;
- o banco `games` possuía zero registros de manutenção antes do teste e
  continuou com zero depois do rollback planejado;
- `git diff --check` não apontou erro de conteúdo; apresentou somente avisos de
  conversão futura entre LF e CRLF.

## Limites respeitados

- nenhuma publicação foi executada;
- nenhum commit ou push foi executado;
- a etapa 27.7 não foi iniciada.
