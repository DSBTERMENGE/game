# Evidência da Etapa 25.6 — comparação dos motores

Data: 09/11/2026.

## Referência persistente

A comparação utilizou a Execução 1 já existente, sem criar outro backtest
persistente:

- configuração 3 — `Configuração_k=0.5, j=0`;
- k = 0,500000 e j = 0,000000;
- modo MAX e versão 1;
- concursos 500 a 3.069;
- 2.570 concursos avaliados;
- duração observada anteriormente na tela: 79,7 segundos.

## Procedimento

O validador `validar_comparacao_motores_selecao.py`:

1. leu os pontos já preservados da Execução 1;
2. executou o motor temporário com a mesma configuração e concurso inicial;
3. comparou, concurso por concurso, quantidade retornada e quantidade de acertos;
4. descartou o relatório temporário;
5. comparou as cardinalidades do banco antes e depois.

## Resultado

- 2.570 pontos persistentes comparados;
- 2.570 pontos temporários comparados;
- zero concursos ausentes ou adicionais;
- zero divergências de quantidade de dezenas;
- zero divergências de quantidade de acertos;
- duração interna temporária: aproximadamente 3,01 segundos;
- duração temporária de ponta a ponta: aproximadamente 3,09 segundos;
- aceleração aproximada diante dos 79,7 segundos observados: 25,79 vezes.

## Ausência de gravação

As cardinalidades antes e depois permaneceram idênticas:

- configurações: 2;
- resultados: 3.069;
- execuções: 1;
- alvos persistidos: 2.570;
- avaliações individuais: 154.200.

O relatório temporário foi descartado e nenhuma linha foi criada, alterada ou
removida por sua execução.

## Observação sobre desempenho

A duração persistente de 79,7 segundos foi a apresentada pela interface durante
a criação original da Execução 1; o banco não possui um campo próprio com essa
duração. Por isso, a aceleração é uma comparação observacional, enquanto a
igualdade dos 2.570 resultados e a ausência de gravação foram verificadas
diretamente e de forma integral.

## Conclusão

Para a configuração e o período comparados, o motor temporário reproduziu
exatamente os resultados do motor persistente, com tempo muito menor e sem
modificar o banco.
