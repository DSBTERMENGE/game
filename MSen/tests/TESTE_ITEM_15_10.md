# Teste da subetapa 15.10 — ativação controlada de PD_003

Data: 2026-10-27

## Regra ativada

- Código: `PD_003`.
- Detector: maior bloco com mais de três dezenas consecutivas.
- Operador: percentual histórico `<=` tolerância.
- Tolerância: 3%.
- Evidência reconciliada: 5 ocorrências em 3.069 resultados.
- Escopo: somente a amostra protegida de 5.000 combinações.

## Resultado reproduzível

- Semente: 20261027.
- Recebidas: 5.000.
- Avaliadas por PD_003: 5.000.
- Excluídas por PD_003: 11.
- Aprovadas: 4.989.
- Saldo depois de PD_003: 4.989.
- Conferência: `5.000 = 11 + 4.989`.

As 11 exclusões reais coincidem em quantidade com as 11 marcações da
simulação sombra da subetapa 15.8, feita com a mesma semente e amostra.

## Proteções verificadas

- A configuração continua em modo `amostra`.
- A confirmação de processamento integral continua `false`.
- Evidência ausente ou não reconciliada resulta em `não avaliável` e não exclui.
- O orquestrador antigo sem filtros rejeita a configuração ativa, evitando que
  a regra seja ignorada silenciosamente.
- Nenhuma alteração ou escrita foi feita no banco de dados.

## Regressão

Foram executados 316 testes Python com sucesso. O ambiente não possui `pytest`;
a suíte foi executada com `unittest`, incluindo `src` apenas no processo de
teste. `git diff --check` não encontrou erro de conteúdo, apenas avisos de
conversão de final de linha pelo Git no Windows.

Resultado: subetapa 15.10 aprovada tecnicamente.
