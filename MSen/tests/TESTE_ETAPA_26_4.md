# Evidência da etapa 26.4

Data: 10/11/2026.

## Motor implementado

- geração baseada em `itertools.combinations`;
- uma entrega por combinação, em ordem determinística;
- progresso inicial, periódico e final;
- cancelamento antes da próxima combinação;
- falha do adaptador convertida em erro operacional;
- relatório compacto sem lista de combinações;
- nenhuma persistência.

## Testes

- 7 dezenas: 7 combinações únicas e ordenadas;
- 8 dezenas: progresso sobre 28 combinações;
- cancelamento após 3 entregas sem quarta entrega;
- falha do adaptador identificada;
- origem com menos de 6 dezenas recusada;
- 26 dezenas: 230.230 combinações e pico inferior a 2 MiB.

## Validação com dados reais

- alvo 2.571, concurso 3.070;
- 16 dezenas registradas;
- 8.008 combinações encaminhadas;
- progresso fechado em 8.008 de 8.008;
- duração aproximada de 0,001 segundo com adaptador vazio;
- zero alterações em lotes, formações ou jogos finais.

O adaptador vazio mede somente geração. O custo real dos filtros será medido na
etapa de integração com o Screener.
