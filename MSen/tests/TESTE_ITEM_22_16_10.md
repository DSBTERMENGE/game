# Teste do item 22.16.10 — Linhas de um desvio-padrão

Data: 2026-10-31

## Regra

- Linha inferior: `media_intervalos - desvio_padrao_intervalos`.
- Linha superior: `media_intervalos + desvio_padrao_intervalos`.
- Unidade: concursos.
- Valor ausente em qualquer operando produz ponto ausente, não zero.

## Resultado

- 57 testes JavaScript aprovados.
- 10 fluxos Chrome aprovados.
- O fluxo gráfico confirmou uma linha inferior e uma superior, além das séries
  preexistentes, sem coordenadas inválidas.
- A página real da dezena 17 confirmou uma linha inferior, uma superior,
  mínimo, máximo e duas linhas médias nos dois gráficos, sem `NaN`.
- As novas linhas entram no domínio automático e não alteram API nem banco.
