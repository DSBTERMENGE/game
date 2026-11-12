# Funcionamento vigente do Game / MSen

Atualizado em 2026-11-11, após a subetapa 28.5.

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

O fluxo visual é único. `Calcular prévia` atualiza a situação e abre um
diálogo com operação, motivo, período, concursos, linhas estimadas e efeito de
gravação. `Cancelar` não cria tarefa. `Prosseguir` constitui a confirmação
explícita e abre o acompanhamento da operação; não existe botão `Executar`
separado. Uma prévia sem alteração mantém o prosseguimento desabilitado.

A página `frequencias.html` apresenta configuração gravada e calculada, estado
da base, seis gráficos atuais das 60 dezenas e análise histórica filtrada por
dezena, evento e período. O bloco histórico mantém consulta, assertividade e
relatório, mas não repete os gráficos. `Consultar dezena` apresenta a fotografia
numérica final e um quadro **Backtest** com intervalo efetivamente avaliado,
concursos avaliados, acertos, erros e percentual de acerto.

O bloco histórico oferece `Abrir gráficos`, que leva a
`graficos-frequencias.html` preservando dezena, evento e período. A página
auxiliar apresenta um gráfico por linha e retorna ao mesmo bloco com os filtros
atuais. Os eixos X e Y usam escalas independentes calculadas para mostrar todas
as séries. O eixo horizontal identifica os extremos e intervalos de 100
concursos. A altura se adapta à janela para manter cada gráfico integralmente
visível. No gráfico dos intervalos, cada par de ocorrências consecutivas forma
um patamar horizontal: o trecho ocupa os dois concursos reais e sua ordenada é
a diferença entre eles. A mudança de valor usa ligação vertical tracejada;
intervalos consecutivos iguais permanecem contínuos. Mínimo e máximo não são
mais desenhados. A média e as linhas `média − desvio-padrão` e
`média + desvio-padrão` são acumuladas desde o primeiro intervalo real e ficam
na unidade de concursos.

Se o período começa no concurso 500, o primeiro patamar é o intervalo real que
liga a última ocorrência anterior a 500 à primeira ocorrência igual ou
posterior, recortado somente na apresentação. Patamares projetados com menos de
8 pixels recebem losango e haste tracejada; mouse, foco ou clique mostram os
concursos reais e o intervalo sem alterar as coordenadas matemáticas.

O botão `Ajuda` abre um diálogo independente da API. O conteúdo acompanha a
ordem visual da página e explica estado da base, configurações, prévia,
gravação, reconstrução, fotografia atual, série histórica, assertividade, fluxo
recomendado e cuidados. Assim, a orientação permanece acessível mesmo quando o
banco ou o servidor de dados não estiver disponível.

A página auxiliar também possui ajuda própria, cobrindo filtros, significado
dos gráficos principais, unidades, intervalos individuais em patamares,
recorte inicial, média acumulada, marcadores de trechos curtos, escalas
independentes, gráficos auxiliares e retorno.

### 10.1. Leitura dos gráficos de intervalos

O cartão **Evolução dos intervalos** reúne três formas complementares de
examinar os mesmos intervalos históricos da dezena e do tipo de evento
selecionados. Cada gráfico possui um botão `Ajuda`; os dois gráficos auxiliares
abrem, um por vez, no mesmo diálogo reutilizável.

**Evolução dos intervalos** mostra o comportamento ao longo do tempo:

- o eixo horizontal é o número do concurso;
- o eixo vertical é a duração do intervalo, em concursos;
- cada patamar representa a distância entre duas ocorrências consecutivas;
- a média é acumulada com os intervalos conhecidos até cada momento;
- as linhas `média − desvio-padrão` e `média + desvio-padrão` mostram a
  dispersão na mesma unidade da média;
- losango e haste tracejada identificam um intervalo curto demais para ficar
  claramente visível na escala horizontal.

Mouse, foco ou clique no marcador informam os concursos inicial e final e a
duração exata. O gráfico descreve o histórico; média e desvio mudam quando um
novo intervalo termina e não determinam a próxima ocorrência.

