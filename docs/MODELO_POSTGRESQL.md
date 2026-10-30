# Modelo PostgreSQL planejado

## Situação

- Item do plano: 1.3.
- Estado: aprovado e concluído em 2026-10-26.
- Database planejado: `games`.
- Este documento não altera o DDL nem executa comandos no PostgreSQL.

## Convenções

- nomes físicos em português, minúsculos e `snake_case`;
- chaves internas com prefixo `id_`;
- datas e horas técnicas com `TIMESTAMPTZ`;
- cálculos decimais com tipos `NUMERIC`, nunca `REAL` ou `DOUBLE PRECISION`;
- valores calculados pelo Python com `Decimal` e `ROUND_HALF_UP`, arredondando
  somente o resultado final conforme o contrato aprovado;
- restrições nomeadas para facilitar diagnóstico e migrações;
- nenhum campo genérico reservado para uso futuro.

## Visão geral

```text
resultados
  1 linha por apresentação/concurso
        |
        | prim_oco e ult_oco referenciam numero_ap
        v
frequencia_de_resultado
  1 linha derivada para cada dezena de 01 a 60

schema_migrations
  controla quais alterações de estrutura já foram aplicadas
```

## 1. Tabela `resultados`

### Finalidade

Guardar os seis valores originais de cada apresentação e os cálculos próprios
daquela linha. A definição funcional completa está em
`docs/DICIONARIO_DADOS_RESULTADOS.md`.

### Campos planejados

| Campo | Tipo PostgreSQL | Nulo | Regra principal |
|---|---|---:|---|
| `id_resultado` | `BIGINT GENERATED ALWAYS AS IDENTITY` | não | chave primária |
| `data_resultado` | `DATE` | não | data válida |
| `numero_ap` | `INTEGER` | não | positivo e único |
| `res_01` | `SMALLINT` | não | 1 a 60 |
| `res_02` | `SMALLINT` | não | 1 a 60 |
| `res_03` | `SMALLINT` | não | 1 a 60 |
| `res_04` | `SMALLINT` | não | 1 a 60 |
| `res_05` | `SMALLINT` | não | 1 a 60 |
| `res_06` | `SMALLINT` | não | 1 a 60 |
| `soma_res` | `SMALLINT` | não | 21 a 345 |
| `media_aritmetica_res` | `NUMERIC(10,6)` | não | 1 a 60 |
| `mediana_res` | `NUMERIC(4,1)` | não | 1 a 60 |
| `desvio_padrao_media` | `NUMERIC(10,6)` | não | maior ou igual a zero |
| `media_coordenada_x` | `NUMERIC(7,6)` | não | 0 a 9 |
| `media_coordenada_y` | `NUMERIC(7,6)` | não | 0 a 5 |
| `versao_calculo` | `SMALLINT` | não | inicialmente 1 |
| `criado_em` | `TIMESTAMPTZ` | não | padrão `CURRENT_TIMESTAMP` |
| `atualizado_em` | `TIMESTAMPTZ` | não | atualizado na gravação |

### Chaves e restrições planejadas

- chave primária: `id_resultado`;
- chave candidata única: `numero_ap`;
- `numero_ap > 0`;
- cada `res_01` a `res_06` entre 1 e 60;
- quinze comparações impedindo repetição entre os seis resultados;
- verificações de intervalo para todos os campos calculados;
- `versao_calculo > 0`.

O banco protegerá intervalos e unicidade. A conferência exata das fórmulas será
responsabilidade do Python, que recalculará os derivados antes de cada gravação.

### Índices planejados

- índice único criado pela restrição de `numero_ap`;
- índice B-tree em `data_resultado` para consultas por período.

Não serão criados inicialmente seis índices separados para `res_01` a `res_06`.
O volume atual é pequeno e a necessidade deverá ser demonstrada por consultas e
medição antes de aumentar o custo de escrita.

## 2. Tabela `frequencia_de_resultado`

### Nome

Nome conceitual informado: `frequenciaDeResultado`.

Nome físico proposto no PostgreSQL: `frequencia_de_resultado`.

### Finalidade

Guardar um resumo calculado para cada dezena de 01 a 60. É uma tabela derivada:
seus dados nunca serão digitados diretamente nem aceitos da planilha.

### Interpretação proposta dos nomes informados

- `id_dezana` será corrigido para `id_dezena`;
- `media_oco_mediana_oco` será separado em dois campos: `media_oco` e
  `mediana_oco`.

Essas interpretações precisam de aprovação antes do DDL.

### Campos planejados

