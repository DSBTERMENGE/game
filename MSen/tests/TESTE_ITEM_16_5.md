# Teste do Item 16.5 — classificador piloto de dezenas sequenciais

Data: 28/10/2026

## Implementação

Foi criado o classificador exclusivo do grupo `PG_001`. Ele usa a mesma função
central dos três detectores históricos e devolve:

- `PD_001` quando o maior bloco possui exatamente duas dezenas;
- `PD_002` quando o maior bloco possui exatamente três dezenas;
- `PD_003` quando o maior bloco possui quatro, cinco ou seis dezenas;
- `SEM_CORRESPONDENCIA` quando não há duas dezenas consecutivas.

A resposta é imutável e inclui evidência estruturada: dezenas ordenadas,
tamanho do maior bloco e todos os blocos empatados nesse tamanho. Essa evidência
permitirá à auditoria futura mostrar exatamente por que a função classificou o
resultado.

## Casos manuais confirmados

```text
01 03 05 07 09 11 -> SEM_CORRESPONDENCIA
10 25 26 38 50 58 -> PD_001; bloco 25,26
10 25 26 27 50 58 -> PD_002; bloco 25,26,27
01 02 03 04 20 40 -> PD_003; bloco 01,02,03,04
01 02 03 04 05 40 -> PD_003; bloco de cinco
01 02 03 04 05 06 -> PD_003; bloco de seis
```

O caso `58,59,60,01,02,03` foi classificado como `PD_002`, com dois blocos
separados (`01,02,03` e `58,59,60`). A função não trata `60` e `01` como
consecutivos.

Também foi confirmado que um resultado com blocos de dois e três pertence
somente ao padrão do maior bloco, sem sobreposição.

## Testes

- 18 testes direcionados do classificador, detectores e estatísticas: aprovados;
- 398 testes na regressão Python: aprovados.

Permaneceram apenas os avisos já conhecidos dos testes do frontend do screener.
Nenhum banco foi acessado e nenhuma classificação foi persistida nesta
subetapa.