**Curva de distribuição** resume quantas vezes cada duração ocorreu. O eixo X
é a duração em concursos e o eixo Y é o percentual das ocorrências com aquela
duração. A distribuição observada é comparada com uma curva normal teórica de
mesma média e mesmo desvio-padrão. Linhas verticais indicam a média e um desvio
abaixo e acima dela. A curva normal é somente uma referência: intervalos são
inteiros e sua distribuição pode ser assimétrica e concentrada em valores
pequenos. Selecionar um ponto informa duração, quantidade e percentual exatos.

**Ocorrências em ordem crescente** ordena todos os intervalos do menor para o
maior, sem eliminar repetições. Os dois eixos vão de 0% a 100%:

- `X(i) = i / N × 100` é o percentual acumulado da ocorrência de ordem `i`
  entre os `N` intervalos;
- `Y(i) = intervalo(i) / maior_intervalo × 100` é a duração relativa ao maior
  intervalo observado.

O quadriculado de 5% serve apenas como referência, e os pontos mantêm seus
percentuais exatos. Durações repetidas formam patamares; um salto mostra que
certas durações intermediárias não ocorreram. O último ponto é sempre
`(100%, 100%)`. Ao selecionar um ponto, a página informa ordem, percentual
acumulado, duração real e percentual do maior intervalo.

Os três gráficos descrevem concentração, dispersão e evolução do histórico.
Eles não classificam automaticamente as dezenas, não alteram filtros do
Screener e não garantem maior probabilidade no concurso seguinte.

As ocorrências reais são consultadas diretamente em `resultados`. A avaliação
considera o primeiro evento posterior ao corte e usa limites inclusivos. Uma
previsão só entra no backtest quando seu limite superior já está coberto pelo
histórico. A primeira faixa que ultrapassa o último concurso encerra a avaliação
daquela dezena; a próxima dezena é independente. O estudo não ativa filtros do
Screener e não promete prever sorteios aleatórios.

## 11. Seleção de dezenas

O módulo `selecao-dezenas.html` é o primeiro de dois screeners. Ele seleciona
dezenas candidatas por recorrência simples; depois, as combinações de seis
dezenas ainda passam pelo Screener de combinações, onde podem ser avaliadas por
2VS, 3VS, estatística, geometria e padrões.

Para uma dezena e um concurso-alvo `C`, usando somente dados até o corte
`C - 1`:

```text
centro = última_ocorrência + média_intervalos + j × desvio_padrão
meia_largura = k × desvio_padrão
limite_inferior = piso(centro - meia_largura)
limite_superior = teto(centro + meia_largura)
```

A dezena é aprovada quando `C` pertence aos limites inclusivos. `k` satisfaz
`0 < k <= 1`; `j` satisfaz `-k <= j <= k`. Desvio zero cria faixa somente no
centro. Sem base suficiente, a dezena recebe `SEM_BASE`. No modo `MAX`, todas
as aprovadas são retornadas; no modo `FIXA`, são retornadas até `N` aprovadas
conforme ranking, sem completar com dezenas fora da faixa.

O backtest começa no concurso 500. Cada alvo é selecionado antes da leitura de
seu resultado e pertence a uma única classe entre zero e seis acertos. O resumo
informa período efetivamente avaliado, quantidade de concursos, tamanhos dos
conjuntos, cobertura, precisão e custo combinatório. Comparações diretas exigem
mesma origem, período, versão e cobertura; caso contrário, a API informa
ressalvas.

A previsão usa o último concurso conhecido `L` como corte e calcula somente o
concurso-alvo `L + 1`. Ela permanece `PENDENTE` até a chegada desse resultado.
Na atualização seguinte, a previsão é conferida sem alterar suas dezenas,
faixas ou ranking; depois disso, uma nova origem pode ser emitida para o
concurso imediatamente seguinte, usando a base atualizada.

