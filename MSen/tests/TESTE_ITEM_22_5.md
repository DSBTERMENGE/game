# Teste da subetapa 22.5 — carga, troca e atualização incremental

Data: 2026-10-30.

## Fluxos implementados

- primeira carga cria geração provisória, grava todas as fotografias e somente
  então a torna ativa;
- repetição com mesma origem e configuração não insere linhas;
- concursos novos aquecem o estado pelo prefixo, mas produzem e gravam somente
  os novos cortes;
- configuração diferente constrói geração provisória completa e troca a ativa
  dentro da mesma transação;
- após a troca, somente a nova geração detalhada é conservada;
- falha durante carga completa ou incremental reverte todas as linhas parciais;
- alteração em concurso antigo é detectada pela assinatura do prefixo e exige
  autorização explícita de reconstrução;
- lacuna, retrocesso, origem encurtada, versão ou configuração incompatível
  impedem acréscimo silencioso.

A migração 020 acrescenta à geração a assinatura SHA-256 e a quantidade dos
resultados usados. A assinatura inclui concurso, data e seis dezenas. A chegada
de concursos novos não altera a assinatura do prefixo anteriormente processado.

## PostgreSQL efêmero controlado

```text
python -m tests.validar_carga_historico_frequencia
```

O cenário confirmou:

- primeira carga: 3 cortes e 540 linhas;
- repetição idempotente: zero linhas;
- acréscimo de dois concursos: somente 2 cortes e 360 linhas;
- troca de configuração: geração nova com 720 linhas e remoção da antiga;
- falhas controladas sem alteração da geração ativa;
- alteração antiga bloqueada até reconstrução autorizada;
- lacuna bloqueada sem perda dos dados ativos.

Tempos desse cenário pequeno variaram aproximadamente entre 0,03 s e 0,08 s.

## Benchmark com os resultados locais

O script `benchmark_carga_historico_frequencia.py` copiou os resultados locais
para outro database efêmero; o `games` foi somente lido.

```text
resultados: 3.069
cortes históricos: 2.570 (500 a 3.069)
linhas: 462.600
motor + gravação: 149,947 s
tabela + índices: 127.811.584 bytes (~121,9 MiB)
índices: 71.688.192 bytes (~68,4 MiB)
```

Esses números são a medição anterior a qualquer otimização. O database efêmero
foi removido ao final.

## Regressão

```text
python -m unittest discover -s tests -p "test_*.py"
```

Resultado: **613 testes aprovados**. Permaneceram somente avisos preexistentes
de arquivos abertos nos testes do Screener. O `games` persistente não foi
alterado.
