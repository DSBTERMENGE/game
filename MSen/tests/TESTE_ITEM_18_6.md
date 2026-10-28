# Evidência de teste — subetapa 18.6

Data: 28/10/2026

## Escopo

Quadro contábil consolidado e serializável das três famílias, ainda sem conexão
com API ou interface.

## Verificações

- entrada, exclusões líquidas e saldo das três famílias;
- entrada, avaliações, exclusões e saldo de cada filtro;
- percentuais sobre total inicial e saldo recebido;
- distinção entre universo e amostra processada;
- fechamento final obrigatório;
- serialização adequada para JSON;
- recusa de saldo, percentual ou estrutura de famílias adulterados;
- bloqueio do modo integral para uma amostra incompleta;
- amostra vazia sem divisão por zero.

## Resultado

- Testes específicos: **7 aprovados**.
- Regressão Python: **486 testes aprovados**.
- Os `ResourceWarning` preexistentes na leitura de três arquivos do frontend não
  causaram falha e não pertencem ao quadro consolidado.
