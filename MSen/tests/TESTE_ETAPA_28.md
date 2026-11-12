# Evidência da etapa 28

Data: 11/11/2026.

## Alterações

- controles de localização e filtros horizontais em telas largas;
- `Pesquisar pelo título` substituído por `Localizar`;
- títulos existentes oferecidos para seleção e pesquisa por trecho;
- primeiro resultado aberto automaticamente;
- `Mostrar arquivados` renomeado para `Consultar arquivados`;
- reorganização responsiva em telas menores.
- formulário com quatro larguras reutilizáveis: curta, média, larga e total;
- Tipo, Prioridade, situações e Origem não ocupam mais a largura reservada aos
  títulos e textos longos.
- o formulário foi movido para baixo da lista e da paginação;
- o campo Tipo acompanha a margem esquerda do botão Anterior;
- as duas primeiras linhas usam intervalo horizontal uniforme de 16 pixels.
- primeira linha do formulário: Tipo, Título, Prioridade e Situação do trabalho;
- segunda linha: Situação da publicação, Origem e Página relacionada;
- terceira linha: Descrição em largura total e com nove linhas de altura.

## Validação

- 114 testes unitários do frontend aprovados;
- teste Playwright aprovado no Chrome com largura de 1900 pixels;
- oito controles permaneceram na mesma linha;
- o navegador confirmou que Tipo e Prioridade são mais estreitos que Título e
  Descrição;
- o navegador mediu alinhamento inicial com tolerância de borda de 2 pixels e
  intervalos uniformes, sem controles encavalados;
- abertura automática, localização por `contém` e zero gravações confirmadas;
- servidor isolado e respostas simuladas, sem alterar o banco de dados.

Nenhuma migração, publicação, commit ou push foi executado.
