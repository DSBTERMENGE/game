# Evidência da etapa 24.4 — Alvo único

Data: 08/11/2026

## Resultado

A documentação e a implementação foram reconciliadas para calcular somente o
concurso-alvo imediatamente posterior ao último resultado cadastrado:

```text
CA = último concurso cadastrado + 1
```

O horizonte configurável foi removido das configurações atuais, da assinatura
versão 2, da API e da interface. Evidências da Etapa 23 foram mantidas como
registro histórico e marcadas como superadas pela Etapa 24.

## Validações aprovadas

- 683 testes Python;
- 86 testes unitários do frontend;
- 2 testes Playwright da página Seleção de dezenas;
- validador integrado da previsão sequencial em PostgreSQL efêmero;
- validador integrado da API, backtest, previsão e jogos em PostgreSQL efêmero;
- migração 023 exercitada pelos testes de DDL e integração.

Os `ResourceWarning` emitidos por três arquivos já existentes do Screener não
causaram falhas. Os avisos do Node sobre módulos sem `type: module` também não
afetaram os resultados.

## Aplicação no banco local

Após autorização específica do usuário, a migração 023 foi aplicada ao banco
local real `games`. A auditoria confirmou:

- versão 023 registrada em `schema_migrations`;
- coluna `horizonte_concursos` removida;
- coluna `versao_assinatura` obrigatória e com padrão 2;
- 0 configurações e 0 execuções, as mesmas cardinalidades verificadas antes da
  migração.

## Ajuste posterior de usabilidade

O primeiro teste manual revelou uma falsa divergência entre números equivalentes
como `1` e `1.000000`. Os parâmetros passaram a ser normalizados para seis
casas decimais antes da assinatura. A interface deixou de exibir a assinatura,
bloqueia a edição de configurações salvas e explica que novos parâmetros devem
ser gravados como nova configuração.

Após o ajuste, foram aprovados 684 testes Python, 86 testes unitários do
frontend, 3 testes Playwright e o validador integrado da API enviando os mesmos
valores numéricos produzidos pelo navegador.
