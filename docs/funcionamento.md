# Funcionamento vigente do Game / MSen

Atualizado em 2026-10-30, após a subetapa 20.16.

Este é o documento funcional canônico. O comportamento confirmado pelo código,
pelas migrações e pelos testes prevalece em caso de divergência.

## 1. Finalidade e estado atual

O MSen importa e armazena resultados da Mega-Sena, calcula grandezas
estatísticas e geométricas, classifica padrões e executa um Screener protegido
para estudar a eliminação de combinações.

O processamento integral das 50.063.860 combinações continua bloqueado. O
Screener opera com amostra reproduzível de 5.000 combinações e somente poderá
usar funções integralmente homologadas e perfis atuais.

No banco local `games`, em 2026-10-30:

- existem 3.069 resultados;
- a matriz de validação possui 200 amostras × 19 critérios = 3.800 provas;
- as 3.800 provas estão aprovadas;
- existem dez perfis operacionais atuais;
- o estado global permanece desatualizado por
  `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`;
- consequentemente, o Screener real recusa a execução até a liberação
  controlada da cobertura.

## 2. Arquitetura executável

```text
frontend HTML/CSS/JavaScript
             |
             v
API Flask em MSen/src/msen/api
             |
             v
serviços, cálculos, geometria, padrões, validação e screener
             |
             v
PostgreSQL (database games)
```

O frontend não acessa o banco diretamente. HTML fica em `frontend/`, CSS em
`frontend/css/` e JavaScript em `frontend/js/`. O backend fica em
`MSen/src/msen/`. O esquema consolidado está em `database/schema_postgresql.sql`
e as alterações incrementais em `database/migrations/`.

## 3. Entrada e atualização de resultados

Resultados entram por planilha `.xlsx` ou inclusão/edição individual. Todos
passam pelas mesmas validações e funções Python. O servidor recebe concurso,
data e seis dezenas; campos derivados nunca são aceitos como fonte externa.

Para cada resultado, o sistema calcula e persiste:

- soma;
- média aritmética;
- mediana;
- desvio-padrão populacional;
- coordenada média;
- análise geométrica, incluindo extensão aberta, perímetro fechado, regiões,
  área e centro de gravidade;
- ocorrências e classificações de padrões implementados.

A importação é incremental: insere concursos novos, reconhece linhas iguais e
separa divergências sem sobrescrever silenciosamente o histórico.

Depois de uma mudança nos resultados, o sistema marca o algoritmo como
desatualizado e recalcula os resumos operacionais sobre todos os resultados
válidos. A chegada de um concurso novo não torna uma função matemática
incorreta e não refaz as 200 provas se assinatura, regra e precisão não mudaram.

Somente backtests futuros usarão corte por concurso ou data; os perfis correntes
sempre representam todo o conjunto disponível.

## 4. Padrões e classificação histórica

`padroes_grupo` guarda os grupos e `padroes_subgrupo` os padrões. Um padrão
pertence a um grupo e seu código possui função Python registrada para se tornar
executável. Cadastrar apenas nome e descrição não cria uma função.

`resultado_classificacao_padrao` registra somente ocorrências reais de padrões.
Desde a migração 010, a classificação histórica não grava uma linha artificial
`SEM_CORRESPONDENCIA`.

Isso não deve ser confundido com a matriz de validação. Nela,
`SEM_CORRESPONDENCIA` é um estado legítimo do resultado esperado ou calculado:
significa que o classificador foi executado corretamente e não identificou
nenhum subgrupo naquela combinação.

As incidências usam as ocorrências reais e o total de sorteios. O Screener
seleciona padrões aprovados cuja incidência seja estritamente menor que o limite
configurado; o valor inicial configurado é 10%.

## 5. Três famílias do Screener

### 5.1 Estatística

Soma, média, mediana e desvio-padrão possuem critérios de homologação. No
funil, soma e média formam uma decisão única porque `média = soma / 6`; mediana
e desvio formam decisões próprias. As faixas operacionais usam média e
desvio-padrão dos 3.069 resultados atuais.

### 5.2 Geometria

Extensão, perímetro, quantidade de regiões, área e coordenadas X/Y do centro
de gravidade são homologadas separadamente. No funil, X e Y compõem uma única
decisão de centro. As funções de produção usam a implementação interna; Shapely
foi usado somente como oráculo independente para produzir e conferir
referências de teste.

### 5.3 Padrões

Os nove padrões atuais, distribuídos em três grupos, são todos validados. Na
execução do Screener, entram somente os padrões homologados selecionados pela
consulta de raridade vigente. Uma combinação que corresponda a um desses
padrões é eliminada; padrão não selecionado não elimina.

## 6. Homologação matemática

As tabelas são:

- `amostras_validacao`: relaciona as 200 combinações com `resultados` sem
  duplicar as dezenas;
- `criterios_validacao`: catálogo das funções, categorias, precisões e
  assinaturas;
- `avaliacoes_validacao`: um par amostra/critério com esperado, calculado,
  assinatura executada, diferença e `S`, `N` ou pendente.

O esperado é produzido independentemente da função testada e registra origem,
revisor e data. O calculado sempre vem da função real resolvida por
`criar_registro_criterios_producao()`.

Comparação:

