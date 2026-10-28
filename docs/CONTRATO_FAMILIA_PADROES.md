# Contrato da família de grupos de padrões

Cada grupo fotografado gera um filtro no funil. A combinação é classificada uma
única vez naquele grupo, resultando em um `padrao_cod` exclusivo ou na classe
`SEM_CORRESPONDENCIA`.

A decisão consulta somente a lista de padrões excludentes congelada no início da
execução. Frequências ou configurações alteradas posteriormente não mudam uma
execução em andamento nem uma auditoria reproduzida.

## Evidência

Cada decisão registra:

- grupo e classe encontrados;
- evidência própria do classificador;
- quantidade e percentual históricos da classe;
- denominador e política de raridade;
- lista excludente fotografada.

`SEM_CORRESPONDENCIA` participa do denominador e do fechamento em 100%, mas não
é código de padrão e nunca integra a lista excludente.

## Extensibilidade e segurança

O construtor aceita qualquer quantidade de grupos, mas exige exatamente um
classificador para cada grupo fotografado. O retorno de um grupo divergente ou
de uma classe ausente da fotografia interrompe a execução com erro explícito.
Atualmente, o classificador oficial de dezenas sequenciais atende `PG_001`.
