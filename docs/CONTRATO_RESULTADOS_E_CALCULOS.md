# Contrato dos resultados e cálculos

## Situação do documento

- Item do plano: 1.2.
- Estado: aprovado e concluído em 2026-10-26.
- Escopo: especificação; nenhum código ou banco é alterado por este documento.
- Dicionário de referência: `docs/DICIONARIO_DADOS_RESULTADOS.md`.

## 1. Princípios gerais

1. A planilha e o formulário fornecem somente os campos de entrada.
2. O Python valida a entrada e calcula todos os campos derivados.
3. As mesmas funções atendem importação, inclusão e edição.
4. Funções matemáticas puras não acessam arquivo, interface ou banco.
5. Um erro de validação impede todos os cálculos e toda gravação daquela linha.
6. Valores originais e derivados são gravados juntos ou não são gravados.
7. Cálculos intermediários não são arredondados; somente o resultado final de
   cada campo é ajustado à precisão de armazenamento.
8. Os cálculos decimais usam `Decimal`, e não ponto flutuante binário.

## 2. Contrato de entrada de uma linha

### Campos recebidos

```text
data_resultado
numero_ap
res_01
res_02
res_03
res_04
res_05
res_06
```

### Regras

- `data_resultado`: data válida; no Excel atual chega como `DD/MM/AAAA`;
- `numero_ap`: inteiro maior que zero;
- resultados: exatamente seis inteiros;
- cada resultado: de 1 a 60, inclusive;
- os seis resultados: diferentes entre si;
- a ordem `res_01` a `res_06`: preservada conforme a fonte.

Espaços externos em textos podem ser removidos antes da validação. Valores como
`5,5`, `05A`, verdadeiro/falso ou célula vazia não serão silenciosamente
convertidos em resultados inteiros.

### Saída após validação e cálculos

```text
data_resultado
numero_ap
res_01 ... res_06
soma_res
media_aritmetica_res
mediana_res
desvio_padrao_media
media_coordenada_x
media_coordenada_y
versao_calculo = 1
```

`id_resultado`, `criado_em` e `atualizado_em` são administrados pela camada de
persistência e não são produzidos pelas funções matemáticas.

## 3. Precisão e arredondamento propostos

- cálculo interno: precisão decimal suficiente para não truncar intermediários;
- armazenamento de média, desvio e coordenadas: seis casas decimais;
- armazenamento da mediana: uma casa decimal;
- apresentação inicial: duas casas decimais;
- modo de arredondamento proposto: metade para cima (`ROUND_HALF_UP`);
- separador no banco e no intercâmbio técnico: ponto;
- separador apresentado ao usuário em português: vírgula.

Exemplo:

```text
valor matemático: 32,333333333...
armazenado:        32.333333
apresentado:       32,33
```

O valor exibido nunca substitui o valor armazenado.

## 4. Contratos dos cálculos de uma linha

### 4.1. Soma

Entrada: seis resultados já validados.

Fórmula:

```text
soma_res = res_01 + res_02 + res_03 + res_04 + res_05 + res_06
```

Saída: inteiro de 21 a 345.

### 4.2. Média aritmética

Entrada: seis resultados validados.

Fórmula:

```text
media_aritmetica_res = soma_res / 6
```

Saída: `Decimal`, ajustado para seis casas apenas ao final.

### 4.3. Mediana

Entrada: seis resultados validados.

Procedimento:

1. criar uma cópia ordenada dos seis valores;
2. preservar a ordem original nos campos `res_01` a `res_06`;
3. somar o terceiro e o quarto valores ordenados;
4. dividir por 2.

Saída: `Decimal` com uma casa, sempre terminando em `,0` ou `,5`.

### 4.4. Desvio-padrão populacional

Entrada: seis resultados validados e média aritmética não arredondada.

Fórmula aprovada no Item 1.1:

```text
variancia = soma((resultado - media)²) / 6
desvio_padrao_media = raiz_quadrada(variancia)
```

Saída: `Decimal`, ajustado para seis casas apenas depois da raiz quadrada.

### 4.5. Coordenadas individuais

Entrada: um resultado inteiro `n`, de 1 a 60.

Fórmulas:

```text
x = (n - 1) módulo 10
y = parte inteira de ((n - 1) / 10)
```

Saída: dois inteiros, `x` entre 0 e 9 e `y` entre 0 e 5.

Casos obrigatórios:

```text
01 = (0; 0)
10 = (9; 0)
51 = (0; 5)
60 = (9; 5)
```

### 4.6. Média espacial

Entrada: as seis coordenadas individuais.

Fórmulas:

```text
media_coordenada_x = soma(x1 ... x6) / 6
media_coordenada_y = soma(y1 ... y6) / 6
```

Saída: dois valores `Decimal`, ajustados para seis casas somente ao final. Não
há arredondamento para o centro de uma dezena.

## 5. Exemplo completo de referência

Entrada:

```text
data_resultado = 11/10/2026
numero_ap = 3069
resultados = 47, 5, 22, 44, 57, 19
```

Resultados ordenados somente para a mediana:

```text
5, 19, 22, 44, 47, 57
```

