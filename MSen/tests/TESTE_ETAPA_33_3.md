# Teste da subetapa 33.3 — Ajuste visual compacto

Data: 14/11/2026

## Alteração verificada

- quatro colunas com quinze dezenas cada;
- números tabulares e itens em uma única linha;
- fonte e espaçamento compactos;
- largura externa fixa em `13rem`;
- ausência de cortes e de deslocamento causado pelos valores.

## Conferência no servidor real

O Painel foi aberto em `http://127.0.0.1:5050/` com o histórico cadastrado e a
camada **Dezenas** isolada. Foram obtidas as seguintes medidas:

- 4 colunas com 15 itens;
- 60 frequências exibidas;
- largura externa do resumo: 208 px (`13rem`);
- largura útil da grade: 203,21875 px;
- fonte dos itens: 11,04 px;
- itens com quebra de linha: 0;
- itens com conteúdo cortado: 0.

Os extremos conferidos foram `01: 301` e `60: 297`.

## Resultado

Aprovado. As frequências cabem na lateral do Painel sem alterar sua largura.
