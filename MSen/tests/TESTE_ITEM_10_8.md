# Evidências do Item 10.8 — páginas e menu horizontal

Data: 2026-10-27.

## Implementação

O Painel foi separado dos cadastros. Foram criadas as páginas:

- `/` — Painel existente;
- `/cadastros.html` — visão geral dos cadastros;
- `/grupos-padroes.html` — estrutura reservada ao Item 10.9;
- `/padroes.html` — estrutura reservada ao Item 10.10.

Todas usam uma barra horizontal de 2,8 rem com marca compacta, botão Voltar,
acesso ao Painel, submenu suspenso Cadastros e identificação da página atual. O
submenu usa posicionamento absoluto e não cria uma segunda linha permanente.

O modal antigo foi retirado do Painel. Seus arquivos CSS e JavaScript foram
preservados para adaptação na página própria durante o Item 10.10.

## Testes

- 20 testes de frontend: aprovados;
- 4 fluxos no Google Chrome: aprovados;
- navegação Painel → Cadastros → Grupos → Voltar → Padrões: aprovada;
- carregamento, seleção, voo, importação e mancha do Painel: preservados;
- Flask retornou HTTP 200 para as quatro páginas;
- nenhum teste acessou ou alterou PostgreSQL.
