# Teste da subetapa 15.11 — próximo padrão histórico

Data: 2026-10-27

## Padrão selecionado

Foi selecionado `PD_002 — Três dezenas sequenciais`, por ser o próximo padrão
do mesmo grupo conceitual de PD_003 e possuir percentual histórico próximo da
tolerância de 3%.

Contrato validado: o maior bloco consecutivo deve possuir exatamente três
dezenas. Blocos de dois pertencem exclusivamente a PD_001; blocos de quatro ou
mais pertencem exclusivamente a PD_003; 60/01 não forma sequência circular.
Os casos estão em `docs/CASOS_ACEITACAO_PD002.md`.

## Reconciliação histórica

- Resultados avaliados: 3.069.
- Primeira ocorrência: concurso 9.
- Última ocorrência: concurso 3.060.
- Ocorrências: 92.
- Percentual histórico: 2,997719%.
- Intervalo médio: 33,527473.
- Desvio-padrão populacional: 33,637806.

Quantidade, intervalo médio e desvio-padrão coincidiram exatamente com os
valores persistidos. A consulta foi somente de leitura.

## Simulação sombra com tolerância hipotética de 3%

| Semente | Avaliadas | Marcadas | Percentual da amostra | Saldo hipotético |
|---:|---:|---:|---:|---:|
| 20261027 | 5.000 | 162 | 3,24% | 4.838 |
| 42 | 5.000 | 142 | 2,84% | 4.858 |

Todas as 10.000 combinações foram realmente aprovadas e nenhuma foi excluída.
A regra histórica seria satisfeita porque `2,997719% <= 3%`, mas continua sem
autorização para exclusão real.

## Testes e estado

- Os 10 casos válidos e 4 contratos de entrada inválida foram verificados.
- A classificação positiva foi conferida como exclusiva de PD_002.
- Passaram 320 testes, incluindo a reprodução das duas simulações.
- O processamento integral permanece bloqueado.
- PD_002 não foi incluído na configuração ativa.

## Ativação autorizada

O usuário aprovou detector, operador inclusivo `<=`, tolerância de 3% e falha
conservadora. PD_002 foi ativado depois de PD_003 na mesma amostra protegida:

- PD_003: 5.000 avaliações, 11 exclusões, saldo 4.989;
- PD_002: 4.989 avaliações, 162 exclusões, saldo 4.827;
- fechamento: `5.000 = 11 + 162 + 4.827`.

PD_002 avaliou 4.989 combinações porque o funil interrompe as 11 já excluídas
por PD_003. Os padrões são exclusivos, portanto nenhuma exclusão de PD_002 foi
perdida por essa ordem. Passaram 323 testes Python. O processamento integral
permanece bloqueado e nenhuma escrita foi feita no banco.

Resultado: primeiro ciclo da subetapa 15.11 concluído com PD_002 ativo apenas
na amostra protegida.
