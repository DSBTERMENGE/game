# Teste da subetapa 20.13 — página de Validação e auditoria

Data: 30/10/2026

## Estado

**Concluída.** A página reservada passou a apresentar o estado global, resumo,
filtros, avaliações paginadas e atualização pelo motor assíncrono.

## API de consulta

`GET /api/validacao/quadro` aceita:

- categoria;
- função/critério;
- grupo;
- subgrupo esperado ou calculado;
- situação `S`, `N` ou pendente;
- página e limite de 1 a 100 linhas.

A resposta contém o estado global, resumo das 3.800 avaliações, opções de
filtro, paginação e linhas detalhadas. As dezenas são obtidas por `JOIN` com
`resultados`; não existe cópia na matriz de validação. Grupo e subgrupos esperado
e calculado também são obtidos pelos relacionamentos atuais.

Parâmetros inválidos retornam HTTP 400. A paginação impede carregar toda a
matriz no navegador de uma vez.

## Interface

A página mostra:

- `Algoritmo de seleção de combinações atualizado` ou `desatualizado`;
- motivo técnico atual e botão de atualização somente quando desatualizado;
- totais geral, aprovado, reprovado e pendente;
- filtros por categoria, função, grupo, subgrupo e situação;
- concurso, seis dezenas, categoria, função/filtro, grupo, esperado, calculado
  e aprovação `S/N`;
- paginação de 50 linhas e estado vazio;
- rolagem interna da grade e cabeçalho fixo.

O botão reutiliza o modal da 20.12 e recarrega o quadro após o término. A
construção usou `textContent`, sem inserir dados do banco como HTML.

## Verificação no banco local

A consulta somente leitura confirmou:

- 3.800 avaliações totais e aprovadas;
- zero reprovadas e pendentes;
- 19 critérios, 3 grupos e 9 subgrupos disponíveis nos filtros;
- filtro `PAD_PD_003` + `PG_001`: 200 linhas, 40 páginas de 5, com estado
  esperado/calculado e `S` coerentes.

O estado exibido é desatualizado com motivo
`HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`, conforme as etapas anteriores.

## Testes

- **557 testes Python aprovados**;
- **36 testes Node aprovados**;
- **2 fluxos Chromium aprovados**.

O navegador verificou modal e recarga, estado global, resumo, dezenas, filtros,
grade e paginação em 1280×800 e 390×844. Permaneceram somente os avisos
preexistentes de arquivos frontend abertos e módulos Node sem `type: module`.

## Resultado

A subetapa 20.13 está encerrada. A 20.14 poderá ampliar a visão de divergências
com resumo por função e diagnóstico detalhado de cada `N`, mediante autorização
separada.
