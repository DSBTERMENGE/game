# Evidência da Etapa 25.5.2 — configuração e período próprios do estudo

Data: 09/11/2026.

## Implementação

- O Backtest possui a lista independente `Configuração do estudo`.
- A primeira opção exige uma escolha explícita e as demais mostram ID e nome.
- A configuração superior não determina mais o estudo.
- O campo de concurso final foi removido.
- O concurso inicial permanece com padrão 500.
- Prévia e início aceitam somente configuração salva e concurso inicial.
- O servidor consulta o último concurso cadastrado e sempre o usa como final.
- Progresso e relatório identificam configuração, k, j, modo, quantidade fixa,
  versão, período e quantidade de concursos.
- O relatório mantém a indicação de que não foi gravado.
- O processo persistente foi preservado e usa a configuração própria do estudo.

## Validação

- 89 testes de frontend aprovados.
- 19 testes da API aprovados.
- 6 testes Playwright aprovados, incluindo independência entre as duas listas.
- O contrato rejeita `concurso_final` enviado pelo cliente.
- A validação real rejeita início 499 e início 3.070, acima do último cadastrado.
- A validação HTTP real processou 2.570 pontos em aproximadamente 3,53 segundos,
  confirmou cancelamento e descarte e manteve as cardinalidades inalteradas.

## Conclusão

O estudo agora exige somente uma configuração salva e o concurso inicial. O
servidor controla o final e o relatório preserva a identificação completa da
configuração efetivamente utilizada.
