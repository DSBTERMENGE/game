# Proposta de decisão da regra PD_003

Data da proposta: 2026-10-27.

Esta decisão é a autorização humana exigida pelo Item 15.9. A regra somente
será ativada no Item 15.10 depois da aprovação explícita dos quatro pontos.

## Evidências

- Detector aprovado em 20 casos, sem divergências.
- Histórico: 5/3.069, ou 0,162920%.
- Quantidade, intervalo médio e desvio reconciliados com o banco.
- Sombra 20261027: 11/5.000 marcadas (0,22%).
- Sombra 42: 5/5.000 marcadas (0,10%).
- Exclusões reais realizadas: zero.

## 1. Detector

Usar `detectar_mais_de_tres_dezenas_sequenciais`: o maior bloco numérico
consecutivo possui quatro, cinco ou seis dezenas. Blocos separados não são
somados e 60/01 não é circular.

**Recomendação:** aprovar.

## 2. Operador

O padrão fica elegível quando:

```text
percentual_historico <= tolerancia
```

**Recomendação:** aprovar o operador inclusivo `<=`.

## 3. Tolerância

Usar inicialmente `3%`, valor discutido desde a concepção do screener. Como
0,162920% <= 3%, PD_003 fica elegível.

Tolerância de 3% **não** significa excluir 3% das combinações. Ela qualifica
padrões ocorridos em até 3% do histórico. Somente combinações em que o detector
encontrar PD_003 seriam reprovadas; nas amostras, foram 0,22% e 0,10%.

Para PD_003, qualquer tolerância igual ou superior a 0,162920% produz a mesma
elegibilidade. Outros padrões continuarão exigindo aprovação individual.

**Recomendação:** aprovar 3% para o piloto PD_003.

## 4. Dado ausente ou inconsistente

Se detector, ocorrências, total, tolerância ou reconciliação estiverem ausentes
ou inconsistentes, a combinação não será excluída. A decisão será
`nao_avaliavel`, com motivo visível.

**Recomendação:** aprovar a falha conservadora, permitindo a combinação.

## Efeito posterior

Se os quatro pontos forem aprovados, o Item 15.10 poderá ativar somente PD_003
na amostra protegida de 5.000. O processamento integral continuará bloqueado e
a contabilidade deverá fechar `recebidas = excluídas + aprovadas`.

## Decisão

Em 2026-10-27, o usuário autorizou o uso da regra proposta. Foram aprovados:

1. detector `detectar_mais_de_tres_dezenas_sequenciais`;
2. operador inclusivo `percentual_historico <= tolerancia`;
3. tolerância de 3% para PD_003; e
4. falha conservadora, sem excluir quando o dado estiver ausente ou inconsistente.

A aprovação permite a ativação controlada do Item 15.10 somente na amostra de
5.000. Não autoriza processamento integral nem outros padrões.
