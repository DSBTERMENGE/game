# Ideias

Possibilidades ainda não aprovadas para o produto. Uma ideia somente vira
funcionalidade depois de decisão explícita registrada em `notas/decisoes.md`.

- Painel com filtros por concurso e período.
- Frequência e atraso aparente das dezenas.
- Comparação de combinações com resultados históricos.
- Visualização gráfica das análises.
- Mapa de calor das dezenas por período.
- Distribuição de pares e ímpares, faixas numéricas e soma das dezenas.
- Histórico de importações com origem e resumo de validação.
- Exportação de consultas para CSV ou planilha.
- Atualização assistida de novos concursos, sempre com conferência antes da
  gravação.
- Painel administrativo para estado do banco, versão das migrações e último
  backup.

Observação: estatísticas históricas não tornam previsíveis sorteios aleatórios.

## Screener consolidado e backtests

- Organizar o quadro do screener em três famílias: valores estatísticos,
  medidas gráficas/geométricas e grupos de padrões.
- Mostrar exclusões e percentuais por filtro, subtotal por família, saldo entre
  famílias e total final de combinações aprovadas.
- Contabilizar cada combinação somente no primeiro filtro que a excluir.
- Preservar o limite experimental de 5.000 enquanto o funil estiver em teste; o
  universo integral C(60, 6) possui 50.063.860 combinações.
- Criar backtests antes de liberar exclusões no universo integral. Em cada ponto
  do backtest, usar somente concursos anteriores para construir as referências.
- Medir quantos resultados reais posteriores seriam preservados ou descartados
  por cada filtro, detectar redundância e comparar a ordem dos critérios.
- Tratar bom resultado histórico apenas como evidência experimental; ele não
  demonstra previsibilidade de sorteios aleatórios.
