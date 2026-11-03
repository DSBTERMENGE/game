# Teste da subetapa 22.17.4

Data: 02/11/2026

## Objetivo

Integrar os dois gráficos auxiliares ao bloco **Evolução dos intervalos** sem
duplicar a estrutura modal e sem repetir a consulta ao servidor.

## Implementação verificada

- botões `Curva de distribuição` e `Ocorrências em ordem crescente` no cartão;
- um único elemento `dialog` para ambos os gráficos;
- compartilhamento de título, legenda, SVG, detalhe, rodapé e botão `Encerrar`;
- função comum de abertura e configuração do modal;
- renderizadores matemáticos mantidos em módulos separados;
- uso dos intervalos já recebidos pela consulta principal;
- fechamento por `Encerrar`, ícone, tecla `Esc` ou clique no fundo;
- limpeza do SVG, atributos, legenda, título e detalhes ao encerrar;
- preservação do gráfico histórico, filtros e dados da consulta.

## Arquivos principais

- `frontend/graficos-frequencias.html`
- `frontend/js/graficos-frequencias.js`
- `frontend/css/graficos-frequencias.css`
- `frontend/tests/frequencias_pagina.test.mjs`

## Testes executados

```text
npm run test:frontend
```

Resultado:

```text
tests 74
pass 74
fail 0
```

O teste estrutural confirma que existe apenas um modal e apenas um SVG para os
dois gráficos e que o evento de fechamento executa a limpeza comum.

## Resultado

Subetapa 22.17.4 concluída. A conferência com dezenas reais e a validação visual
dos dois gráficos permanecem reservadas à subetapa 22.17.5.
