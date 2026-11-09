# Contrato matemático e temporal — Seleção de dezenas

Este documento fecha a subetapa 23.0. Ele define o cálculo de elegibilidade de
uma dezena para um concurso-alvo, sem criar tabelas, API ou página.

## 1. Finalidade e escopo

A seleção estima quais dezenas possuem faixa de retorno contendo determinado
concurso-alvo. O cálculo é experimental e descritivo: não garante resultado
futuro nem ativa automaticamente filtros do Screener.

O screener de dezenas usa exclusivamente ocorrências `SIMPLES`, pois sua
pergunta é se cada dezena estará presente no concurso-alvo. `2VS` e `3VS` não
acrescentam nem retiram dezenas desse conjunto. Esses dois eventos pertencem ao
screener posterior das combinações de seis dezenas, no qual representam
repetições consecutivas que podem aprovar ou eliminar um jogo.

## 2. Corte temporal obrigatório

Para selecionar dezenas para o concurso-alvo `C`, somente resultados com
número menor que `C` podem ser utilizados. O corte é, portanto, `C - 1`.

```text
dados da seleção de C: concursos <= C - 1
dados da conferência: resultado de C, consultado somente após a seleção
```

O concurso `C` e qualquer resultado posterior são invisíveis durante o
cálculo. No backtest iniciado em 500, a primeira fotografia precisa ser
calculada com resultados até 499. A linha histórica persistida do concurso 500
não pode substituí-la, pois já conhece o resultado que será conferido.

## 3. Estatísticas de cada tipo

Para cada dezena `D` e corte, usam-se as ocorrências `SIMPLES`:

- `U`: número da última ocorrência conhecida até o corte;
- `μ`: média dos intervalos simples concluídos até o corte;
- `σ`: desvio-padrão populacional desses intervalos.

As regras de formação dos intervalos simples permanecem as do
`CONTRATO_FREQUENCIA_DEZENAS.md`. Média e desvio continuam na unidade
**concurso**.

## 4. Parâmetros de calibração

`k` controla a meia largura da faixa:

```text
0 < k <= 1
valor padrão: 1
```

`j` desloca o centro em unidades de desvio-padrão:

```text
-k <= j <= +k
valor padrão: 0
```

Assim, o centro ajustado permanece dentro da faixa original de amplitude
`k × σ`. `j < 0` antecipa o centro, `j = 0` conserva a média e `j > 0` posterga
o centro. Uma configuração usa o mesmo `k` e o mesmo `j` em todo o período; é
proibido ajustá-los depois de conhecer cada resultado.

Os parâmetros são decimais, persistidos e intercambiados inicialmente com seis
casas decimais e `ROUND_HALF_UP`.

## 5. Fórmula da faixa

Existindo ao menos um intervalo:

```text
centro_original = U + μ
centro_ajustado = centro_original + j × σ
meia_largura = k × σ

limite_inferior_exato = centro_ajustado - meia_largura
limite_superior_exato = centro_ajustado + meia_largura
```

Os limites operacionais inteiros preservam a regra externa já usada pelo
módulo de frequências:

```text
limite_inferior = floor(limite_inferior_exato)
limite_superior = ceil(limite_superior_exato)
```

Os limites são inclusivos. Para um corte `K`, somente alvos posteriores a `K`
são consultados; não se altera a faixa exata para esconder que parte dela já
ficou no passado.

A elegibilidade da dezena é:

```text
limite_inferior <= concurso_alvo <= limite_superior
```

## 6. Estados especiais

- **Sem intervalo:** `μ` e `σ` são `NULL`; a dezena fica `SEM_BASE` e não é
  aprovada pela faixa.
- **Desvio zero:** o deslocamento e a meia largura são zero; `j` e `k` não
  alteram o centro. Como todos os intervalos observados são iguais, o centro é
  inteiro e somente esse concurso é elegível.
- **Faixa no passado:** se o alvo for posterior ao corte mas estiver acima do
  limite superior, a dezena fica `FORA_DA_FAIXA`.

## 7. Concurso-alvo

Se `L` é o último concurso armazenado, o único concurso-alvo calculado é
`CA = L + 1`. Não existe horizonte configurável nem cálculo de concursos além
desse alvo, pois a metodologia recalcula as estatísticas após cada resultado
novo.

O alvo usa como corte o concurso `L`. Quando o resultado de `CA` for importado,
a previsão congelada será conferida e preservada. Somente então uma nova
previsão poderá ser produzida para `CA + 1`, usando a base atualizada e sem
reescrever a previsão anterior.

## 8. Benefício e risco do deslocamento `j`

O deslocamento permite testar se a previsão central fica sistematicamente
adiantada ou atrasada. Ele não aumenta a largura da faixa: ao mover um limite
para um lado, também move o limite oposto e pode retirar dezenas que antes eram
elegíveis.

O backtest deverá comparar configurações imutáveis. Escolher `j` por concurso
depois de ver o resultado constitui vazamento futuro e é proibido.

## 9. Casos manuais obrigatórios

### 9.1. Faixa sem deslocamento

```text
U = 480; μ = 25; σ = 6; k = 0,5; j = 0
centro = 505
faixa exata = 502 a 508
faixa operacional = 502 a 508
```

Os alvos 502 e 508 são elegíveis por serem limites inclusivos; 501 e 509 não
são elegíveis.

### 9.2. Deslocamento para a direita

```text
U = 480; μ = 25; σ = 6; k = 0,5; j = 0,25
centro ajustado = 506,5
faixa exata = 503,5 a 509,5
faixa operacional = 503 a 510
```

O alvo 510 passa a ser elegível, enquanto o alvo 502 deixa de ser.

### 9.3. Deslocamento para a esquerda

```text
U = 480; μ = 25; σ = 6; k = 0,5; j = -0,5
centro ajustado = 502
faixa operacional = 499 a 505
```

### 9.4. Separação dos dois screeners

A faixa `SIMPLES` decide se a dezena é aprovada para o alvo. Somente depois de
definido o conjunto de dezenas são formadas combinações de seis. Regras 2VS e
3VS podem então eliminar combinações, mas não reescrevem a seleção de dezenas.

### 9.5. Proteção do concurso 500

A seleção para o alvo 500 é calculada exclusivamente com concursos 1 a 499.
Somente após congelar a lista de candidatas o resultado 500 pode ser lido para
conferência.

### 9.6. Concurso-alvo único

Com último concurso cadastrado 3090, somente 3091 é calculado, com corte 3090.
Depois da importação do resultado 3091, ele é conferido e o sistema pode
calcular 3092 com corte 3091.

## 10. Fora do escopo da subetapa 23.0

- tabelas e migrações;
- persistência das pesquisas;
- métricas consolidadas do backtest;
- quantidade fixa de dezenas e formação de jogos;
- API, página, progresso e ajuda.

Esses assuntos pertencem às subetapas seguintes da Etapa 23.
