# Teste do Item 4.3 — repositório de resultados

Data: 2026-10-26.

## Testes automatizados

- seis testes específicos aprovados;
- 106 testes acumulados aprovados;
- parâmetros preservam campos originais e derivados;
- retorno das 18 colunas convertido em `ResultadoPersistido`;
- quantidade incorreta de colunas rejeitada;
- conexão que não seja Psycopg rejeitada;
- erro do repositório mantém código e concurso;
- valores `Decimal` não são convertidos em `float`.

## Teste real isolado

Ambiente: cluster PostgreSQL 16.11 temporário, porta 55443, com a migração `001`
aplicada pelo executor do Item 4.2.

Resultados:

- concurso 10 inserido e lido com todos os campos;
- segunda inserção do concurso 10 rejeitada como `RESULTADO_DUPLICADO`;
- inserção do concurso 11 dentro de transação com erro provocado foi totalmente
  revertida;
- concurso 10 editado para `10, 20, 30, 40, 50, 60` e recalculado como soma
  `210`, média `35.000000`, mediana `35.0`, desvio `17.078251`, média X
  `9.000000` e média Y `2.500000`;
- listagem retornou concursos 10 e 12 em ordem crescente;
- atualização do concurso 999 rejeitada como `RESULTADO_NAO_ENCONTRADO`.

## Isolamento

O cluster temporário foi parado e removido. A porta 55443 ficou sem resposta.
Os PostgreSQL persistentes 16 e 18 e o PythonAnywhere não foram alterados. A
planilha real não foi importada.
