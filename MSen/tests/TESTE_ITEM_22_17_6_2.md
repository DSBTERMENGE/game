# Teste da subetapa 22.17.6.2

Data: 02/11/2026

## Conteúdo implementado

A ajuda contextual de **Evolução dos intervalos** agora apresenta:

- finalidade do gráfico;
- eixo horizontal como número do concurso;
- eixo vertical como duração em concursos;
- interpretação dos patamares e transições verticais;
- média acumulada dos intervalos;
- média menos e mais um desvio-padrão;
- losango e haste para intervalos estreitos;
- consulta por mouse, teclado ou clique;
- exemplo `Concursos 1246 → 1261 · intervalo 15`;
- alerta de que o histórico não garante a próxima ocorrência.

## Testes

```text
npm run test:frontend
tests 77
pass 77
fail 0
```

O teste confirma a presença dos eixos, linhas, marcadores, exemplo e limitação
de interpretação no conteúdo associado ao tipo `evolucao`.

## Resultado

Subetapa 22.17.6.2 concluída. As ajudas de **Curva de distribuição** e
**Ocorrências em ordem crescente** permanecem provisórias.
