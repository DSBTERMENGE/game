# Teste da subetapa 17.1 — catálogo dos parâmetros

## Escopo

- documentar os dez parâmetros estatísticos e geométricos já disponíveis;
- confrontar funções Python, colunas e precisões com o catálogo;
- registrar dependências e cuidados de interpretação;
- não alterar banco, API, interface ou screener.

## Verificações automatizadas

O arquivo `test_catalogo_parametros_analise.py` confirma:

1. presença única dos dez códigos no catálogo;
2. existência das sete funções reais que produzem os valores;
3. correspondência das dez colunas e tipos no esquema PostgreSQL;
4. registro da equivalência entre soma e média;
5. distinção entre o desvio das seis dezenas e um futuro desvio histórico.

## Resultado

- 4 testes específicos aprovados.
- 414 testes Python de regressão aprovados.
- O primeiro comando de regressão, executado indevidamente a partir da raiz do
  repositório, não encontrou `wsgi` e `tests`; repetido no diretório `MSen`, com
  o contexto correto do projeto, passou integralmente.
- Foram emitidos apenas avisos preexistentes de arquivos do screener não
  fechados por um teste; eles não causaram falha.
- Banco, API, interface e regras do screener permaneceram inalterados.
