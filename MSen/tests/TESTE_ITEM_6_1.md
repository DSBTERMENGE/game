# Teste do Item 6.1

Data: 2026-10-26

## Decisão funcional

- dois ou mais resultados: navegação circular;
- um resultado: seletor e mancha habilitados, navegação e voo desabilitados;
- nenhum resultado: todos os controles dependentes dos dados desabilitados.

## Testes do painel

Comando:

```text
node --test frontend/tests/painel_navegacao.test.mjs
```

Resultado: 5 testes aprovados.

Casos cobertos:

- presença dos controles obrigatórios no HTML;
- seletor de arquivo restrito a `.xlsx`;
- mensagem e controles quando não há resultados;
- exibição e controles com um resultado;
- seleção direta pelo seletor;
- Anterior no primeiro seleciona o último;
- Próximo no último seleciona o primeiro.

O teste usa o executor nativo do Node.js 22 e uma implementação DOM controlada,
sem instalar dependências JavaScript ou acessar rede.

## Regressão Python

Os 137 testes Python permaneceram aprovados. Nenhum banco foi modificado e o
PythonAnywhere não foi acessado.
