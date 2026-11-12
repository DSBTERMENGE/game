# Evidência da etapa 26.2

Data: 10/11/2026.

## Interface implementada

- título `Formação de jogos com as dezenas registradas`;
- origem com concurso, configuração, dezenas e combinações brutas;
- campos `Número máximo de jogos` e `Valor de um jogo (R$)`;
- valor máximo previsto calculado exatamente em centavos;
- conferência em diálogo antes do futuro processamento;
- comando `Confirmar e iniciar Screener` visível, desabilitado e explicado;
- Ajuda adequada ao estado realmente disponível.

## Proteções verificadas

- escolher a origem faz somente a consulta de prévia;
- conferir não gera combinações;
- conferir não executa o Screener;
- conferir não grava jogos nem configurações;
- a interface não chama mais o POST antigo que persistia todas as combinações;
- solicitar mais jogos que a quantidade bruta não completa artificialmente a
  lista: a redução futura continua explicitada no texto da conferência.

## Testes

- 89 testes unitários do frontend aprovados;
- 8 testes Playwright aprovados;
- o teste do navegador confirmou valor de R$ 5,00 × 100 = R$ 500,00;
- o teste confirmou zero chamadas POST de jogos.

Nenhuma migração ou alteração de dados foi realizada.
