# Evidência da Etapa 25.5.1 — correção do acesso ao relatório gráfico

Data: 09/11/2026.

## Falha observada

O processo persistente aceitava `Concurso final` vazio e adotava o último
resultado cadastrado, mas o relatório temporário rejeitava o mesmo campo vazio.
A mensagem aparecia somente no início da página e, com a rolagem posicionada no
bloco Backtest, o clique parecia não produzir efeito.

## Correções

- a prévia temporária aceita o concurso final vazio;
- a API resolve o valor vazio para o último concurso cadastrado;
- o valor resolvido é colocado no campo e apresentado na prévia antes do cálculo;
- estado e erros são informados no próprio bloco Backtest;
- o comando antigo passou a se chamar `Executar e gravar backtest`;
- a prévia antiga informa explicitamente a gravação e oferece os comandos
  `Cancelar — não gravar` e `Confirmar e gravar backtest`;
- a Ajuda diferencia os dois processos e explica o concurso final automático;
- a Execução 1 existente não foi alterada nem removida.

## Validação

- 89 testes de frontend aprovados;
- 19 testes da API aprovados, incluindo concurso final omitido;
- 5 testes Playwright aprovados;
- o teste de navegador deixa o campo final vazio, recebe o último concurso da
  prévia, preenche o campo e conclui a exibição dos gráficos;
- validação HTTP integrada processou 2.570 pontos em aproximadamente 3,29
  segundos, confirmou cancelamento e descarte e manteve as cardinalidades do
  PostgreSQL inalteradas.

## Conclusão

O relatório temporário agora mantém a mesma convenção de período usada pelo
processo anterior, mas continua sem persistir seus resultados.
