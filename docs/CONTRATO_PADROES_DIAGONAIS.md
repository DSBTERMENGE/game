# Contrato dos padrões de assinaturas diagonais

Este documento define o estudo das combinações pelas diagonais que cruzam
dezenas de referência. A função de análise identifica assinaturas geométricas;
a raridade continua sendo determinada posteriormente pela incidência e pela
configuração do sistema.

## Inclinações

- `D`, inclinada à direita: passo numérico `±9`;
- `E`, inclinada à esquerda: passo numérico `±11`.

Os passos são uma consequência das coordenadas, não um substituto para elas.
Cada diagonal deve ser construída respeitando os limites de dez colunas e seis
linhas do volante, sem atravessar bordas indevidamente.

## Dezenas de referência

As seis dezenas são ordenadas numericamente. São testadas como referências as
posições intermediárias `P2`, `P3`, `P4` e `P5`.

Para cada referência são construídas as duas diagonais completas que passam
por seu centro. Também são registrados os comprimentos totais dessas diagonais.
Uma referência participa do estudo principal `xDyE` somente quando ambas as
diagonais possuem pelo menos quatro posições. Isso impede que diagonais de
canto, limitadas a uma, duas ou três posições, criem assinaturas artificialmente
pequenas. Uma combinação sem referência elegível recebe o diagnóstico
`SEM_REFERENCIA_LONGA`, e não `0D0E`.

## Formação da assinatura

A própria dezena de referência não entra nas quantidades. Entre as outras cinco
dezenas são contadas:

- `x`: quantas pertencem à diagonal `D` da referência;
- `y`: quantas pertencem à diagonal `E` da referência.

A assinatura é escrita como `xDyE`. Exemplos:

- `0D0E`: nenhuma das outras cinco dezenas pertence às duas diagonais;
- `3D0E`: três estão na diagonal direita e nenhuma na esquerda;
- `0D4E`: quatro estão na diagonal esquerda e nenhuma na direita;
- `2D2E`: duas estão em cada inclinação e a sexta dezena está fora delas;
- `0D5E`: todas as outras cinco estão na diagonal esquerda, totalizando seis
  dezenas nessa diagonal quando se inclui a referência.

Como só existem cinco dezenas além da referência, toda assinatura válida deve
obedecer a `x + y <= 5`. Assim, `2D4E` e `0D6E` não são assinaturas possíveis
para uma única referência.

## Posição relativa dos pontos

A assinatura considera pertencimento às diagonais completas. Ela não considera:

- de que lado da referência cada dezena está;
- se a aparência é `V`, `V` invertido ou `X`;
- se existem posições vazias entre duas dezenas alinhadas;
- a distância entre as dezenas sobre a diagonal.

Essas aparências são visualizações diferentes da mesma relação geométrica e não
criam subtipos. Por exemplo, toda disposição com duas companheiras em cada
inclinação pertence a `2D2E`.

## Perfil de uma combinação

A análise registra separadamente os resultados de `P2` a `P5`, incluindo a
dezena de referência e os comprimentos das duas diagonais. Ela também consolida
o conjunto de assinaturas encontrado na combinação.

Se a mesma assinatura aparecer em mais de uma referência, a combinação contém
essa assinatura apenas uma vez para fins de incidência. A posição permanece
disponível somente como evidência de auditoria.

## Estudo de incidência

Uma amostra aleatória deverá:

1. conter combinações únicas de seis dezenas;
2. usar uma semente fixa e registrada;
3. calcular todas as referências elegíveis de cada combinação;
4. contar cada assinatura no máximo uma vez por combinação;
5. calcular `ocorrências / tamanho da amostra × 100`;
6. apresentar também quantas combinações ficaram sem referência longa.

A amostra estima frequências. Ela não decide a raridade e não altera o limite
configurado. Assinaturas próximas ou abaixo do limite poderão ser estudadas em
amostras maiores, nos resultados históricos ou no universo completo.

## Modelo de execução no Screener

Este estudo constitui um único filtro cadastral. As assinaturas não serão
transformadas em 21 funções detectoras nem em 21 registros obrigatórios de
padrão. A proposta anterior de separar as inclinações ou cadastrar uma função
por assinatura está substituída por este modelo.

O cadastro deverá identificar:

