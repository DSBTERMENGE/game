# Configuração das faixas do estudo

A página de distribuições permite configurar, no diálogo **Configurar faixas**:

- percentual da média ou múltiplos do desvio-padrão;
- margem inferior;
- margem superior.

As margens podem ser diferentes. O botão **Calcular prévia** consulta a mesma API
e as mesmas funções utilizadas pelo painel e apresenta os limites dos dez
parâmetros antes que o estudo possa ser salvo.

Nesta fase, a configuração é armazenada no `localStorage` do navegador. Ela é
restaurada ao abrir novamente a página, mas não é uma configuração operacional
do servidor e não é compartilhada entre navegadores ou computadores.

Salvar o estudo apenas atualiza os gráficos. Não cria nem ativa regras do
screener. A passagem de uma faixa estudada para uma regra de exclusão exigirá
uma etapa posterior, validação, backtest e autorização expressa.
