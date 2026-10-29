# Contrato da família de grupos de padrões

Cada grupo fotografado gera um filtro no funil. Somente padrões reais, com
`padrao_cod` e função Python aprovada, participam da fotografia.

A decisão consulta somente a lista de padrões excludentes congelada no início da
execução. Frequências ou configurações alteradas posteriormente não mudam uma
execução em andamento nem uma auditoria reproduzida.

## Evidência

Cada decisão registra:

- grupo e padrão encontrados;
- evidência própria do classificador;
- quantidade e percentual históricos do padrão;
- denominador e política de raridade;
- lista excludente fotografada.

Quando nenhum padrão estudado é identificado, nenhuma classe é criada ou
persistida e a combinação segue para o próximo critério. O denominador dos
percentuais continua sendo o total de sorteios históricos.

## Extensibilidade e segurança

O construtor aceita qualquer quantidade de grupos, mas exige exatamente um
classificador para cada grupo fotografado. O retorno de um grupo divergente ou
de uma classe ausente da fotografia interrompe a execução com erro explícito.
Atualmente, o classificador oficial de dezenas sequenciais atende `PG_001`.