- inteiro: igualdade exata;
- decimal: arredondamento na precisão contratada;
- padrão: igualdade do estado e, quando identificado, do subgrupo;
- referência ausente ou execução incompleta: pendente;
- igualdade: `S`;
- divergência: `N`.

Uma função somente fica `APROVADO` com `S` nas 200 amostras ativas.

Sincronização do catálogo:

- função nova cria 200 avaliações pendentes;
- mudança apenas da implementação preserva esperados e limpa calculados;
- mudança de regra, tipo, precisão, grupo ou significado invalida também os
  esperados;
- exclusão deliberada remove as avaliações dependentes por cascata;
- toda mudança bloqueia o Screener até nova reconciliação.

## 7. Perfis operacionais atuais

`perfis_operacionais_atuais` possui dez linhas substituíveis: quatro grandezas
estatísticas e seis geométricas. Cada linha guarda quantidade total,
presentes/ausentes, média, desvio-padrão populacional, mínimo, máximo e data.

`estado_algoritmo_selecao` é uma linha única com o flag global, motivo,
quantidade e assinatura SHA-256 do conjunto de resultados, assinatura do
catálogo homologado e datas de atualização/cobertura.

## 8. Trava do Screener

Antes de construir o plano executável, o Screener exige:

1. estado global atualizado;
2. catálogo ativo idêntico ao registro Python de produção;
3. assinaturas de função e regra atuais;
4. todas as avaliações conferidas, executadas e `S`;
5. dez perfis calculados para a quantidade atual de resultados;
6. todos os critérios estatísticos e geométricos cobertos;
7. exatamente os padrões aprovados selecionados pelo limite vigente.

Qualquer função nova, alterada, pendente ou com `N`, filtro ausente/extra,
perfil antigo ou estado global falso bloqueia toda a API. Não existe aprovação
por omissão.

## 9. Página Validação e auditoria

`frontend/auditoria.html` oferece:

- estado global e motivo;
- botão de atualização quando desatualizado;
- modal com progresso real da tarefa;
- totais, filtros e grade paginada de esperado/calculado;
- relatório por função;
- detalhes de cada `N` e hipótese diagnóstica não mutável;
- exportação JSON técnica e CSV seguro.

O JSON possui identificação SHA-256 reproduzível. O CSV neutraliza prefixos de
fórmula de planilha. A IA pode sugerir uma causa para a divergência, mas não
altera automaticamente referência, função ou aprovação.

## 10. Frequência das dezenas

O módulo independente de frequência preserva o que seria conhecido em cada
corte histórico. A configuração inicial começa no concurso 1, forma a primeira
fotografia no concurso 500 e expande o final um concurso por vez. Cada
fotografia contém as 60 dezenas para ocorrência simples, 2VS e 3VS.

`configuracao_frequencia_dezenas` guarda a configuração ativa e sua assinatura.
`geracoes_frequencia_dezenas` isola uma construção completa e identifica a
origem. `historico_frequencia_dezenas` guarda uma linha por geração, corte,
dezena e tipo, sem copiar as seis dezenas de `resultados`.

Atualização:

- primeira carga ou mudança de configuração reconstrói uma geração;
- concursos novos acrescentam somente novos cortes à geração ativa;
- alteração antiga ou lacuna exige reconstrução explícita;
- simulação usa o mesmo motor sem gravar;
- confirmação, execução única, progresso e cancelamento seguro são obrigatórios.

A página `frequencias.html` apresenta configuração gravada e calculada, estado
da base, seis gráficos atuais das 60 dezenas e histórico filtrado por dezena,
evento e período. Intervalos e números previstos de concursos usam gráficos
separados para não misturar unidades.

As ocorrências reais são consultadas diretamente em `resultados`. A avaliação
considera o primeiro evento posterior ao corte, usa limites inclusivos e
censura casos sem futuro conhecido. O erro percentual usa como denominador o
intervalo real entre eventos, não o número absoluto do concurso. O estudo não
ativa filtros do Screener e não promete prever sorteios aleatórios.

## 11. Páginas e APIs vigentes

Páginas: `index.html`, `cadastros.html`, `grupos-padroes.html`, `padroes.html`,
`distribuicoes.html`, `screener.html`, `auditoria.html` e `frequencias.html`.

Rotas centrais desta etapa:

- `POST /api/screener/quadro`;
- `GET /api/validacao/quadro`;
- `GET /api/validacao/relatorio`;
- `GET /api/validacao/exportacao?formato=json|csv`;
- `POST /api/validacao/execucoes`;
- `GET /api/validacao/execucoes/<identificador>`.
- `GET /api/frequencias/estado`;
- `GET /api/frequencias/fotografia-atual`;
- `GET /api/frequencias/serie`;
- `POST /api/frequencias/previa`;
- `POST /api/frequencias/execucoes` e acompanhamento/cancelamento por
  identificador.

As demais APIs vigentes estão indexadas em `docs/INDICE_DOCUMENTACAO.md`.

## 12. Limites atuais

- processamento integral continua bloqueado;
- PythonAnywhere continua adiado;
- o estudo de assertividade das frequências existe, mas o backtest geral do
  Screener ainda não foi implementado;
- a liberação do flag global exige confirmação controlada de cobertura;
- commit e push dependem de autorização específica.
