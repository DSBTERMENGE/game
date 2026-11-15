# Teste da subetapa 29.5.5 — validação limitada e estimativa

Data: 11/11/2026

## Escopo

O motor e os filtros reais foram executados sobre os primeiros 10.000, 20.000
e 50.000 itens do iterador integral. O limitador existe somente no roteiro de
validação `validar_etapa_29_5_5.py`; a aplicação continua configurada para o
universo oficial de 50.063.860 combinações.

## Resultados progressivos

| Volume | Duração | Taxa | Fechamento |
| ---: | ---: | ---: | :---: |
| 10.000 | 0,563 s | 17.765,9/s | correto |
| 20.000 | 0,757 s | 26.421,2/s | correto |
| 50.000 | 2,941 s | 17.000,6/s | correto |

Nos três limites, `analisadas = excluídas + aprovadas`. Nesse prefixo
lexicográfico todas foram excluídas pelos filtros; isso não representa a
proporção esperada no universo inteiro e explica a velocidade elevada, pois a
reprovação antecipada evita os filtros posteriores.

## Memória, progresso e cancelamento

- memória residente inicial: 62,93 MiB;
- memória após o aquecimento: aproximadamente 71 MiB;
- pico observado do processo: 72,15 MiB;
- entre 20.000 e 50.000 itens não houve crescimento proporcional ao volume;
- o progresso chegou exatamente ao total de cada ensaio;
- o pedido de cancelamento feito após 10.000 itens foi reconhecido no ponto
  seguro seguinte em 1,228 s, sem produzir resultado parcial.

## Estimativa

A taxa média dos prefixos produziria um melhor caso de aproximadamente 0,68
hora. Esse valor é otimista porque o prefixo foi integralmente rejeitado cedo.
Usando como referência conservadora a amostra real anterior — 5.000 itens em
4,343 segundos e com passagem por mais filtros — a projeção é de cerca de
12,08 horas. Assim, a execução integral deve ser tratada como operação de longa
duração; a medição real será feita somente na subetapa 29.5.6 autorizada.

## Regressão

Foram executados 36 testes do servidor, do contrato do funil e dos geradores,
todos aprovados. Permanecem apenas avisos preexistentes de arquivos estáticos
abertos durante testes da API.

As 50.063.860 combinações não foram executadas nesta subetapa.
