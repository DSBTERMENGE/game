# Contrato do backtest e das métricas — Seleção de dezenas

Este documento fecha a subetapa 23.1. Ele define como conferir historicamente
as seleções produzidas pelo contrato matemático da subetapa 23.0, sem criar
tabelas, API ou página.

## 1. Finalidade

O backtest mede quantas das seis dezenas efetivamente sorteadas estavam no
conjunto selecionado antes de cada concurso-alvo. Ele compara configurações de
forma reproduzível, mas não transforma desempenho passado em garantia futura.

## 2. Período

- Primeiro concurso-alvo: 500.
- Último concurso-alvo: último resultado existente no corte da execução.
- Período inclusivo.
- Previsões posteriores ao último resultado ficam pendentes e não entram no
  backtest.

Uma comparação direta exige o mesmo concurso inicial, concurso final e a mesma
assinatura da tabela de resultados.

## 3. Separação obrigatória entre seleção e conferência

Para cada alvo `C`:

1. reconstruir ou obter as estatísticas usando somente concursos até `C - 1`;
2. calcular e congelar configuração, justificativas e dezenas selecionadas;
3. somente depois consultar o resultado real de `C`;
4. calcular a interseção entre selecionadas e sorteadas.

O serviço de seleção não receberá o resultado de `C`. A conferência será uma
operação posterior e separada. Para o alvo 500, os cálculos usam somente os
concursos 1 a 499; a fotografia persistida do próprio concurso 500 é proibida.

## 4. Dados mínimos por concurso-alvo

Cada avaliação precisa conservar:

- identificação e cópia imutável da configuração;
- assinatura dos resultados e versão do cálculo;
- concurso-alvo e corte `C - 1`;
- `k`, `j` e estratégia de quantidade aplicáveis;
- dezenas selecionadas em ordem crescente;
- condição `SIMPLES` e classificação que justificaram cada seleção;
- quantidade de dezenas selecionadas;
- referência ao resultado real, sem duplicar suas seis dezenas na tabela de
  pesquisa;
- dezenas acertadas, obtidas pela interseção;
- quantidade de acertos e classe exclusiva;
- situação e motivo quando não avaliável.

Os valores matemáticos que justificam cada dezena — última ocorrência, média,
desvio, centro e limites — pertencem ao detalhe da seleção e deverão ser
preservados para auditoria.

## 5. Interseção e classe exclusiva

Se `S(C)` é o conjunto selecionado e `R(C)` é o conjunto das seis dezenas do
resultado:

```text
acertos(C) = S(C) ∩ R(C)
quantidade_acertos(C) = |acertos(C)|
classe(C) = quantidade_acertos(C)
```

`classe(C)` assume exatamente um valor entre 0 e 6. Se houve seis acertos, o
concurso conta somente na classe 6; não é repetido nas classes 1 a 5. A classe
0 é obrigatória.

Uma seleção vazia produz zero acertos e classe 0 quando havia base matemática
válida e nenhuma faixa continha o alvo. Ausência completa de base não deve ser
confundida com uma seleção válida vazia.

## 6. Situações da avaliação

- `AVALIADO`: seleção congelada e resultado real disponível.
- `PENDENTE`: seleção do próximo concurso congelada, mas o resultado ainda não
  existe.
- `NAO_AVALIAVEL`: lacuna histórica, ausência completa de base simples,
  incompatibilidade de versão ou falha que impeça reproduzir a seleção.

`PENDENTE` e `NAO_AVALIAVEL` não entram no denominador das taxas de acerto. O
motivo deve ser registrado e exibido separadamente.

## 7. Relatório consolidado obrigatório

Para uma execução de pesquisa, informar:

- período solicitado e período efetivamente avaliado;
- quantidade de concursos solicitados, avaliados, pendentes e não avaliáveis;
- quantidade e percentual de concursos em cada classe de 0 a 6;
- quantidade mínima, máxima e média de dezenas selecionadas por concurso;
- quantidades solicitada, aprovada e efetivamente retornada, incluindo quantas
  vezes uma configuração fixa não atingiu `N`;
- total de dezenas selecionadas;
- total de dezenas acertadas;
- percentual das dezenas sorteadas cobertas;
- percentual das dezenas selecionadas que foram acertadas;
- custo combinatório total e médio, quando aplicável.

