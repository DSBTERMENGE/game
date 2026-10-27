# Evidências do Item 10.9 — grade de grupos de padrões

Data: 2026-10-27.

## Implementação

A página `/grupos-padroes.html` recebeu grade CRUD conectada à API de grupos.
HTML, CSS e JavaScript permanecem separados.

Para economizar espaço:

- título, nome, descrição e botão Adicionar ocupam uma barra horizontal;
- a página usa linhas `auto auto minmax(0, 1fr)`;
- a grade ocupa o espaço vertical restante;
- cabeçalho da tabela permanece fixo;
- rolagens vertical e horizontal ficam contidas na grade;
- código e ações possuem colunas estreitas;
- nome e descrição usam a largura restante;
- em tela estreita, a barra usa rolagem horizontal em vez de várias linhas.

## Testes

- 21 testes de frontend: aprovados;
- fluxo CRUD no Google Chrome: aprovado;
- carregamento, inclusão, edição e exclusão confirmados;
- confirmação antes da exclusão confirmada;
- tentativa de excluir grupo ocupado manteve a linha e exibiu a mensagem da API;
- nenhum teste acessou o PostgreSQL.
