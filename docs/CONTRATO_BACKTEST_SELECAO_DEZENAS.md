# Contrato do Backtest — Seleção de dezenas

Este documento registra a revisão iniciada na Etapa 25.1 e consolidada após a
validação da Etapa 25.8. O Backtest calcula o relatório sem gravar resultados
derivados.

## 1. Finalidade

O backtest verifica, em resultados históricos conhecidos, quantas das seis
dezenas sorteadas estavam na lista produzida pelo screener antes de cada
concurso. Seu relatório deve permitir observar simultaneamente:

- a variação da quantidade de dezenas retornadas;
- a quantidade de acertos de 0 a 6;
- o equilíbrio entre cobertura histórica e tamanho da seleção.

Desempenho histórico não constitui garantia de resultado futuro.

## 2. Premissas de reprodutibilidade

Resultados históricos validados são imutáveis. Novos concursos são
acrescentados à série e não alteram os anteriores.

Com os mesmos resultados históricos, configuração e versão do algoritmo, o
screener deve produzir o mesmo resultado. Por isso, o Backtest não
persistirá avaliações individuais nem listas derivadas que possam ser
recalculadas.

Alterações diretas no PostgreSQL ficam fora do fluxo normal da aplicação. Uma
eventual correção administrativa de resultado deverá invalidar qualquer
relatório do Backtest ainda aberto.

## 3. Entrada

O Backtest recebe somente:

- identificador de uma configuração previamente salva e disponível;
- concurso inicial.

O período é inclusivo, o concurso inicial não pode ser anterior a 500 e deve
ser menor ou igual ao último resultado cadastrado. O concurso final não é
informado pelo usuário: o servidor sempre utiliza o último concurso cadastrado.
A configuração utilizada é imutável e contém `k`, `j`, modo de quantidade,
quantidade fixa quando aplicável e versão do cálculo.

Antes do processamento, a página apresenta uma prévia com a configuração, o
período e a quantidade de concursos. O cálculo começa somente após confirmação
expressa do usuário.

## 4. Proteção temporal

Para cada concurso-alvo `C`:

1. utilizar exclusivamente resultados até `C - 1` para formar as estatísticas;
2. executar o screener sem fornecer a ele o resultado de `C`;
3. obter a lista efetivamente retornada pelo screener;
4. somente então consultar as seis dezenas sorteadas em `C`;
5. calcular a interseção entre as retornadas e as sorteadas.

Para o alvo 500, os cálculos usam somente os concursos 1 a 499. Resultados
posteriores ao alvo jamais podem influenciar sua seleção.

## 5. Resultado por concurso

Durante o relatório, cada concurso é representado apenas por:

```text
concurso
quantidade_dezenas_retornadas
quantidade_acertos
```

Para uma lista `S(C)` retornada pelo screener e o resultado `R(C)`:

```text
quantidade_acertos(C) = |S(C) ∩ R(C)|
```

A quantidade de acertos assume exatamente um valor entre 0 e 6. Um concurso
com seis acertos pertence somente à classe 6, e não também às classes menores.

As avaliações das 60 dezenas podem existir enquanto o concurso está sendo
calculado, mas devem ser descartadas em seguida. Somente os três valores acima
permanecem durante a consulta até o relatório ser fechado ou substituído.

## 6. Ausência de persistência

O Backtest é uma operação de leitura. Ele não deve:

- criar execução de pesquisa no banco;
- criar alvos de pesquisa;
- gravar avaliações individuais das dezenas;
- gravar listas retornadas;
- gravar resumos ou pontos dos gráficos;
- alterar resultados, configurações ou registros do screener.

O relatório deixa de existir quando a página é atualizada ou fechada. Para
consultá-lo novamente, o usuário executa novamente o cálculo.

O contrato não exige nova tabela para dados derivados. A Etapa 25.2 deverá
confirmar se as tabelas básicas e os índices existentes são suficientes para a
leitura eficiente. Qualquer nova estrutura proposta deverá armazenar apenas
dados básicos indispensáveis, nunca reproduzir o resultado calculável do
backtest.

## 7. Primeiro gráfico — quantidade de dezenas

