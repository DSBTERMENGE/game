# Evidência da etapa 26.3

Data: 10/11/2026.

## Modelo criado

- `ConfiguracaoFormacaoJogos` imutável;
- dinheiro representado por `Decimal` com duas casas;
- valor máximo previsto calculado por quantidade solicitada × valor unitário;
- chave SHA-256 reproduzível para idempotência;
- assinatura do Screener e assinatura/versão do classificador obrigatórias.

## Banco

- migração 026: `formacoes_jogos_selecao` e `jogos_finais_selecao`;
- migração 027: valores calculados ampliados para `NUMERIC(24,2)`;
- configuração protegida contra atualização;
- jogo final protegido contra atualização;
- totais reconciliados e quantidade disponibilizada limitada;
- tabelas antigas preservadas temporariamente;
- nenhuma tabela ou registro existente removido.

## Validação real

Uma transação de ensaio confirmou:

- R$ 5,00 × 100 = R$ 500,00 no PostgreSQL;
- repetição da chave idempotente recusada;
- tentativa de alterar o valor unitário recusada;
- rollback integral do ensaio;
- zero formações e zero jogos finais depois do teste.

As novas tabelas ainda não possuem API de gravação. Elas somente serão usadas
depois da integração das próximas etapas.
