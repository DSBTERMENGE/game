# Evidência — subetapa 23.3

Data: 03/11/2026

## Objetivo

Projetar o modelo relacional das pesquisas da Seleção de dezenas sem executar
DDL.

## Estrutura aprovada

- `configuracoes_pesquisa_selecao`;
- `execucoes_pesquisa_selecao`;
- `alvos_pesquisa_selecao`;
- `avaliacoes_dezenas_pesquisa`.

## Integridade prevista

- configuração assinada, versionada e imutável após uso;
- execução com cópia JSON e assinaturas de configuração e resultados;
- alvo único por execução e concurso;
- referência opcional a `resultados.id_resultado`, sem copiar as seis dezenas;
- exatamente 60 avaliações por alvo concluído pelo motor;
- quantidades aprovada e retornada reconciliadas com os detalhes, e acertos
  conferidos pela referência a `resultados`;
- cascatas somente entre execução, alvos e avaliações;
- `RESTRICT` para configuração e resultado;
- nenhuma tabela de combinações nesta fase.

## Volume analisado

Um backtest de 2.570 alvos gera 154.200 avaliações por configuração. Esse
volume é adequado ao PostgreSQL e permite auditar ranking e exclusões sem
recalcular pesquisas antigas.

## Resultado

Subetapa 23.3 concluída exclusivamente no nível de modelo lógico. Nenhuma
migração, tabela, função, API ou página foi criada.