O primeiro gráfico apresenta:

- eixo horizontal com todos os concursos do período;
- rótulos e linhas verticais finas somente de 100 em 100 concursos;
- concursos intermediários posicionados matematicamente, sem linhas verticais
  nem rótulos;
- eixo vertical com a quantidade de dezenas retornadas pelo screener;
- um ponto para cada concurso e uma linha contínua passando pelos pontos;
- uma linha horizontal no menor valor observado;
- uma linha horizontal no maior valor observado.

A escala vertical é ajustada ao mínimo e ao máximo observados, com pequena
margem visual. Ela deve ser mais compacta que a escala do gráfico de acertos;
a proporção inicial será avaliada visualmente com dados reais e poderá ser
ajustada sem modificar a regra de cálculo.

## 8. Segundo gráfico — quantidade de acertos

O segundo gráfico compartilha exatamente as mesmas posições do eixo horizontal
do primeiro, mas possui escala vertical independente de 0 a 6.

- linhas horizontais 0, 1, 2 e 3: vermelhas;
- linhas horizontais 4, 5 e 6: verdes;
- linhas verticais: somente de 100 em 100 concursos;
- um ponto por concurso na classe correspondente;
- linha fina ligando os pontos para tornar visível o percurso histórico.

Os dois gráficos devem manter alinhamento horizontal: o mesmo concurso ocupa a
mesma coordenada X em ambos.

## 9. Quadro-resumo

O relatório informa obrigatoriamente:

- número de testes efetuados;
- quantidade e percentual nas classes 0, 1, 2, 3, 4, 5 e 6;
- menor quantidade de dezenas retornadas;
- maior quantidade de dezenas retornadas;
- média de dezenas retornadas;
- média de acertos por concurso;
- quantidade e percentual de concursos com 4, 5 ou 6 acertos.

Se `A` é o total de concursos avaliados e `n_r` é o total da classe `r`:

```text
percentual_classe(r) = n_r / A × 100
```

As quantidades das sete classes devem somar `A`. Seus percentuais devem somar
100%, admitida somente diferença visual de arredondamento.

## 10. Execução, progresso e cancelamento

O processamento pode ser assíncrono para não bloquear a página, mas sua
identificação acompanha somente o cálculo e não representa registro no banco.

A página deve mostrar:

- quantidade total de concursos;
- quantidade já processada;
- duração transcorrida;
- conclusão, cancelamento ou erro em linguagem compreensível.

O cancelamento interrompe novos cálculos e descarta o relatório incompleto. Não
há retomada persistente, pois nenhum progresso do Backtest é gravado.

## 11. Comparação entre configurações

Comparações não dependerão de IDs permanentes de execuções. Quando
implementadas, deverão utilizar relatórios do Backtest mantidos apenas durante
a sessão da página e exigir o mesmo período e a mesma versão do algoritmo.

Não haverá índice automático de “melhor configuração”. Quantidade de acertos e
tamanho da seleção devem ser interpretados juntos.

## 12. Critérios de aceitação

O novo contrato estará atendido quando:

1. cada alvo usar somente o histórico até `C - 1`;
2. o resultado do alvo for consultado somente após a seleção;
3. cada concurso produzir somente o trio de dados contratado;
4. nenhuma tabela receber dados derivados do Backtest;
5. as sete classes forem exclusivas e somarem os testes efetuados;
6. os dois gráficos compartilharem as mesmas coordenadas horizontais;
7. somente centenas gerarem linhas verticais e rótulos no eixo dos concursos;
8. o gráfico superior mostrar mínimo, máximo e percurso da quantidade;
9. o gráfico inferior mostrar 0 a 3 em vermelho e 4 a 6 em verde;
10. atualizar a página eliminar o relatório do Backtest;
11. o novo motor produzir os mesmos resultados do motor antigo para casos de
    comparação controlada;
12. tempo e memória serem medidos com o período completo antes da substituição
    do processo atual.

## 13. Histórico do escopo

Motor, endpoints, gráficos e substituição do método anterior foram
concluídos nas etapas 25.2 a 25.8. A comparação simultânea de vários relatórios
do Backtest continua fora do escopo atual.
