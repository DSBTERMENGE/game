# Teste da subetapa 29.6.3 — validação final controlada

Data: 12/11/2026

## Processamento limitado

O mesmo motor e os filtros reais foram exercitados em limites controlados de
10.000, 20.000 e 50.000 combinações. Nos três casos:

- o progresso chegou ao total informado;
- `analisadas = excluídas + aprovadas`;
- o quadro foi marcado como reconciliado;
- a memória permaneceu estável após o aquecimento.

O cancelamento solicitado depois de 10.000 itens foi reconhecido no ponto
seguro seguinte e não devolveu resultado parcial.

## Testes automatizados

- 41 testes Python do servidor, homologação, contratos, funil e geradores;
- 115 testes unitários do frontend;
- 7 cenários Chromium do Screener.

Todos foram aprovados. Os cenários cobriram confirmação, desistência antes de
iniciar, envio do comando, progresso, conclusão simulada, falha, bloqueio por
validação, cancelamento confirmado e descarte do resultado parcial.

## Limite desta validação

A aplicação integral permaneceu disponível e conectada ao mesmo motor. A
validação utilizou simulações e volumes limitados; não foi necessário percorrer
as 50.063.860 combinações para conferir o contrato da interface e do servidor.
