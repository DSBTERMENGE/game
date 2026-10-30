# Teste da subetapa 22.1 — fotografia atual das frequências

Data: 2026-10-30.

## Escopo

- inventário do cálculo e da tabela `frequencia_de_resultado`;
- quantidade, mínimo e máximo dos intervalos simples;
- preservação de média, mediana e desvio-padrão populacional existentes;
- migração e preenchimento a partir das seis dezenas de `resultados`;
- atualização transacional pelo repositório;
- reconciliação e regressão.

## Alterações verificadas

- `FrequenciaResultado` passou a expor `qtd_intervalos`, `intervalo_minimo` e
  `intervalo_maximo`.
- `RepositorioFrequencias` grava os três campos junto com o resumo já existente.
- A migração `017_ampliar_frequencia_resultado.sql` deriva os intervalos com
  `LAG(numero_ap)` após abrir as seis dezenas com `UNNEST`.
- A restrição exige zero intervalos e limites nulos com menos de duas
  ocorrências; com duas ou mais, exige `qtd_intervalos = num_oco - 1`, mínimo
  positivo e máximo maior ou igual ao mínimo.
- O esquema consolidado recebeu a mesma estrutura. A migração 001 permaneceu
  inalterada por já integrar o histórico aplicado.

## PostgreSQL efêmero

Executado:

```text
python -m tests.validar_migracao_frequencia_resultado
```

O cenário partiu da estrutura antiga, inseriu quatro resultados e aplicou a
migração 017. Resultado:

```text
60 dezenas
24 ocorrências
3 intervalos
dezena 02: 3 intervalos, mínimo 10, máximo 15
```

O database temporário foi removido ao final. O database persistente `games` não
foi alterado.

Em um segundo database efêmero, o executor aplicou todas as migrações, incluindo
a 017, e na repetição não reaplicou nenhuma, confirmando a idempotência pelo
registro e checksum de `schema_migrations`.

## Regressão

Executado:

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **576 testes aprovados**. Permaneceram somente avisos preexistentes
de arquivos abertos em testes do Screener, sem falha.

`git diff --check` não encontrou erro de whitespace; exibiu apenas os avisos de
conversão futura de LF para CRLF já próprios do ambiente Windows.
