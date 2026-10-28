# Teste da subetapa 17.7 — configuração das faixas

## Regras verificadas

- escolha entre percentual da média e múltiplos do desvio-padrão;
- margens inferior e superior independentes e não negativas;
- prévia obrigatória antes de habilitar o salvamento;
- limites dos dez parâmetros calculados pela API real do sistema;
- persistência local e recuperação após recarregar a página;
- estudo salvo sem qualquer campo de ativação do screener;
- diálogo com tabela de prévia e rolagem interna.

## Resultado

- 29 testes JavaScript aprovados.
- 16 fluxos completos no Google Chrome aprovados.
- O Chrome confirmou o ciclo abrir, alterar, calcular dez limites, salvar e
  recuperar a configuração após recarregar.
- 446 testes Python de regressão aprovados.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Nenhum dado de banco foi gravado e nenhuma exclusão foi ativada.
