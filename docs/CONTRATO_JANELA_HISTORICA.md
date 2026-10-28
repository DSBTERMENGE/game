# Contrato da janela histórica

A janela histórica fornece a amostra que será usada pelos perfis estatísticos,
geométricos e de padrões e, futuramente, pelo backtest.

## Modos

- Sem corte: seleciona todos os resultados disponíveis. Este modo serve para a
  análise atual do histórico completo.
- `numero_ap_antes_de=N`: seleciona somente concursos com número menor que `N`.
- `data_antes_de=D`: seleciona somente resultados com data menor que `D`.

Os cortes são **exclusivos**. Ao avaliar o concurso 100, deve-se informar
`numero_ap_antes_de=100`; a amostra conterá no máximo os concursos 1 a 99. Isso
impede que o resultado avaliado e informações futuras contaminem o backtest.

Concurso e data não podem ser informados simultaneamente. A escolha de um único
eixo torna o corte reproduzível e evita resultados diferentes por interpretação.

## Garantias

- a entrada pode estar fora de ordem e a saída será ordenada por concurso;
- concursos duplicados são rejeitados;
- uma data posterior associada a um concurso anterior é rejeitada;
- a coleção original não é modificada;
- uma janela anterior ao primeiro concurso é válida e fica vazia;
- o serviço não consulta nem modifica banco, API, interface ou screener.

O serviço aceita os modelos já usados pelo sistema, `ResultadoEntrada` e
`ResultadoCalculado`, e devolve também o total disponível, a quantidade
selecionada e os limites efetivamente aplicados.
