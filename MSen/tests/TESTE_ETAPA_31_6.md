# Evidência da etapa 31.6 — Reorganização visual do Painel

Data: 12/11/2026

## Organização aplicada

Os comandos antes reunidos em três linhas passaram a ocupar cinco quadros com
cantos arredondados:

1. Dados e navegação;
2. Voo dos pássaros;
3. Manchas;
4. Ocorrência das dezenas;
5. Quadrantes.

Dados e navegação ficaram em um quadro compacto à esquerda, acima do mapa. O
quadro termina logo após sua mensagem operacional. Voo dos pássaros, Manchas,
Ocorrência das dezenas e Quadrantes ficaram fora dele, numa coluna de análise à
direita. Assim, os novos controles ocupam o espaço lateral livre e não criam uma
segunda faixa acima do mapa.

Todos os identificadores dos comandos existentes foram preservados. O mapa, o
cabeçalho do resultado, o diálogo de aparência e o código JavaScript não
precisaram ser modificados.

## Adaptação da tela

- telas largas mantêm Dados e o mapa à esquerda e os controles à direita;
- telas intermediárias empilham a coluna de controles entre Dados e o mapa;
- telas pequenas apresentam os controles laterais em uma única coluna;
- os quadros permitem quebra interna dos comandos sem ultrapassar a janela.

## Validação

- 126 testes unitários do frontend aprovados;
- quatro fluxos Chromium aprovados em porta isolada: aparência, camadas
  geométricas, voo, importação, mancha e limpeza;
- a primeira tentativa do navegador encontrou a porta padrão 4173 já ocupada;
  a validação foi repetida na porta livre 4190;
- nenhuma API, tabela ou linha do banco foi alterada.

A integração funcional de Polígono 2, quadrantes e gradientes permanece nas
etapas específicas seguintes.
