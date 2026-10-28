# Evidência de teste — subetapa 18.7

Data: 28/10/2026

## Escopo

Interface expansível ligada ao contrato real do quadro consolidado, ainda sem
API ou execução do novo funil.

## Verificações

- três famílias em linhas compactas e inicialmente recolhidas;
- nove filtros de exemplo contratual renderizados no teste do navegador;
- abertura e fechamento conjunto dos detalhes;
- universo, amostra, exclusões, aprovações e fechamento;
- entradas, avaliações, dois percentuais e saldos por filtro;
- indicação de função Python validada;
- aviso de que cadastro não cria função ou filtro automaticamente;
- ausência de dados fictícios e de chamada à API;
- conteúdo contido na janela do Chrome.

## Resultado

- Testes JavaScript: **35 aprovados**.
- Testes completos no Google Chrome: **18 aprovados**.
- Regressão Python da etapa: **486 testes aprovados** antes das mudanças
  exclusivamente de frontend desta subetapa.
- Página local respondeu **HTTP 200** em `127.0.0.1:5050`.