- nome do filtro, como `Arranjos diagonais`;
- tipo de avaliação categórica percentual;
- função analisadora;
- descrição integral do procedimento;
- comando de consulta, como `Ver tuplas`, para apresentar a distribuição
  histórica calculada automaticamente.

Nenhuma pessoa digita códigos ou percentuais das assinaturas. A mesma função
produz os códigos usados na base histórica e nas combinações inspecionadas.

### Preparação histórica

No início da execução do Screener, uma função separada aplica o analisador a
todos os registros da tabela `resultados`. Ela monta em memória uma tabela de
pares equivalentes a:

```text
(`0D0E`, 73,541870%)
(`1D2E`,  2,574128%)
(`2D2E`,  0,097752%)
```

Essa tabela é calculada uma vez por execução e permanece imutável durante o
funil. Ela não é recalculada para cada combinação e não exige persistir as
combinações analisadas.

### Avaliação de uma combinação

Para cada combinação de seis dezenas, o analisador devolve as assinaturas
encontradas nas referências elegíveis. Cada assinatura é procurada na tabela
histórica em memória.

- percentual estritamente menor que o limite do Screener: assinatura rara;
- percentual igual ou maior que o limite: assinatura comum;
- assinatura ausente da tabela histórica: percentual considerado igual a
  zero, pois não ocorreu nos resultados analisados.

A combinação é eliminada quando ao menos uma de suas assinaturas é rara. Ela
prossegue somente quando todas as assinaturas encontradas possuem percentual
igual ou superior ao limite.

`SEM_REFERENCIA_LONGA` deve ser tratado pelo mesmo processo como uma categoria
calculada, para que sua incidência histórica também possa ser comparada ao
limite em vez de depender de uma decisão implícita.

### Evidências no relatório

O filtro produz uma única decisão final para a combinação, acompanhada de:

- assinaturas calculadas;
- percentual histórico de cada assinatura;
- limite utilizado;
- comparação realizada;
- assinatura ou assinaturas que determinaram a exclusão;
- quantidade e denominador dos resultados históricos.

O comando `Ver tuplas` poderá apresentar os mesmos pares usados pela execução,
incluindo ocorrências, percentual e quantidade total de resultados. A tela não
mantém uma segunda fórmula nem uma cópia manual desses dados.

## Descrição obrigatória no cadastro

O registro do filtro no banco deverá conter uma descrição funcional suficiente
para que sua manutenção não dependa da memória de quem o implementou. O texto
deverá preservar, no mínimo, as seguintes informações:

> Analisa as dezenas intermediárias P2 a P5 e calcula assinaturas xDyE, em que
> D representa a diagonal de passo 9 e E a diagonal de passo 11. A referência
> não entra na contagem; V, V invertido e X não criam categorias diferentes.
> Antes do funil, a mesma função calcula nos resultados históricos os pares
> arranjo/percentual e os mantém em memória. Para cada combinação, os arranjos
> calculados são comparados com essa tabela e com o limite global informado no
> Screener. Qualquer arranjo abaixo do limite elimina a combinação; arranjo sem
> ocorrência histórica equivale a 0%. Use “Ver tuplas” para consultar a tabela
> histórica usada pela execução.

Esse conteúdo pode receber melhorias de redação na interface, mas não pode ser
reduzido a uma descrição genérica como “verifica diagonais”. Mudança da regra,
do significado de D/E, das referências ou da política de ausência exige
atualização simultânea desta documentação, da descrição no banco e dos testes.

## Contrato aplicado ao banco

A avaliação categórica pertence ao grupo, pois uma única função analisa todas
as assinaturas. A migração 034 acrescentou a `padroes_grupo`:

| Campo | Tipo | Regra |
|---|---|---|
| `tipo_avaliacao` | `VARCHAR(30)` | Obrigatório; padrão `BOOLEANO` |
| `funcao_analisadora` | `VARCHAR(500)` | Nulo para grupo booleano; obrigatório para grupo categórico |

Valores inicialmente permitidos para `tipo_avaliacao`:

- `BOOLEANO`: funcionamento atual, com `funcao_detectora` em cada padrão;
- `CATEGORICO_PERCENTUAL`: uma função do grupo retorna categorias que são
  comparadas com uma distribuição histórica calculada em memória.

As restrições devem garantir:

```text
BOOLEANO               → funcao_analisadora é nula
CATEGORICO_PERCENTUAL  → funcao_analisadora é texto preenchido
```