| Campo | Tipo PostgreSQL | Nulo | Significado |
|---|---|---:|---|
| `id_dezena` | `SMALLINT GENERATED ALWAYS AS IDENTITY` | não | chave interna |
| `dezena` | `SMALLINT` | não | número de 1 a 60, único |
| `prim_oco` | `INTEGER` | sim | `numero_ap` da primeira ocorrência |
| `ult_oco` | `INTEGER` | sim | `numero_ap` da última ocorrência |
| `num_oco` | `INTEGER` | não | quantidade total de ocorrências |
| `qtd_intervalos` | `INTEGER` | não | quantidade de intervalos entre ocorrências simples |
| `intervalo_minimo` | `INTEGER` | sim | menor intervalo simples observado |
| `intervalo_maximo` | `INTEGER` | sim | maior intervalo simples observado |
| `media_oco` | `NUMERIC(12,6)` | sim | média dos intervalos entre ocorrências |
| `mediana_oco` | `NUMERIC(12,6)` | sim | mediana dos intervalos entre ocorrências |
| `desv_padrao_oco` | `NUMERIC(12,6)` | sim | desvio-padrão populacional dos intervalos |
| `versao_calculo` | `SMALLINT` | não | versão das fórmulas, inicialmente 1 |
| `atualizado_em` | `TIMESTAMPTZ` | não | instante do último recálculo |

### Significado das estatísticas

Os campos `media_oco`, `mediana_oco` e `desv_padrao_oco` serão calculados sobre
os intervalos, não sobre os próprios números das apresentações.

```text
intervalo = numero_ap_atual - numero_ap_anterior
```

`desv_padrao_oco` usará o desvio-padrão populacional dos intervalos observados.

## 2.1. Configuração do estudo de frequência

`configuracao_frequencia_dezenas` mantém uma única linha ativa com concurso
inicial, tamanho inicial, regra de evolução da janela, tipos de evento, método
da faixa, parâmetro, unidade, arredondamento e versão do cálculo. A assinatura
SHA-256 corresponde ao JSON canônico desses campos e é conferida novamente na
leitura pelo código Python.

A configuração inicial é `1 / 500 / INICIO_FIXO_FINAL_EXPANSIVO / TODOS`, com
faixa de média mais ou menos um desvio-padrão e limites externos. Nenhuma unidade
é inferida pelo valor numérico.

## 2.2. Histórico materializado da frequência

`geracoes_frequencia_dezenas` identifica uma construção completa ou provisória,
preserva assinatura e JSON da configuração, assinatura e quantidade dos
resultados de origem e impede mais de uma geração ativa. A assinatura da origem
permite distinguir concursos novos de alterações em concursos já processados.

`historico_frequencia_dezenas` usa uma linha por geração, concurso, dezena e
tipo de evento. Guarda quantidades, estatísticas, previsão e limites exatos e
operacionais, sem repetir as seis dezenas de `resultados`. A exclusão de uma
geração remove somente suas fotografias por cascata.

O índice `(id_geracao, dezena, tipo_evento, numero_do_concurso)` atende a série
dos gráficos. Com 3.069 resultados, a carga real do concurso 500 ao 3.069
produziu 462.600 linhas para os três tipos. Tabela e índices ocuparam
127.811.584 bytes, dos quais 71.688.192 bytes em índices, no benchmark local de
2026-10-30.

A carga completa levou 146,761 s; acrescentar um concurso gerou 180 linhas em
0,189 s. Consultar as três fotografias atuais levou 0,003 s e uma série de 2.571
pontos com assertividade levou 0,057 s. Esses números são referência local, não
garantia para outro equipamento ou volume.

Exemplo para ocorrências da dezena 02 nas apresentações 20, 35 e 50:

```text
prim_oco        = 20
ult_oco         = 50
num_oco         = 3
intervalos      = [15, 15]
media_oco       = 15.000000
mediana_oco     = 15.000000
desv_padrao_oco = 0.000000
```

### Casos sem intervalos suficientes

| Ocorrências | `prim_oco` | `ult_oco` | `num_oco` | Média/mediana/desvio |
|---:|---|---|---:|---|
| 0 | `NULL` | `NULL` | 0 | todos `NULL` |
| 1 | apresentação | mesma apresentação | 1 | todos `NULL` |
| 2 | primeira | última | 2 | média e mediana iguais ao único intervalo; desvio 0 |

Isso segue o contrato aprovado: sem intervalo observado, não inventar valor
zero. Com um intervalo observado, seu desvio-padrão é zero.

### Chaves, restrições e relações planejadas

- chave primária: `id_dezena`;
- `dezena` única e limitada a 1–60;
- `num_oco >= 0`;
- `prim_oco` e `ult_oco` devem ser ambas nulas ou ambas preenchidas;
- quando preenchidas, `prim_oco <= ult_oco`;
- `num_oco = 0` exige primeira e última ocorrências nulas;
- `num_oco > 0` exige primeira e última ocorrências preenchidas;
- médias e desvio não podem ser negativos;
- `versao_calculo > 0`;
- `prim_oco` e `ult_oco` referenciam `resultados(numero_ap)`.

