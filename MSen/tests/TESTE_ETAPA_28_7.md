# Evidência — subetapa 28.7 e encerramento da Etapa 28

Data: 11/11/2026

## Conferência

- conteúdo sensível confrontado com código, contratos e testes;
- busca por títulos, aliases e conteúdo;
- navegação lateral, links diretos, foco e teclado;
- tratamento seguro de tópico ausente e origem externa;
- retorno à página de origem;
- responsividade em tela estreita;
- destinos contextuais das páginas e dos três gráficos;
- remoção das cópias editoriais locais.

Não foi encontrada nova lacuna funcional que exigisse registro na Gestão do
desenvolvimento. A divergência de portas fixas pertencia somente à
infraestrutura dos testes e foi corrigida nos testes.

## Resultados

- `npm run test:frontend`: 114 testes aprovados;
- testes Python direcionados a resultados, Frequência, Seleção, Screener e
  Gestão: 70 aprovados;
- `PLAYWRIGHT_TEST_PORT=4187 npm run test:browser`: 47 testes Chromium aprovados;
- `git diff --check`: sem erro de espaço em branco após a correção final;
- banco de dados não acessado nem alterado.
