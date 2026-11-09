# Evidência da subetapa 23.12 — Matriz completa de testes

> Registro histórico: os cenários de horizonte e previsões futuras desta
> matriz foram substituídos na Etapa 24. A migração 023 e a matriz atual
> validam somente `CA = último cadastrado + 1`.

## Resultado geral

Todos os níveis da Seleção de dezenas foram exercitados sem falhas:

- **674 testes Python**;
- **86 testes unitários do frontend**;
- **36 testes no Chrome por Playwright**;
- **6 validadores integrados**, com databases PostgreSQL efêmeros quando havia
  persistência envolvida.

## Rastreabilidade dos requisitos

### Proteção temporal

O backtest do concurso `C` usa corte `C - 1`. O motor não recebe o resultado do
alvo durante a seleção. O ensaio integrado confirmou o concurso 500 calculado
somente com os resultados 1 a 499.

### Matemática de seleção

Foram confirmados:

- largura da faixa por `k`;
- deslocamento do centro por `j`, limitado a `-k <= j <= k`;
- arredondamento do limite inferior para baixo e do superior para cima;
- limites inteiros inclusivos;
- desvio zero, aprovando apenas o centro;
- estado `SEM_BASE` quando a dezena não possui histórico suficiente;
- ranking determinístico e modos `MAX` e `FIXA`.

### Backtest e pesquisa

- classes de zero a seis acertos mutuamente exclusivas;
- soma das classes igual à quantidade de concursos avaliados;
- cancelamento e retomada sem duplicar alvos;
- 60 avaliações por alvo;
- pesquisas originais preservadas;
- comparação somente com origem, período, versão e cobertura equivalentes.

### Previsões futuras

O ensaio integrado emitiu previsões para 506 e 507 usando corte 505. Depois da
inserção do resultado 506:

- a previsão 506 passou de `PENDENTE` para `AVALIADO`;
- as dezenas originalmente emitidas permaneceram inalteradas;
- foi criada uma nova origem com corte 506 para 507 e 508;
- as duas previsões do concurso 507 foram preservadas, cada uma com seu corte.

### Formação de jogos

- `C(60,6) = 50.063.860` sem materialização antecipada;
- sete dezenas geram sete jogos;
- jogos únicos e em ordem lexicográfica determinística;
- gravação e exportação recusadas sem autorização;
- confirmação adicional exigida para volume elevado;
- vínculo entre jogos, alvo, pesquisa e configuração preservado no banco.

### API e navegador

Foram validados contratos HTTP, erros controlados, prévia, confirmação,
progresso, cancelamento, previsão pendente, relatório 0–6, detalhes, comparação
e prévia combinatória. A suíte completa do navegador incluiu também os demais
módulos do sistema.

## Não regressão da Frequência das dezenas

Todos os testes unitários e de navegador da Frequência das dezenas passaram,
incluindo atualização, reconstrução, simulação, gráficos, ajuda, responsividade
e retorno entre páginas. Nenhuma regra desse módulo foi modificada.

## Operação segura

Os databases temporários foram removidos pelos validadores. Nenhum dado de
pesquisa foi gravado no banco local persistente, nenhum servidor foi iniciado,
nenhuma porta foi aberta e nenhum commit ou push foi realizado.
