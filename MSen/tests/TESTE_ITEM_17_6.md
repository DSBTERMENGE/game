# Teste da subetapa 17.6 — painel com todos os gráficos

## Escopo visual

- dez cartões simultâneos em grade compacta;
- histograma observado, curva normal de referência, média e faixa;
- resumo da janela histórica e das margens;
- rolagem interna sem crescimento vertical ilimitado;
- uma coluna em telas estreitas, duas em telas comuns e três em telas largas;
- aviso permanente de que o screener está inativo.

## Verificações

- teste estrutural de HTML, CSS e JavaScript;
- dados simulados com dez parâmetros e dez classes;
- Google Chrome nas larguras de 1.280 e 760 pixels;
- contenção horizontal e vertical e existência da rolagem interna;
- regressões JavaScript, Python e fluxos existentes do Chrome.

## Resultado

- 25 testes JavaScript aprovados.
- 3 testes específicos no Google Chrome aprovados.
- 15 testes completos no Google Chrome aprovados, incluindo os fluxos antigos.
- 446 testes Python de regressão aprovados.
- A grade ficou contida em 1.280 e 760 pixels e apresentou rolagem interna.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Nenhuma regra de exclusão foi ativada e nenhum dado foi gravado.
