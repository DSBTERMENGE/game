# Evidência — subetapa 22.17.2

Data: 2026-11-02

## Implementação

Renderizador: `frontend/js/frequencia-grafico-distribuicao.js`.

- Eixo X: duração do intervalo em concursos.
- Eixo Y: ocorrências em percentual.
- Distribuição real: linha e pontos vinho.
- Curva normal teórica: linha azul tracejada.
- Média: marcador vertical contínuo.
- Média menos/mais um desvio: marcadores verticais tracejados.
- Pontos reais acessíveis por mouse, foco e clique, mostrando duração,
  quantidade e percentual.
- Limites fora do domínio são informados sem alteração das coordenadas.
- Conjunto vazio e desvio zero possuem apresentação controlada.

O renderizador é independente do modal. A ligação ao único diálogo gráfico
será realizada na subetapa 22.17.4.

## Testes

Arquivo: `frontend/tests/frequencia_grafico_distribuicao.test.mjs`.

- curvas real e normal compartilham domínio;
- nenhum caminho contém `NaN` ou infinito;
- média e limites somente são desenhados dentro do domínio;
- desvio zero omite a curva normal e preserva a distribuição real;
- conjunto vazio não cria geometria.

Resultado:

```text
npm run test:frontend
69 testes aprovados
```
