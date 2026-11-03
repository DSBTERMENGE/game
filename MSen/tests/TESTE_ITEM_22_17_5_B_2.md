# Teste da subetapa 22.17.5-B.2

Data: 02/11/2026

## Amostras controladas

| Quantidade | Passo horizontal | Pontos intermediários fora da grade | Último ponto |
|---:|---:|---:|---|
| 20 | 5% | 0 | `(100%,100%)` |
| 14 | 7,142857% | 12 | `(100%,100%)` |
| 17 | 5,882353% | 16 | `(100%,100%)` |

Os pontos não foram arredondados nem deslocados para as linhas de 5%.

## Dados reais

Evento `SIMPLES`, concursos 500 a 3.069:

| Dezena | Pontos | Passo X | Pontos coincidentes com grade | Inversões | Último ponto |
|---:|---:|---:|---:|---:|---|
| 08 | 264 | 0,378788% | 4 | 0 | `(100%,100%)` |
| 10 | 314 | 0,318471% | 2 | 0 | `(100%,100%)` |
| 17 | 271 | 0,369004% | 1 | 0 | `(100%,100%)` |

As coincidências reais com a grade decorrem do cálculo exato; nenhum encaixe
artificial foi aplicado.

## Chrome

Foram confirmados:

- 21 marcas de 0% a 100% em cada eixo;
- 42 linhas finas, sendo 21 verticais e 21 horizontais;
- títulos percentuais dos dois eixos;
- primeiro ponto conforme `100/N`;
- último ponto em `(100%,100%)`;
- modal único e limpeza ao encerrar.

## Regressões

```text
npm run test:frontend
tests 75
pass 75
fail 0
```

```text
npm run test:browser
34 passed
```

## Resultado

Subetapa 22.17.5-B.2 aprovada. O gráfico está liberado para avaliação visual do
usuário. A ajuda e a documentação continuam suspensas até essa avaliação.