Para `A` concursos avaliados e `n_r` concursos da classe `r`:

```text
percentual_classe(r) = n_r / A × 100
```

As sete quantidades de classe devem somar `A`, e seus percentuais devem somar
100%, admitida apenas diferença de apresentação causada por arredondamento.

## 8. Métricas de cobertura e concentração

Se `H` é a soma dos acertos, `Q` é a soma das quantidades selecionadas e cada
concurso tem seis dezenas sorteadas:

```text
cobertura_das_sorteadas = H / (6 × A) × 100
precisao_das_selecionadas = H / Q × 100
media_acertos_por_concurso = H / A
```

Se `Q = 0`, a precisão das selecionadas é `NULL`, nunca zero. Essas métricas
complementam as classes exclusivas e não as substituem.

Também podem ser exibidas taxas cumulativas claramente identificadas, como
`pelo menos 4 acertos`, mas elas são derivadas e não alteram a classificação
exclusiva.

## 9. Custo combinatório

Se uma seleção possui `N` dezenas e forem gerados todos os jogos possíveis de
seis dezenas:

```text
jogos(C) = C(N,6), quando N >= 6
jogos(C) = 0, quando N < 6
```

O custo total da pesquisa é a soma de `jogos(C)` nos concursos avaliados. O
custo médio é o total dividido por `A`.

Se `quantidade_acertos(C) = 6`, a geração completa de `C(N,6)` contém
exatamente uma combinação igual ao resultado real. Se houve menos de seis
acertos, nenhuma combinação formada somente pelas selecionadas pode reproduzir
as seis dezenas sorteadas.

## 10. Comparação entre configurações

Uma comparação válida exige:

- mesma assinatura de resultados;
- mesmo período efetivamente avaliado;
- mesma versão das fórmulas;
- ausência de concursos não avaliáveis em apenas uma das pesquisas, ou
  apresentação explícita dessa diferença.

O relatório comparativo deve colocar lado a lado:

- `k`, `j` e estratégia de quantidade;
- distribuição das classes 0 a 6;
- cobertura das sorteadas;
- precisão das selecionadas;
- quantidade média de dezenas selecionadas;
- custo combinatório total e médio.

Não haverá inicialmente um único índice automático de “melhor configuração”.
Uma configuração que seleciona mais dezenas tende a aumentar a cobertura e o
custo ao mesmo tempo. A decisão deve mostrar esse compromisso, sem declarar
vencedora apenas a maior quantidade de acertos.

## 11. Casos manuais obrigatórios

### 11.1. Classe exclusiva

```text
selecionadas = {10, 20, 30, 40, 50, 60}
resultado    = {10, 20, 30, 40, 50, 59}
interseção   = {10, 20, 30, 40, 50}
classe       = 5
```

Esse concurso incrementa somente a classe 5.

### 11.2. Classe zero com seleção válida

```text
selecionadas = {01, 02, 03}
resultado    = {10, 20, 30, 40, 50, 60}
classe       = 0
```

### 11.3. Seleção vazia

Se todas as dezenas possuíam base matemática, mas nenhuma faixa continha o
alvo, a seleção vazia é válida e pertence à classe 0.

### 11.4. Sem base

Se nenhum tipo ativo de nenhuma dezena possui intervalo suficiente, o alvo é
`NAO_AVALIAVEL` e não pertence à classe 0.

### 11.5. Consolidação

Em quatro concursos avaliados com classes `0, 2, 5, 5`:

```text
classe 0: 1 concurso = 25%
classe 2: 1 concurso = 25%
classe 5: 2 concursos = 50%
demais classes: 0
```

### 11.6. Proteção temporal

A lista do concurso 500 deve ser idêntica quando o teste é executado em bases
que compartilham os resultados 1 a 499, mesmo que uma delas contenha resultados
posteriores diferentes.

## 12. Fora do escopo da subetapa 23.1

- DDL e nomes definitivos das tabelas;
- implementação da quantidade configurável, definida posteriormente nas
  subetapas 23.2 e 23.2-A;
- persistência, execução assíncrona e cancelamento;
- API, página, gráficos e ajuda;
- otimização automática dos parâmetros.
