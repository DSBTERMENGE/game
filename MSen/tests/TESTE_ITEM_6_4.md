# Teste do Item 6.4

Data: 2026-10-26

## Resultado

- 4 testes específicos da mancha aprovados;
- 19 testes de frontend acumulados aprovados;
- 137 testes Python de regressão aprovados;
- nenhum banco alterado e nenhum acesso ao PythonAnywhere.

## Casos confirmados

- conjunto pequeno cria seis marcas por resultado e uma marca de média;
- ocorrências da mesma dezena ocupam posições lado a lado;
- o diâmetro lógico é de aproximadamente 3 mm a 96 DPI;
- depois de preencher as linhas de uma célula, a próxima ocorrência retorna ao
  primeiro ponto e aumenta a densidade por sobreposição;
- 3.000 resultados geram 18.000 marcas de dezenas e 3.000 marcas de média;
- limite automatizado de desempenho: menos de 2 segundos;
- limite automatizado de memória adicional: menos de 128 MiB;
- Limpar remove todas as 21.000 marcas e restaura cabeçalho e mensagem.

## Execução

```text
node --test frontend/tests/painel_navegacao.test.mjs
```

O teste acumulado completo terminou em aproximadamente 0,34 segundo neste
ambiente local com Node.js 22.
