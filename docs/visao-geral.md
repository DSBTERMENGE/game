# Visão geral

## Objetivo

O MSen é uma aplicação local para importar, organizar e analisar históricos de
resultados da Mega-Sena, homologar suas funções matemáticas e executar um
Screener protegido em três famílias.

## Organização do repositório

- `MSen`: aplicação Python, testes e dados utilizados por ela;
- `docs`: documentação estável sobre o produto e sua arquitetura;
- `notas`: ideias, pendências e decisões ainda em elaboração;
- `frontend`: interface HTML, JavaScript e CSS integrada à API Flask;

## Princípios iniciais

1. Separar regras de negócio da leitura de arquivos e da interface.
2. Proteger os dados originais contra alterações acidentais.
3. Cobrir cálculos e transformações importantes com testes automatizados.
4. Registrar decisões que afetem a arquitetura ou o formato dos dados.

O fluxo funcional detalhado está documentado em `docs/funcionamento.md`.
O índice dos documentos vigentes está em `docs/INDICE_DOCUMENTACAO.md`.
O planejamento operacional vigente está em `PLANO_ETAPAS_E_TESTES.md`.
