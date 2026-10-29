# Teste da subetapa 18-D.2 — Screener oficial

Data: 2026-10-29

## Objetivo

Fazer `/screener.html` abrir diretamente o funil real em três níveis, sem
passagem pelo screener antigo e sem os links transitórios entre telas.

## Alterações

- `/screener.html` recebeu a interface validada do funil em três níveis;
- o título principal passou a ser apenas `Screener`;
- a barra identifica a estrutura como `Funil em três níveis`;
- foram retirados dessa página os links `Abrir novo funil` e `Screener atual`;
- limite de raridade, execução protegida de 5.000, resumo, famílias, detalhes,
  comparação e reconciliação foram preservados;
- a validação humana provisória não aparece mais na página oficial;
- testes de interface e integração passaram a acessar `/screener.html`.

Os arquivos e a API legados ainda não foram removidos nesta subetapa. Sua
retirada segura continua reservada para 18-D.5 e 18-D.6.

## Testes

- 7 testes direcionados da API aprovados;
- 35 testes JavaScript aprovados;
- 18 fluxos Chrome aprovados;
- 1 fluxo Chrome contra servidor e API reais aprovado;
- execução oficial reconciliada em 5.000 analisadas, 4.586 excluídas e 414
  aprovadas;
- banco de dados não alterado.

## Resultado

O menu `Screener` agora leva diretamente à única interface oficial. Subetapa
18-D.2 aprovada tecnicamente.
