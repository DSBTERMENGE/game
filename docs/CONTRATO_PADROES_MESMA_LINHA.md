# Contrato dos padrões de dezenas na mesma linha

Data de definição: 2026-10-27.

## 1. Cadastros interpretados

O grupo `PG_003 — Dezenas na mesma linha` contém:

| Código | Regra funcional interpretada |
|---|---|
| `PD_007` | a linha mais ocupada possui exatamente duas dezenas |
| `PD_008` | a linha mais ocupada possui exatamente três dezenas |
| `PD_009` | a linha mais ocupada possui quatro, cinco ou seis dezenas |

As descrições informam expressamente que as dezenas não precisam ser
sequenciais. O código estável, e não o nome editável, será usado para associar
cada cadastro à sua função Python.

## 2. Matriz e cálculo da linha

```text
Linha 1: 01 02 03 04 05 06 07 08 09 10
Linha 2: 11 12 13 14 15 16 17 18 19 20
Linha 3: 21 22 23 24 25 26 27 28 29 30
Linha 4: 31 32 33 34 35 36 37 38 39 40
Linha 5: 41 42 43 44 45 46 47 48 49 50
Linha 6: 51 52 53 54 55 56 57 58 59 60
```

A linha de uma dezena será calculada por `((dezena - 1) // 10) + 1`.

## 3. Classificação exclusiva

O sistema contará quantas dezenas existem em cada uma das seis linhas e usará
a maior quantidade encontrada. O resultado pertencerá a no máximo um destes
três padrões:

- maior quantidade igual a 2: somente `PD_007`;
- maior quantidade igual a 3: somente `PD_008`;
- maior quantidade superior a 3: somente `PD_009`;
- todas as linhas com somente uma dezena: nenhum padrão deste grupo.

Uma linha com três dezenas contém combinações de pares, mas não será registrada
também em `PD_007`. Se duas ou mais linhas empatarem na maior quantidade, o
resultado contará como uma única ocorrência do padrão correspondente.

## 4. Casos de referência

| Resultado | Maior ocupação de linha | Classificação |
|---|---:|---|
| `01, 12, 23, 34, 45, 56` | 1 | nenhum padrão |
| `01, 05, 18, 27, 44, 59` | 2 | somente `PD_007` |
| `01, 05, 12, 18, 44, 59` | 2 em duas linhas | somente `PD_007`, uma ocorrência |
| `21, 25, 30, 34, 45, 56` | 3 | somente `PD_008` |
| `01, 05, 09, 12, 18, 44` | 3 e 2 | somente `PD_008` |
| `31, 33, 36, 40, 45, 56` | 4 | somente `PD_009` |
| `01, 02, 03, 04, 05, 06` | 6 | somente `PD_009` |

A ordem de entrada não alterará a classificação. As seis dezenas continuarão
obrigatoriamente diferentes, inteiras e contidas entre 1 e 60.

## 5. Estatísticas históricas

Cada concurso classificado contará uma vez. Entre concursos consecutivos do
mesmo padrão, o intervalo será a diferença entre seus números de apresentação.
Serão calculados quantidade de ocorrências, intervalo médio e desvio-padrão
populacional dos intervalos, reutilizando a infraestrutura existente.

Com nenhuma ou uma ocorrência, ainda não existe intervalo observável;
`intervalo_medio` e `desv_padrao` permanecerão nulos.

## 6. Casos obrigatórios para os testes

- nenhuma linha repetida;
- exatamente duas, exatamente três e mais de três dezenas na mesma linha;
- dezenas não sequenciais na mesma linha;
- duas linhas empatadas com pares;
- uma linha com três dezenas e outra com duas;
- limites das linhas, incluindo `01`, `10`, `11`, `50`, `51` e `60`;
- entrada em ordem diferente;
- quantidade diferente de seis, repetição, booleano, texto e valores fora de
  `01` a `60`;
- histórico vazio, uma ocorrência e várias ocorrências com intervalos conhecidos.

## 7. Limite da subetapa 12.1

Esta subetapa somente formaliza a interpretação e os testes esperados. Os
detectores, o registro, o cálculo histórico e a persistência dependerão de
autorizações posteriores.
