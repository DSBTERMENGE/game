# Item 15.16 — regressão e fechamento da Etapa 15

Data: 2026-10-27

## Regressão automatizada

- 379 testes Python aprovados;
- 24 testes JavaScript aprovados;
- 11 fluxos Playwright aprovados no Google Chrome;
- `git diff --check` sem erros de espaços ou conflitos.

## Inspeção no Chrome

O teste ponta a ponta iniciou uma instância Flask local isolada, abriu
`/screener.html` no canal Google Chrome e executou a API real, sem simulação.
Foram confirmados:

- 5.000 combinações recebidas;
- oito linhas no quadro do funil;
- 591 exclusões;
- 4.409 combinações aprovadas;
- 30 casos de validação humana;
- seleção de resultado esperado produzindo estado `Conforme`;
- barra horizontal compacta e grades contidas na janela.

O teste encerrou seu servidor automaticamente. Não permaneceram portas de
teste abertas em 4173, 4174 ou 5000.

## Proteções preservadas

- processamento integral continua bloqueado;
- limites continuam identificados como experimentais;
- a validação humana não persiste alterações;
- nenhum acesso ou escrita no PostgreSQL foi necessário;
- PythonAnywhere permanece adiado.

Resultado: Etapa 15 concluída e pronta para commit de segurança mediante
autorização do usuário.
