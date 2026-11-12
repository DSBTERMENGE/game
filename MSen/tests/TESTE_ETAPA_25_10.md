# Teste da etapa 25.10

## Alterações verificadas

- o primeiro clique em `Salvar configuração` abre a conferência sem fazer POST;
- cancelar não cria configuração e confirmar produz exatamente uma gravação;
- nomes repetidos são recusados pela interface, pelo repositório e pelo banco;
- a migração 025 cria o índice exclusivo sobre `LOWER(BTRIM(nome))`;
- nomes são exibidos sem os identificadores internos nas duas listas e em todo
  o fluxo do Backtest;
- a Ajuda explica confirmação, cancelamento e exclusividade do nome.

## Validação

- 691 testes Python aprovados;
- 89 testes unitários do frontend aprovados;
- 7 testes Playwright da página aprovados;
- migração 025 aplicada no banco Games sem apagar ou renumerar registros;
- tentativa real de repetir um nome recusada com
  `NOME_CONFIGURACAO_EXISTENTE`;
- sequência interna permaneceu em 5 antes e depois da tentativa recusada.

## Resultado

O banco só é chamado após confirmação explícita. O nome tornou-se a identidade
visível da configuração, enquanto o número permanece exclusivamente como chave
técnica para preservar os vínculos existentes.
