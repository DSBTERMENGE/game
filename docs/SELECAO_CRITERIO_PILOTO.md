# Seleção do critério piloto

Data da análise: 2026-10-27.

Escolher o piloto autoriza somente a preparação de seus casos de aceitação no
Item 15.4. Não aprova tolerância, modo sombra, exclusão ou ativação.

## Candidatos mais adequados

| Prioridade | Código | Padrão | Ocorrências | Percentual | Avaliação para piloto |
|---:|---|---|---:|---:|---|
| 1 | PD_003 | Mais de três dezenas sequenciais | 5 | 0,162920% | Regra simples, rara, exclusiva e já coberta por testes. |
| 2 | PD_006 | Mais de três em linhas subjacentes na mesma coluna | 4 | 0,130336% | É o mais raro, mas acrescenta a geometria vertical da matriz. |
| 3 | PD_005 | Três em linhas subjacentes na mesma coluna | 66 | 2,150538% | Raro, porém depende da mesma interpretação vertical. |
| 4 | PD_002 | Três dezenas sequenciais | 92 | 2,997719% | Simples e útil para testar limite de 3%, mas fica muito perto do exemplo ainda não aprovado. |
| 5 | PD_009 | Mais de três dezenas na mesma linha | 93 | 3,030303% | Bom contraponto ao limite de 3%, mas a ocupação de linha é menos simples que sequência numérica. |

PD_001, PD_004, PD_007 e PD_008 não são recomendados como primeiro piloto
porque aparecem em 28% a 67% do histórico. Eles continuam válidos para estudo,
mas não exercitam primeiro o caso de baixa ocorrência que motivou o screener.

## Recomendação: PD_003

`PD_003 — Mais de três dezenas sequenciais` é o piloto recomendado porque:

1. sua regra é diretamente verificável: o maior bloco consecutivo tem tamanho
   quatro, cinco ou seis;
2. a ordem das dezenas não interfere;
3. ele é exclusivo em relação a PD_001 e PD_002;
4. possui detector puro e testes existentes;
5. ocorreu somente 5 vezes em 3.069 resultados;
6. permite validar todo o processo antes de acrescentar coordenadas de coluna,
   ocupação de linha ou situações próximas ao limite de 3%.

Os concursos históricos registrados para PD_003 são 186, 509, 2052, 2789 e
2908. Esses números serão conferidos novamente na reconciliação do Item 15.6.

## Alternativa

Se a prioridade for começar pelo padrão mais raro em termos absolutos, a
alternativa é `PD_006`, com 4 ocorrências. Essa escolha exige que os casos de
aceitação comprovem cuidadosamente o significado de mesma coluna **e linhas
imediatamente subjacentes**.

## Decisão

Em 2026-10-27, o usuário aprovou `PD_003` como piloto de teste. A aprovação
permite preparar os casos de aceitação e validar o detector. Ela não aprova
tolerância, modo sombra, exclusão ou ativação no funil.
