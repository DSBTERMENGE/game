# Teste da subetapa 18.0 — protótipo visual do novo screener

## Escopo

- página separada e identificada como esboço fictício;
- três níveis compactos e expansíveis;
- totais, percentuais e saldos reconciliados;
- detalhes de filtros e política de raridade;
- nenhuma API, banco ou regra real alterada.

## Resultado

- 33 testes JavaScript aprovados.
- 17 fluxos completos no Google Chrome aprovados.
- O protótipo abriu três níveis e doze filtros, reconciliou a contabilidade e
  não realizou nenhuma requisição de API.
- 446 testes Python de regressão aprovados.
- A página real respondeu HTTP 200 na porta 5050 e declarou o esboço fictício.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Banco, API e execução atual do screener permaneceram inalterados.
