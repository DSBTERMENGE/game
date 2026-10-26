# Dicionário de dados — tabela `resultados`

## Situação do documento

- Item do plano: 1.1.
- Estado: aprovado e concluído em 2026-10-26.
- Este documento ainda não autoriza alteração do DDL ou execução no banco.

## Evidência da fonte atual

Arquivo analisado em modo somente leitura:

`MSen/dados/fontes/Resultados_ate_concurso_3069_sorteio.xlsx`

Resultado da conferência:

- aba: `mega_sena_www.asloterias.com.br`;
- cabeçalho: linha 7;
- linhas de resultados: 3.069;
- concursos: 1 a 3069, todos únicos;
- datas: texto no formato `DD/MM/AAAA`;
- dezenas: inteiros de 1 a 60;
- linhas com dezena repetida: zero;
- linhas inválidas encontradas: zero;
- ordem do arquivo: do concurso mais recente para o mais antigo.

## Convenções de nomes

Os nomes apresentados ao usuário podem seguir a nomenclatura original. No
PostgreSQL e no Python serão usados nomes em minúsculas e `snake_case`, evitando
identificadores entre aspas e diferenças entre maiúsculas e minúsculas.

## Campos de identificação e entrada

### `id_resultado`

- Nome conceitual: `IdResultado`.
- Finalidade: identificador interno estável da linha.
- Origem: gerado exclusivamente pelo PostgreSQL.
- Tipo proposto: `BIGINT GENERATED ALWAYS AS IDENTITY`.
- Nulidade: não aceita `NULL`.
- Chave: chave primária.
- Editável pelo usuário: não.
- Exemplo: `1`.

O identificador interno não substitui o número oficial da apresentação. Ele não
deve ser importado do Excel nem reutilizado para atribuir significado histórico.

### `data_resultado`

- Nome conceitual: `Data`.
- Finalidade: data oficial da apresentação/concurso.
- Origem no Excel: coluna `Data`.
- Formato recebido atualmente: texto `DD/MM/AAAA`.
- Tipo PostgreSQL proposto: `DATE`.
- Tipo Python: `datetime.date`.
- Nulidade: não aceita `NULL`.
- Editável pelo usuário: sim, com recálculo e validação ao salvar.
- Exemplo de entrada: `11/10/2026`.
- Exemplo armazenado: `2026-10-11`.

### `numero_ap`

- Nome conceitual: `NumAp`.
- Significado proposto: número oficial da apresentação, correspondente à coluna
  `Concurso` da planilha atual.
- Origem no Excel: coluna `Concurso`.
- Tipo PostgreSQL: `INTEGER`.
- Tipo Python: `int`.
- Nulidade: não aceita `NULL`.
- Restrições: maior que zero e único.
- Editável pelo usuário: sim, sem permitir duplicidade.
- Exemplo: `3069`.

### `res_01` a `res_06`

- Nomes conceituais: `Res01`, `Res02`, `Res03`, `Res04`, `Res05`, `Res06`.
- Finalidade: preservar os seis valores na ordem original em que aparecem na
  fonte.
- Origem no Excel: `bola 1` a `bola 6`, respectivamente.
- Tipo PostgreSQL: `SMALLINT`.
- Tipo Python: `int`.
- Nulidade: não aceitam `NULL`.
- Intervalo permitido: 1 a 60, inclusive.
- Regra conjunta: os seis valores devem ser diferentes entre si.
- Editáveis pelo usuário: sim; qualquer edição recalcula todos os campos
  derivados da linha.
- Exemplo: `47, 5, 22, 44, 57, 19`.

Mapeamento individual:

| Campo PostgreSQL | Nome conceitual | Coluna atual do Excel |
|---|---|---|
| `res_01` | `Res01` | `bola 1` |
| `res_02` | `Res02` | `bola 2` |
| `res_03` | `Res03` | `bola 3` |
| `res_04` | `Res04` | `bola 4` |
| `res_05` | `Res05` | `bola 5` |
| `res_06` | `Res06` | `bola 6` |

## Campos calculados e armazenados

Esses campos serão calculados pelo Python. O Excel, a API e o formulário não
serão autorizados a fornecer seus valores como definitivos.

### `soma_res`

- Nome conceitual: `SomaRes`.
- Fórmula: soma de `res_01` a `res_06`.
- Tipo PostgreSQL: `SMALLINT`.
- Tipo Python: `int`.
- Nulidade: não aceita `NULL`.
- Intervalo matemático para seis valores distintos de 1 a 60: 21 a 345.
- Exemplo para `47, 5, 22, 44, 57, 19`: `194`.

### `media_aritmetica_res`