As referências propostas usarão atualização em cascata e impedirão exclusão que
deixe o resumo apontando para uma apresentação inexistente. Exclusões, quando
forem permitidas pelo produto, deverão recalcular o resumo na mesma transação.

### Quantidade e inicialização

A tabela possuirá exatamente 60 linhas, uma para cada dezena. A criação inicial
inserirá as dezenas de 1 a 60 com `num_oco = 0` e demais estatísticas nulas.

### Atualização planejada

Após importação, inclusão, edição ou futura exclusão de um resultado, o Python
recalculará as 60 linhas dentro da mesma transação que altera `resultados`.

Para o volume atual, recalcular 60 resumos a partir de aproximadamente 3.000
resultados é mais simples e seguro do que tentar corrigir incrementalmente apenas
as dezenas afetadas. Otimização somente será considerada depois de medição.

Não haverá edição direta dessa tabela pela interface.

### Índices planejados

- índice único criado pela restrição de `dezena`;
- nenhuma outra indexação inicial, pois haverá somente 60 linhas.

## 3. Tabela `schema_migrations`

### Finalidade

Registrar cada migração aplicada e impedir aplicação duplicada ou alteração
silenciosa de um arquivo já executado.

### Campos planejados

| Campo | Tipo PostgreSQL | Regra |
|---|---|---|
| `versao` | `VARCHAR(20)` | chave primária |
| `nome` | `VARCHAR(200)` | obrigatório |
| `checksum_sha256` | `CHAR(64)` | obrigatório e imutável |
| `aplicada_em` | `TIMESTAMPTZ` | padrão `CURRENT_TIMESTAMP` |

O executor Python futuro comparará o checksum registrado com o arquivo local.
Uma diferença interromperá a inicialização em vez de reaplicar SQL modificado.

## 4. Transações e consistência

Uma operação que altere resultados seguirá, conceitualmente:

```text
BEGIN
  validar entrada
  calcular campos da linha
  inserir ou atualizar resultados
  recalcular frequencia_de_resultado para 01–60
  validar quantidades e referências
COMMIT
```

Qualquer erro executará `ROLLBACK`, preservando tanto o resultado anterior quanto
o resumo anterior.

## 5. Ordem de criação planejada

1. criar `schema_migrations` pelo inicializador controlado;
2. criar `resultados`;
3. criar índices e comentários de `resultados`;
4. criar `frequencia_de_resultado`;
5. criar restrições e referências;
6. inserir as 60 dezenas iniciais;
7. registrar a migração concluída.

A tradução deste modelo para SQL pertence ao Item 1.4 e não está autorizada pelo
Item 1.3.

## 6. Decisões aprovadas no Item 1.3

1. Usar o nome físico `frequencia_de_resultado`.
2. Corrigir `id_dezana` para `id_dezena`.
3. Separar `media_oco_mediana_oco` em `media_oco` e `mediana_oco`.
4. Interpretar média, mediana e desvio como estatísticas dos intervalos entre
   ocorrências.
5. Manter exatamente 60 linhas, inclusive para dezenas nunca ocorridas.
6. Recalcular as 60 linhas na mesma transação de qualquer alteração em
   `resultados`.
7. Incluir `versao_calculo` e `atualizado_em` na tabela de frequência.
8. Incluir checksum SHA-256 em `schema_migrations`.

As oito decisões foram aprovadas pelo usuário em 2026-10-26. O Item 1.3 está
concluído. A alteração efetiva do DDL continua dependendo de autorização
separada para o Item 1.4.

## 7. Extensão aprovada no Item 9.2 — tabela `padroes`

A migração `002_criar_tabela_padroes.sql` acrescenta o cadastro sem alterar as
tabelas existentes.

| Campo | Tipo PostgreSQL | Regra |
|---|---|---|
| `id_padrao` | `BIGINT IDENTITY` | chave primária |
| `padrao_cod` | `VARCHAR(20)` | obrigatório, único, formato `PD_001` |
| `padrao_nome` | `VARCHAR(200)` | obrigatório, preenchido e único |
| `padrao_descr` | `TEXT` | obrigatório e preenchido |
| `num_oco` | `INTEGER` | nulo antes do cálculo ou maior/igual a zero |
| `intervalo_medio` | `NUMERIC(12,6)` | calculado, nulo com menos de duas ocorrências |
| `desv_padrao` | `NUMERIC(12,6)` | calculado, nulo com menos de duas ocorrências |

O estado totalmente nulo significa que a estatística ainda não foi calculada;
`num_oco = 0` significa que o histórico foi analisado e o padrão nunca ocorreu.
Com duas ou mais ocorrências, média e desvio deverão estar preenchidos. Essa
distinção é protegida por restrição do PostgreSQL.

A migração `003` insere os três cadastros iniciais sem sobrescrever registros
existentes e cria `padroes_codigo_seq`. A sequência fornece `PD_004` em diante e
não reutiliza códigos de linhas excluídas.
