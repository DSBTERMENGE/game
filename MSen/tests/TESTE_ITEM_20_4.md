# Teste da subetapa 20.4 — repositório das amostras e avaliações

Data: 30/10/2026

## Escopo

Implementação do repositório Python responsável pela inclusão, consulta e
desativação de amostras, sincronização incremental da matriz amostra × critério
e consulta detalhada por relacionamentos. Não foram carregadas as 200 amostras,
cadastrados critérios reais, criadas APIs ou alterado o frontend.

## Arquivos

- `MSen/src/msen/database/validacao_repository.py`;
- `MSen/src/msen/database/__init__.py`;
- `MSen/tests/test_validacao_repository.py`;
- `MSen/tests/validar_repositorio_validacao.py`.

## Comportamento validado

- inclusão transacional da amostra;
- criação automática de uma avaliação pendente para cada critério ativo;
- sincronização geral que cria somente pares faltantes entre amostras e
  critérios ativos;
- repetição da sincronização sem duplicidade;
- preservação de resultados esperados e avaliações existentes;
- critério novo associado somente às amostras ativas;
- desativação da amostra sem apagar suas avaliações;
- consulta das dezenas por `JOIN` com `resultados`;
- consulta de função, grupo e subgrupos esperado/calculado com nomes legíveis
  pelas respectivas tabelas relacionadas;
- modelos de retorno imutáveis e validação de identificadores.

## PostgreSQL temporário

O ensaio aplicou 001–013 em database efêmero e criou duas amostras e dois
critérios para validar a matriz inicial. Em seguida:

- confirmou quatro avaliações iniciais;
- repetiu a sincronização sem inserir linha;
- confirmou que o valor esperado permaneceu intacto;
- resolveu grupo e subgrupo por `JOIN`;
- desativou a segunda amostra sem excluir suas linhas;
- incluiu um terceiro critério e criou somente uma avaliação, correspondente à
  amostra ainda ativa;
- removeu o database temporário ao final.

## Regressão

Resultado: **526 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.4 aprovada. O repositório está pronto para receber o registro de
critérios da 20.5 e a carga das amostras da 20.6. As tabelas do `games`
permanecem sem amostras, critérios ou avaliações nesta subetapa.
