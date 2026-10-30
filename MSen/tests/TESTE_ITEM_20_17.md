# Evidência — subetapa 20.17

Data: 2026-10-30.

## Documentos reconciliados

- `docs/funcionamento.md`: fluxo vigente completo.
- `PLANO_DO_PROJETO.md`: visão atual, capacidades e limites.
- `docs/INDICE_DOCUMENTACAO.md`: precedência e documentos históricos.
- `docs/CONTRATO_HOMOLOGACAO_FUNCOES.md`: estado implementado.
- `docs/API_VALIDACAO.md`: quadro, relatório, exportação e tarefa assíncrona.
- `docs/visao-geral.md`, `docs/arquitetura.md` e `docs/codigo-python.md`.
- `notas/decisoes.md` e `notas/funcionalidades.md`.

## Histórico preservado sem ambiguidade

- `docs/funcionamento_historico_ate_etapa_19.md`.
- `docs/PLANO_DO_PROJETO_HISTORICO.md`.
- Contratos antigos do Screener e da classificação receberam avisos de contexto.
- A classificação histórica não grava `SEM_CORRESPONDENCIA`; a matriz de
  validação pode usar esse estado para classificador executado sem subgrupo.

## Conferência automática

`test_documentacao_20_17.py` confirmou:

- existência dos documentos canônicos e históricos;
- correspondência das rotas documentadas com o código Flask;
- correspondência das tabelas documentadas com o esquema consolidado;
- ausência, nos documentos vigentes, das afirmações revogadas selecionadas.

## Regressão final

- Python: 571 testes aprovados.
- Node: 37 testes aprovados.
- Chromium: 20 fluxos aprovados.
- `git diff --check`: sem erro.

Nenhum commit, push ou publicação externa foi executado.