- Nome conceitual: `MédiaArtRes`.
- Fórmula: `soma_res / 6`.
- Tipo PostgreSQL proposto: `NUMERIC(10,6)`.
- Tipo Python proposto: `Decimal`.
- Nulidade: não aceita `NULL`.
- Precisão proposta para armazenamento: seis casas decimais.
- Exibição inicial proposta: duas casas decimais, sem alterar o valor armazenado.
- Exemplo: `32,333333` armazenado para soma igual a 194.

### `mediana_res`

- Nome conceitual: `MedianaRes`.
- Fórmula: ordenar os seis resultados e calcular a média entre o terceiro e o
  quarto valores.
- Tipo PostgreSQL proposto: `NUMERIC(4,1)`.
- Tipo Python proposto: `Decimal`.
- Nulidade: não aceita `NULL`.
- Valores possíveis terminam em `,0` ou `,5`.
- Exemplo para `5, 19, 22, 44, 47, 57`: `33,0`.

### `desvio_padrao_media`

- Nome conceitual: `Desv_PadraoMedia`.
- Finalidade: medir a dispersão dos seis resultados em relação à média
  aritmética da linha.
- Fórmula proposta: desvio-padrão populacional, dividindo a soma dos quadrados
  dos desvios por 6 antes da raiz quadrada.
- Tipo PostgreSQL proposto: `NUMERIC(10,6)`.
- Tipo Python proposto: `Decimal`.
- Nulidade: não aceita `NULL`.
- Precisão proposta para armazenamento: seis casas decimais.
- Exibição inicial proposta: duas casas decimais.

A escolha populacional foi aprovada no Item 1.1. A implementação e seus casos de
teste serão detalhados em itens posteriores.

### `media_coordenada_x`

- Finalidade: posição horizontal média dos seis resultados na matriz.
- Coordenada individual: `x = (resultado - 1) % 10`.
- Fórmula: `(x1 + x2 + x3 + x4 + x5 + x6) / 6`.
- Tipo PostgreSQL proposto: `NUMERIC(7,6)`.
- Tipo Python proposto: `Decimal`.
- Nulidade: não aceita `NULL`.
- Intervalo: 0 a 9.
- Exibição inicial proposta: duas casas decimais.

### `media_coordenada_y`

- Finalidade: posição vertical média dos seis resultados na matriz.
- Coordenada individual: `y = (resultado - 1) // 10`.
- Fórmula: `(y1 + y2 + y3 + y4 + y5 + y6) / 6`.
- Tipo PostgreSQL proposto: `NUMERIC(7,6)`.
- Tipo Python proposto: `Decimal`.
- Nulidade: não aceita `NULL`.
- Intervalo: 0 a 5.
- Exibição inicial proposta: duas casas decimais.

## Campos técnicos propostos

### `versao_calculo`

- Finalidade: identificar qual versão das fórmulas produziu os campos derivados.
- Tipo PostgreSQL: `SMALLINT`.
- Nulidade: não aceita `NULL`.
- Valor inicial: `1`.
- Editável pelo usuário: não.

Esse campo permite detectar linhas que precisem ser recalculadas caso uma fórmula
mude no futuro.

### `criado_em`

- Finalidade: registrar quando a linha foi inserida no sistema.
- Tipo PostgreSQL: `TIMESTAMPTZ`.
- Valor inicial: `CURRENT_TIMESTAMP`.
- Nulidade: não aceita `NULL`.
- Editável pelo usuário: não.

### `atualizado_em`

- Finalidade: registrar a última gravação da linha.
- Tipo PostgreSQL: `TIMESTAMPTZ`.
- Valor inicial: `CURRENT_TIMESTAMP`.
- Nulidade: não aceita `NULL`.
- Editável pelo usuário: não.

## Regras de atualização

1. Inclusão por Excel e inclusão manual passam pela mesma validação.
2. O Python calcula todos os campos derivados antes da gravação.
3. Inserção ou edição grava originais e derivados na mesma transação.
4. Alterar qualquer `res_01` a `res_06` recalcula todos os derivados.
5. Campos calculados recebidos do navegador ou Excel serão ignorados.
6. Uma linha com `numero_ap` já existente e dados idênticos não será duplicada.
7. Uma linha existente com dados divergentes será separada para confirmação, e
   não sobrescrita silenciosamente.

## Decisões aprovadas no Item 1.1

1. `numero_ap` significa o número oficial da coluna `Concurso`.
2. O desvio-padrão da linha será populacional, com divisor 6.
3. Médias, coordenadas e desvio-padrão serão armazenados com seis casas decimais
   e inicialmente exibidos com duas.
4. Serão incluídos `versao_calculo`, `criado_em` e `atualizado_em` como campos
   técnicos.
5. `id_resultado` será uma identidade interna `BIGINT`, enquanto `numero_ap`
   continuará sendo a identificação funcional única do resultado.

As cinco decisões foram aprovadas pelo usuário em 2026-10-26. O Item 1.1 está
concluído. O Item 1.2 continua dependendo de uma nova autorização.
