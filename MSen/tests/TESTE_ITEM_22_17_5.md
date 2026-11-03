# Teste da subetapa 22.17.5

Data: 02/11/2026

## Dados reais conferidos

Consulta: evento `SIMPLES`, concursos 500 a 3.069.

| Dezena | Concursos | Ocorrências/intervalos | Mínimo | Máximo | Durações repetidas | Soma percentual |
|---:|---:|---:|---:|---:|---:|---:|
| 08 | 2.570 | 264 | 1 | 46 | 24 | 100% |
| 10 | 2.570 | 314 | 1 | 49 | 25 | 100% |
| 17 | 2.570 | 271 | 1 | 60 | 27 | 100% |

As repetições permanecem como ocorrências independentes no gráfico ordenado.
O primeiro ponto ocupa `1/N × 100`, o último ocupa 100% e nenhum ponto é
movido para coincidir com a grade de 5%.

## Validação do modal no Chrome

Confirmado:

- somente um `dialog` e um SVG compartilhados pelos dois botões;
- abertura da curva de distribuição;
- fechamento por `Esc` com limpeza do SVG;
- abertura posterior do gráfico ordenado sem conteúdo residual;
- encerramento pelo botão `Encerrar` com nova limpeza;
- gráfico histórico, filtros e retorno preservados;
- página contida em larguras normal e estreita.

O servidor temporário do teste de navegador foi atualizado para servir os três
novos módulos JavaScript. A aplicação real na porta 5050 já os disponibilizava
corretamente.

## Regressões

### Python

```text
PYTHONPATH=MSen/src python -m unittest \
  MSen.tests.test_frequencia_historica MSen.tests.test_api_frequencias
Ran 29 tests
OK
```

### JavaScript

```text
npm run test:frontend
tests 74
pass 74
fail 0
```

### Chrome — página de frequências

```text
npx playwright test frontend/tests/browser/frequencias.spec.mjs
10 passed
```

### Chrome — regressão completa

```text
npm run test:browser
34 passed
```

## Resultado

Subetapa 22.17.5 aprovada sem alteração das fórmulas. A ajuda e a documentação
dos dois novos gráficos permanecem reservadas à subetapa 22.17.6.
