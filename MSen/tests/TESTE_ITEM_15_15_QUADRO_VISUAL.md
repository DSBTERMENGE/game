# Item 15.15 — quadro visual e validação humana

Data: 2026-10-27

## Entrega

Foi criada a página `/screener.html`, acessível pela barra horizontal compacta.
HTML, CSS e JavaScript permanecem em arquivos e pastas separados:

- `frontend/screener.html`;
- `frontend/css/screener.css`;
- `frontend/js/screener.js`.

A página executa apenas a amostra protegida de 5.000 combinações por meio de
`GET /api/screener/quadro`. O quadro apresenta ordem, critério, avaliações,
exclusões, percentual sobre o total inicial e saldo.

## Saída de validação

Foram expostos 30 casos reproduzíveis da mesma amostra. Para cada caso a tela
mostra:

- combinação;
- resultado esperado, a ser indicado pelo usuário;
- resultado obtido;
- primeiro critério que excluiu ou informação de aprovação pelos oito;
- conformidade ou divergência.

Na amostra exibida há 27 aprovações e 3 exclusões, permitindo conferir os dois
tipos de decisão. A escolha do usuário é local à tela e não altera regra,
configuração ou banco.

## Organização visual

- barra de navegação continua em uma linha;
- quadro e validações usam rolagem interna;
- cabeçalhos das tabelas permanecem visíveis;
- a página evita crescimento vertical permanente e admite rolagem horizontal
  quando a largura for insuficiente.

## Testes

- 379 testes Python aprovados;
- 24 testes JavaScript aprovados;
- API testada sem conexão com PostgreSQL;
- página, CSS e JavaScript servidos separadamente;
- processamento integral permanece bloqueado;
- banco não foi escrito.

Resultado: quadro pronto para inspeção local no navegador e validação humana
das decisões experimentais.
