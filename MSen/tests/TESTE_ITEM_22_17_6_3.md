# Teste da subetapa 22.17.6.3

Data: 02/11/2026

## Conteúdo implementado

A ajuda contextual de **Curva de distribuição** agora explica:

- finalidade da análise de frequência por duração;
- duração em concursos no eixo horizontal;
- percentual de ocorrências no eixo vertical;
- diferença entre distribuição observada e curva normal teórica;
- média e limites de um desvio-padrão;
- consulta da quantidade e do percentual em cada ponto;
- exemplo `Intervalo 4: 28 ocorrências · 11,07%`;
- possibilidade de distribuição assimétrica concentrada em intervalos curtos;
- ausência de garantia sobre a próxima ocorrência.

## Testes

```text
npm run test:frontend
tests 78
pass 78
fail 0
```

O teste confirma a presença dos eixos, das duas curvas, das referências
estatísticas, do exemplo e das limitações no conteúdo associado ao tipo
`distribuicao`.

## Resultado

Subetapa 22.17.6.3 concluída. A ajuda de **Ocorrências em ordem crescente**
permanece provisória.
