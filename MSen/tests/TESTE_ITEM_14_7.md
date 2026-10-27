# Evidência do Item 14.7 — ensaio integrado de 5.000 combinações

Data: 2026-10-27.

## Fluxo executado

O fluxo carregou a configuração local opcional, validou modo/semente/limite,
gerou 5.000 combinações distintas, passou pelo funil sem filtros e serializou o
quadro. Recebeu 5.000, aprovou 5.000 e produziu zero linhas de exclusão. O tempo
medido somente para o funil vazio foi aproximadamente 0,0003 segundo, usando a
semente `20261027`.

## Proteção dos critérios

O ensaio bloqueia qualquer categoria marcada como ativa. Como nenhuma regra
real de exclusão foi aprovada, a execução filtrada e a comparação da ordem dos
filtros não são aplicáveis ainda. Regras artificiais não foram usadas no ensaio.

## Testes

- 5 testes específicos e 294 testes da regressão Python aprovados.
- Mesma semente reproduziu a amostra; outra semente alterou o ensaio.
- Modo integral e critério real prematuro permaneceram bloqueados.

Nada foi persistido e nenhum banco foi modificado.
