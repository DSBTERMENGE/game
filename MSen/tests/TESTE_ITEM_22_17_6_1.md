# Teste da subetapa 22.17.6.1

Data: 02/11/2026

## Implementação

- um único `dialog` contextual para as três ajudas;
- botão `Ajuda` no cartão **Evolução dos intervalos**;
- botão `Ajuda` no cabeçalho do modal dos gráficos auxiliares;
- título selecionado conforme o gráfico aberto;
- fechamento por botão, ícone, `Esc` e clique no fundo;
- limpeza do conteúdo ao fechar;
- retorno do foco ao botão acionador;
- preservação do gráfico, filtros e dados carregados.

O modal possui conteúdo provisório nesta subetapa. Os textos definitivos serão
incorporados separadamente nas subetapas 22.17.6.2, 22.17.6.3 e 22.17.6.4.

## Testes

```text
npm run test:frontend
tests 76
pass 76
fail 0
```

O teste estrutural confirma que existe somente um modal contextual e que os
três títulos são selecionados pela mesma função de abertura.

## Resultado

Subetapa 22.17.6.1 concluída. A próxima é a inserção da ajuda de
**Evolução dos intervalos**.
