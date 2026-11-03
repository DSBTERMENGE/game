# Evidência — subetapa 23.1

Data: 03/11/2026

## Objetivo

Fechar o contrato do backtest e das métricas da futura página `Seleção de
dezenas`, sem implementar persistência ou execução.

## Regras verificadas

- período inclusivo do alvo 500 ao último resultado disponível;
- seleção do alvo `C` congelada com corte `C - 1` antes da conferência;
- classes mutuamente exclusivas de 0 a 6 acertos;
- resultado de seis acertos contabilizado somente na classe 6;
- seleção válida vazia contabilizada na classe 0;
- ausência completa de base marcada como `NAO_AVALIAVEL`;
- pendentes e não avaliáveis fora dos denominadores;
- distribuição de classes, cobertura, precisão e média de acertos;
- quantidade mínima, máxima e média de dezenas selecionadas;
- custo combinatório por `C(N,6)`;
- comparação somente com mesma origem, período e versão.

## Casos manuais

O contrato contém casos de cinco acertos, zero acertos, seleção vazia, ausência
de base, consolidação de classes e proteção temporal do concurso 500.

## Resultado

Subetapa 23.1 concluída exclusivamente no nível contratual. Não foram criadas
tabelas, migrações, funções, APIs ou páginas.
