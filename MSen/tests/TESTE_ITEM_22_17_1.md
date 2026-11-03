# Evidência — subetapa 22.17.1

Data: 2026-11-02

## Implementação

Módulo puro: `frontend/js/frequencia-intervalos-auxiliares.js`.

- Não acessa DOM, servidor ou banco.
- Calcula frequência real por duração e percentual sobre o total.
- Calcula média e desvio-padrão populacional sobre o mesmo conjunto.
- Calcula a área normal teórica de cada faixa `d − 0,5` a `d + 0,5`.
- Ordena intervalos sem eliminar repetições.
- Calcula `i / N × 100` e `intervalo / maior_intervalo × 100`.
- Trata conjunto vazio e desvio zero.
- Rejeita intervalos não inteiros, não positivos ou inválidos.

## Testes

Arquivo: `frontend/tests/frequencia_intervalos_auxiliares.test.mjs`.

Foram validados:

- distribuição 50%, 25%, 0%, 25%, totalizando 100%;
- média 2 e variância populacional 1,5;
- repetições preservadas nas posições 25%, 50%, 75% e 100%;
- simetria da curva normal em torno da média;
- conjunto vazio, único intervalo e desvio zero;
- rejeição de entradas fora do contrato.

Resultado geral:

```text
npm run test:frontend
65 testes aprovados
```
