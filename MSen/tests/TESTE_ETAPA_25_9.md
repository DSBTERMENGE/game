# Teste da etapa 25.9

## Alterações verificadas

- interface, Ajuda e mensagens utilizam somente `Backtest`;
- Ajuda explica finalidade, configuração, comando e relatório em quatro partes;
- referências à transição foram retiradas da documentação vigente;
- código e API usam nomes definitivos e rotas `/backtests`;
- relatório continua explicitando que seus resultados não são gravados;
- cancelamento, fechamento e indisponibilidade apresentam orientação ao usuário.

## Validação

- 689 testes Python aprovados;
- 89 testes unitários do frontend aprovados;
- 5 testes Playwright da página aprovados;
- 2 testes no navegador contra a aplicação e o PostgreSQL reais aprovados;
- período completo de 500 a 3.069 e início personalizado em 2.500 validados;
- nenhum resultado derivado do Backtest foi gravado.

## Resultado

A terminologia de transição deixou de fazer parte do produto. Para o usuário e
para o código vigente, o módulo chama-se somente `Backtest`.