O grupo diagonal deverá ficar com:

```text
grupo_cod          = PG_004
grupo_nome         = Arranjos diagonais
tipo_avaliacao     = CATEGORICO_PERCENTUAL
funcao_analisadora = msen.padroes.diagonais.analisar_assinaturas_diagonais
```

`PD_013` permanecerá como único item cadastral desse grupo, com nome
`Configurações diagonais xDyE`, descrição funcional completa e
`funcao_detectora` nula. Sua ausência de função booleana não significa que o
filtro esteja pendente: a disponibilidade vem da função analisadora do grupo.

Os demais grupos recebem `BOOLEANO` e continuam usando as funções detectoras
individuais já persistidas. A migração não altera sua execução.

Não serão criados:

- campos de coordenadas;
- colunas na tabela `resultados`;
- tabela persistente com as tuplas;
- registros para cada combinação testada;
- 21 padrões ou funções independentes.

A distribuição `arranjo → ocorrências/percentual` será uma fotografia imutável
em memória durante cada execução. O relatório e `Ver tuplas` usam essa mesma
fotografia, sem fórmula paralela.

## Reorganização exata do catálogo

A migração localiza os registros pelos códigos estáveis, nunca pelos IDs
internos observados numa instalação específica.

### Registros mantidos e transformados

`PG_004` será mantido com o mesmo `id_grupo` e `grupo_cod`, recebendo:

```text
grupo_nome         = Arranjos diagonais
tipo_avaliacao     = CATEGORICO_PERCENTUAL
funcao_analisadora = msen.padroes.diagonais.analisar_assinaturas_diagonais
```

Sua descrição explicará que o filtro calcula P2–P5, produz assinaturas `xDyE`,
monta a distribuição histórica em memória e compara todas as assinaturas da
combinação com o limite global do Screener.

`PD_013` será mantido com o mesmo `id_padrao` e `padrao_cod`, associado a
`PG_004`, recebendo:

```text
padrao_nome       = Configurações diagonais xDyE
funcao_detectora  = NULL
```

Sua descrição conterá o procedimento obrigatório definido neste contrato e
informará o comando `Ver tuplas`.

### Registros removidos

Serão excluídos os padrões ainda não implementados:

```text
PD_014, PD_015, PD_016, PD_017, PD_018, PD_019,
PD_020, PD_021, PD_022, PD_023, PD_024, PD_025, PD_026
```

Depois da remoção de seus sete padrões, `PG_006` será excluído. Nenhum registro
será transferido entre grupos. Os códigos removidos não serão reutilizados e as
sequências do PostgreSQL não serão reduzidas.

Partindo do catálogo atual, a reorganização reduz o total de 11 para 10 grupos
e de 49 para 36 padrões.

### Pré-condições de segurança

A migração aborta integralmente se:

- `PG_004`, `PG_006` ou qualquer padrão de `PD_013` a `PD_026` estiver ausente;
- algum padrão a remover possuir função, ocorrência, denominador ou percentual;
- houver classificação histórica, critério ou avaliação referenciando esses
  grupos e padrões;
- `PD_013` estiver associado a outro grupo;
- os nomes existentes indicarem que os códigos já foram reaproveitados por uma
  alteração posterior.

A migração histórica 033 não será editada. Em instalação nova, ela cria o
catálogo anterior e a migração seguinte executa esta reorganização, preservando
um histórico reproduzível.

## Estado verificado após a migração 034

Em 17/11/2026, a migração 034 foi validada primeiro em banco temporário e,
depois, aplicada ao banco local `games`. A auditoria confirmou:

- 10 grupos e 36 padrões no catálogo;
- `PG_004` com tipo `CATEGORICO_PERCENTUAL` e função analisadora cadastrada;
- `PD_013` como único padrão de `PG_004`, sem função detectora booleana;
- ausência de `PG_006` e dos padrões `PD_014` a `PD_026`;
- segunda execução do executor sem reaplicação da migração;
- os mesmos nomes, descrições e totais nas APIs usadas pela página
  `grupos-padroes.html`.

Esse estado cadastral não significa que o filtro esteja operacional no
Screener. A função analisadora, a fotografia histórica em memória, a decisão
do funil e a visualização `Ver tuplas` ainda precisam ser implementadas e
validadas em etapas próprias.
