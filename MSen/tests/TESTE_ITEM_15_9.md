# Evidência do Item 15.9 — aprovação da regra PD_003

Data: 2026-10-27.

Após revisar detector, histórico reconciliado e duas simulações sombra, o
usuário autorizou o uso da regra de PD_003.

## Regra aprovada

- Detector: maior bloco numérico consecutivo com quatro, cinco ou seis dezenas.
- Operador: `percentual_historico <= tolerancia`.
- Tolerância para PD_003: 3%.
- Dado ausente/inconsistente: não excluir; registrar `nao_avaliavel` e motivo.

O percentual histórico reconciliado de PD_003 é 5/3.069 = 0,162920%, portanto
o padrão atende ao limite aprovado. A tolerância qualifica o padrão; ela não
determina diretamente o percentual de combinações excluídas.

## Limite da autorização

A regra poderá ser ativada no Item 15.10 somente na amostra protegida de 5.000,
com conferência da contabilidade. O universo integral e os demais padrões
continuam sem autorização.

Nenhuma ativação foi realizada neste item.