Saída calculada esperada:

```text
soma_res             = 194
media_aritmetica_res = 32.333333
mediana_res           = 33.0
desvio_padrao_media   = 18.217818
media_coordenada_x    = 4.666667
media_coordenada_y    = 2.666667
versao_calculo        = 1
```

Coordenadas usadas:

```text
47 = (6; 4)
05 = (4; 0)
22 = (1; 2)
44 = (3; 4)
57 = (6; 5)
19 = (8; 1)
```

## 6. Contratos das análises históricas

### 6.1. Ordem da série

Para análises temporais, os resultados serão ordenados do mais antigo para o
mais recente por `numero_ap` crescente. A data servirá como conferência. Uma
incompatibilidade entre ordem do número e data será relatada como divergência.

### 6.2. Frequência de 01 a 60

Entrada:

- série de resultados válidos;
- período opcional com limites inclusivos.

Saída: sessenta registros, mesmo quando algum número nunca ocorreu.

Cada registro contém inicialmente:

```text
numero
quantidade_ocorrencias
```

Histórico vazio devolve os números de 01 a 60 com frequência zero; não é erro.

### 6.3. Ocorrências e intervalos

Para cada número, guardar na saída da função as apresentações em que ocorreu,
em ordem crescente.

Definição proposta de intervalo:

```text
intervalo = numero_ap_atual - numero_ap_anterior
```

Definição confirmada pelo usuário em 2026-10-26. Exemplo:

```text
dezena = 02
ocorrência anterior = apresentação 35
ocorrência seguinte = apresentação 50
intervalo = 50 - 35 = 15
```

Com essa definição:

- ocorrências em apresentações consecutivas produzem intervalo 1;
- a quantidade de apresentações sem ocorrência entre elas é `intervalo - 1`;
- zero ou uma ocorrência produz lista de intervalos vazia.

### 6.4. Intervalo médio

Entrada: lista de intervalos de um número.

- lista vazia: saída `NULL`, pois não existe intervalo observado;
- lista com valores: soma dos intervalos dividida pela quantidade;
- armazenamento ou intercâmbio futuro: seis casas decimais;
- apresentação inicial: duas casas decimais.

Zero não será usado para representar ausência de intervalo, porque zero seria um
valor matemático e não “dado inexistente”.

### 6.5. Desvio-padrão dos intervalos

Definição proposta: desvio-padrão populacional dos intervalos observados.

- nenhum intervalo: `NULL`;
- exatamente um intervalo: `0.000000`;
- dois ou mais: aplicar a fórmula populacional com divisor igual à quantidade
  de intervalos.

## 7. Contrato de erros

As funções retornarão dados válidos ou lançarão um erro específico; não
retornarão cálculos parciais.

| Código | Condição |
|---|---|
| `DATA_AUSENTE` | data não fornecida |
| `DATA_INVALIDA` | valor não representa data real no formato aceito |
| `NUMERO_AP_AUSENTE` | apresentação/concurso não fornecido |
| `NUMERO_AP_INVALIDO` | não inteiro ou menor que 1 |
| `QUANTIDADE_RESULTADOS_INVALIDA` | quantidade diferente de seis |
| `RESULTADO_AUSENTE` | uma das seis posições está vazia |
| `RESULTADO_NAO_INTEIRO` | valor não é inteiro |
| `RESULTADO_FORA_INTERVALO` | valor menor que 1 ou maior que 60 |
| `RESULTADO_REPETIDO` | um número aparece mais de uma vez na linha |
| `PERIODO_INVALIDO` | limite inicial posterior ao final |

`NUMERO_AP_DUPLICADO` e divergências com o banco pertencem à persistência ou
importação, não às funções matemáticas puras.

Uma mensagem destinada ao usuário acompanhará o código e indicará campo, valor e
linha da planilha quando essa informação existir. A mensagem não poderá expor
credenciais ou detalhes internos do servidor.

## 8. Contrato da edição

Ao salvar uma edição:

1. validar novamente todos os campos de entrada;
2. ignorar quaisquer derivados enviados pelo navegador;
3. recalcular todos os derivados a partir dos seis resultados;
4. definir `versao_calculo = 1`;
5. gravar a linha completa em uma transação;
6. atualizar `atualizado_em` somente se a gravação for confirmada;
7. em caso de erro, manter integralmente a versão anterior.

## 9. Decisões aprovadas no Item 1.2

1. Usar `Decimal` e arredondamento `ROUND_HALF_UP`.
2. Arredondar somente o resultado final de cada campo, nunca os intermediários.
3. Ordenar análises históricas por `numero_ap` crescente e usar a data como
   conferência.
4. Definir intervalo como a diferença entre números de apresentação; concursos
   consecutivos têm intervalo 1 e zero concursos ausentes entre eles. Definição
   confirmada pelo usuário em 2026-10-26.
5. Para intervalo médio e desvio dos intervalos, devolver `NULL` quando não
   existir intervalo; com exatamente um intervalo, o desvio será zero.

As decisões foram aprovadas pelo usuário em 2026-10-26. O Item 1.2 está
concluído. O Item 1.3 continua dependendo de nova autorização.
