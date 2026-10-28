# Teste da subetapa 17.5 — API das distribuições

## Verificações

- histograma reconcilia frequência e percentual da amostra;
- curva normal é referência visual e não substitui a distribuição real;
- série constante informa curva normal indisponível;
- contrato HTTP encaminha corte exclusivo, classes, método e margens;
- parâmetros inválidos, janela vazia e geometria incompleta são protegidos;
- a serialização é determinística e mantém o screener inativo.

## Resultado

- 9 testes específicos aprovados.
- 446 testes Python de regressão aprovados.
- Consulta local somente de leitura processou 3.069 resultados, retornou os dez
  parâmetros com dez classes cada e manteve `ativa_no_screener=false`.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Nenhum dado foi gravado e nenhuma regra de exclusão foi ativada.
