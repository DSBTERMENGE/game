# Teste da subetapa 20.0 — contrato de homologação das funções

Data: 29/10/2026

## Escopo

Formalização documental do modelo de validação. Nenhum DDL, código de produção,
API, frontend ou banco de dados foi criado ou alterado.

## Decisões verificadas

- as amostras relacionam `resultados` por `id_resultado` sem repetir dezenas;
- `id_resultado` será PK/FK com exclusão em cascata;
- cada avaliação associa amostra e função;
- valores esperados são independentes e protegidos;
- funções reais preenchem somente valores calculados;
- padrões relacionam grupo e subgrupos esperado/calculado com nomes por `JOIN`;
- `aprovado` usa `NULL`, `S` e `N` sem confundir pendência com divergência;
- `SEM_CORRESPONDENCIA` é resultado válido e explícito de classificador;
- alteração de implementação preserva esperado e invalida o cálculo;
- alteração da regra invalida também o esperado;
- inclusão e exclusão são incrementais, com cascatas controladas;
- qualquer pendência ou `N` bloqueia a função no Screener;
- o relatório resume funções e detalha cada divergência;
- análise da IA é diagnóstica e não modifica aprovação automaticamente.

## Exemplos conferidos

O contrato contém exemplos aprovados de:

1. função estatística com 200 resultados conformes;
2. função geométrica com uma divergência e estado reprovado;
3. classificador com nomes legíveis de grupo e subgrupos;
4. estado pendente separado de `SEM_CORRESPONDENCIA`.

## Resultado

Contrato registrado em `docs/CONTRATO_HOMOLOGACAO_FUNCOES.md`. A subetapa 20.0
está concluída somente em documentação. A subetapa 20.1, destinada ao DDL das
amostras, permanece sem autorização.
