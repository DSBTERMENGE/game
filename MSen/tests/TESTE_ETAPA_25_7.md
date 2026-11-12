# Teste da etapa 25.7

O backtest em memória passou a ser o único processo de backtest. O processo
persistente anterior foi removido do Python, da API, do JavaScript, do HTML, dos
testes e da documentação, preservando previsão registrada e formação de jogos.

A migração `024_remover_backtest_persistente.sql` removeu uma execução antiga,
2.570 alvos e 154.200 avaliações. Nenhum lote de jogos estava vinculado. As
tabelas compartilhadas permaneceram e agora aceitam somente execuções do tipo
`PREVISAO_FUTURA`.

Verificações: 689 testes Python, 89 testes unitários do frontend e 5 testes
Playwright aprovados; backtest real de 2.570 concursos concluído em memória sem
alterar cardinalidades; auditoria posterior com zero registro de `BACKTEST`.
