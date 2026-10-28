# Teste da subetapa 17.2 — janela histórica

## Escopo

- selecionar todo o histórico ou aplicar corte exclusivo por concurso/data;
- impedir que o próprio resultado e registros futuros entrem no backtest;
- validar cortes inicial, intermediário e final;
- rejeitar entradas ambíguas ou historicamente inconsistentes.

## Casos automatizados

1. histórico completo, recebido fora de ordem;
2. corte antes do primeiro concurso, produzindo janela vazia;
3. corte intermediário, sem o próprio concurso e sem posteriores;
4. corte no último concurso, mantendo somente seus antecessores;
5. corte exclusivo por data;
6. cortes conflitantes e tipos inválidos;
7. concursos duplicados e datas divergentes da ordem dos concursos;
8. coleção ou item de tipo inválido.

## Resultado

- 8 testes específicos aprovados.
- 422 testes Python de regressão aprovados.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Banco, API, interface e regras do screener permaneceram inalterados.
