# Visão geral

## Objetivo

O MSen será uma aplicação para importar, organizar e analisar históricos de
resultados da Mega-Sena. O escopo será refinado conforme as funcionalidades
forem definidas.

## Organização do repositório

- `MSen`: aplicação Python, testes e dados utilizados por ela;
- `docs`: documentação estável sobre o produto e sua arquitetura;
- `notas`: ideias, pendências e decisões ainda em elaboração;
- `frontend`: interface HTML, JavaScript e folhas de estilo, ainda não integrada
  à aplicação Python;

## Princípios iniciais

1. Separar regras de negócio da leitura de arquivos e da interface.
2. Proteger os dados originais contra alterações acidentais.
3. Cobrir cálculos e transformações importantes com testes automatizados.
4. Registrar decisões que afetem a arquitetura ou o formato dos dados.

O fluxo funcional detalhado está documentado em `docs/funcionamento.md`.
O planejamento consolidado e legível como texto simples está em
`docs/PLANO_FUNCIONALIDADES.txt`.