As configurações são assinadas e preservadas. O modelo possui
`configuracoes_pesquisa_selecao`, `execucoes_pesquisa_selecao`,
`alvos_pesquisa_selecao` e `avaliacoes_dezenas_pesquisa`. Jogos autorizados são
armazenados em `lotes_jogos_selecao` e `jogos_selecao_dezenas`. O alvo
referencia `resultados` por chave, sem copiar as seis dezenas.

A interface exige prévia e confirmação antes do backtest. Durante a execução,
o modal mostra etapa, quantidade, percentual, duração e cancelamento seguro.
Somente uma execução pode permanecer ativa. Para jogos, a página calcula
`C(N,6)` antes de materializar; gravação exige autorização e volume elevado
exige confirmação adicional.

O fluxo recomendado é:

1. escolher ou preencher uma configuração;
2. calcular a prévia;
3. executar o backtest;
4. comparar somente pesquisas equivalentes;
5. calcular e preservar a previsão do próximo concurso;
6. inspecionar o detalhe e o custo antes de formar jogos.

Maior quantidade de acertos pode decorrer apenas de um conjunto maior e mais
caro. O módulo mede comportamento histórico e não garante sorteios futuros.
Contratos detalhados: `docs/CONTRATO_SELECAO_DEZENAS.md`,
`docs/CONTRATO_BACKTEST_SELECAO_DEZENAS.md`,
`docs/MODELO_PESQUISA_SELECAO_DEZENAS.md` e
`docs/API_SELECAO_DEZENAS.md`.

## 12. Páginas e APIs vigentes

Páginas: `index.html`, `cadastros.html`, `grupos-padroes.html`, `padroes.html`,
`distribuicoes.html`, `screener.html`, `auditoria.html`, `frequencias.html`,
`graficos-frequencias.html`, `selecao-dezenas.html` e
`gestao-desenvolvimento.html` e `ajuda.html`.

A Ajuda central possui índice lateral, busca por títulos, aliases e conteúdo,
links diretos por tópico e retomada do último assunto consultado no navegador.
O item `Ajuda` ocupa a última posição do menu principal. Os tópicos que ainda
aguardam implantação funcional são identificados como limitações. Todas as
páginas vigentes possuem explicação operacional central. Os acessos contextuais
de Frequência, Gráficos, Seleção e Gestão abrem diretamente o tópico
correspondente e oferecem retorno à origem quando ela é uma página interna
conhecida. Os antigos modais locais não são mais executáveis.

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
- `GET|POST /api/selecao-dezenas/configuracoes`;
- `POST /api/selecao-dezenas/previa`;
- `POST /api/selecao-dezenas/backtests` e acompanhamento ou
  cancelamento por identificador do cálculo, sem persistir o relatório;
- `POST /api/selecao-dezenas/previsoes`;
- `GET|POST /api/selecao-dezenas/alvos/<id>/jogos[/previa]`.
- `GET|POST /api/gestao-desenvolvimento` e operações específicas de consulta,
  atualização, histórico, arquivamento e desarquivamento.

As demais APIs vigentes estão indexadas em `docs/INDICE_DOCUMENTACAO.md`.

A Gestão do desenvolvimento usa o CRUD navegável reutilizável. A inclusão de
configurações da Seleção de dezenas reutiliza o fluxo menor de gravação
confirmada, sem alterar a regra de que uma configuração salva é imutável.
Cancelar ou apenas conferir não chama a API de criação.

Na Gestão do desenvolvimento, o usuário escolhe a data do registro em um
calendário. A Situação do trabalho permanece; não existem Prioridade, Origem ou
escolha de ordenação. A lista segue sempre a ordem técnica de criação.

## 13. Limites atuais

- processamento integral continua bloqueado;
- PythonAnywhere continua adiado;
- o estudo de assertividade das frequências existe, mas o backtest geral do
  Screener ainda não foi implementado;
- a Seleção de dezenas possui backtest próprio, mas seu resultado não constitui
  garantia de desempenho futuro;
- a liberação do flag global exige confirmação controlada de cobertura;
- commit e push dependem de autorização específica.
