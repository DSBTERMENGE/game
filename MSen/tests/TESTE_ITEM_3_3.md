# Teste do Item 3.3 — cálculo das linhas importadas

Data: 2026-10-26.

## Resultado

- seis testes específicos aprovados;
- 70 testes acumulados aprovados;
- linha importada idêntica à inclusão manual equivalente;
- todas as linhas da planilha controlada calculadas;
- campos originais e ordem das dezenas preservados;
- soma, média, mediana, desvio-padrão e coordenadas produzidos com as precisões
  aprovadas;
- versão do cálculo armazenada como `1`;
- planilha de entrada preservada após o processamento;
- função de composição rejeita objetos que não sejam `ResultadoEntrada`.

## Conferência independente

Na primeira execução, o teste continha expectativas manuais incorretas para o
desvio-padrão e as coordenadas da sequência `1, 10, 20, 30, 40, 60`. O desvio
foi conferido independentemente com `statistics.pstdev` e com cálculo decimal da
variância populacional. As coordenadas foram conferidas pelas seis posições da
matriz. Somente as expectativas do teste foram corrigidas; as funções aprovadas
na Etapa 2 não foram alteradas.

Valores confirmados:

- soma: `161`;
- média aritmética: `26.833333`;
- mediana: `25.0`;
- desvio-padrão populacional: `19.497151`;
- média X: `7.500000`;
- média Y: `1.833333`.

O Item 3.3 não compara com registros existentes e não grava no PostgreSQL.
