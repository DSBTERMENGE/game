# Teste da subetapa 23.5 — motor de seleção para um concurso-alvo

Data: 03/11/2026.

## Escopo concluído

- motor puro, sem leitura do resultado do concurso-alvo;
- cálculo de centro original, deslocamento `j`, faixa `k × desvio`, limites
  inteiros inclusivos e distâncias;
- avaliação explicável das 60 dezenas;
- ranking determinístico por distância normalizada, distância absoluta e
  número da dezena;
- modos `MAX` e `FIXA`, sem completar a quantidade com dezenas reprovadas;
- tratamento de `SEM_BASE`, faixa não atingida e desvio zero;
- leitura da fotografia `SIMPLES` ativa no corte exato;
- reconstrução por `resultados` para cortes anteriores ao histórico;
- rejeição de origem com lacuna histórica.

## Casos unitários

Executado:

```text
python -m unittest tests.test_selecao_dezenas -v
```

Resultado: **7 testes aprovados**, cobrindo os exemplos matemáticos das
subetapas 23.0 e 23.2.

## Validação somente de leitura no banco local

Executado:

```text
python -m tests.validar_motor_selecao_dezenas
```

Resultado:

```text
Alvo 500: 45 dezenas; alvo 3070: 49 dezenas.
```

O alvo 500 usou exclusivamente resultados de 1 a 499. O alvo 3070 usou o
corte real 3069. O ensaio não gravou pesquisa nem alterou o banco.

## Regressão

Executado:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **651 testes aprovados**. Permaneceram apenas três avisos
preexistentes de arquivos do Screener abertos durante testes.
