# Teste da subetapa 22.17.5-A.2

Data: 02/11/2026

## Amostra controlada

Entrada: `4, 1, 2, 2`.

Resultado exato:

```text
(1,1), (2,2), (3,2), (4,4)
```

Os pontos 2 e 3 possuem posições horizontais diferentes e a mesma altura. Os
três espaços horizontais consecutivos são iguais.

## Dados reais

Evento `SIMPLES`, concursos 500 a 3.069:

| Dezena | Pontos | Primeiro | Último | Inversões |
|---:|---:|---|---|---:|
| 08 | 264 | `(1,1)` | `(264,46)` | 0 |
| 10 | 314 | `(1,1)` | `(314,49)` | 0 |
| 17 | 271 | `(1,1)` | `(271,60)` | 0 |

As diferenças residuais entre espaçamentos ficaram abaixo de `3,3 × 10⁻¹³`
unidades SVG e decorrem apenas da representação binária de números decimais.
Visualmente e matematicamente, o espaçamento é uniforme.

## Regressões

```text
npm run test:frontend
tests 74
pass 74
fail 0
```

```text
npm run test:browser
34 passed
```

No Chrome foram confirmados os títulos:

- `Ordem dos intervalos (menor para o maior)`;
- `Duração do intervalo (concursos)`.

## Resultado

Subetapa 22.17.5-A.2 aprovada. O gráfico está liberado para nova avaliação
visual do usuário. A ajuda e a documentação permanecem suspensas até essa
avaliação.
