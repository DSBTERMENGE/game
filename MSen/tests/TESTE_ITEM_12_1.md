# Evidência do Item 12.1 — contrato de dezenas na mesma linha

Data: 2026-10-27.

## Leitura do cadastro

- `PG_003`: Dezenas na mesma linha;
- `PD_007`: duas dezenas na mesma linha;
- `PD_008`: três dezenas na mesma linha;
- `PD_009`: mais de três dezenas na mesma linha;
- os três registros estão associados a `PG_003`;
- as estatísticas estão nulas e os detectores aparecem como pendentes.

## Definição aprovada para implementação

A linha é `((dezena - 1) // 10) + 1`. A classificação será exclusiva pela
maior ocupação entre as seis linhas: exatamente duas, exatamente três ou mais
de três dezenas. Sequencialidade não será exigida e cada concurso contará no
máximo uma ocorrência em cada grupo conceitual.

Foram registrados casos normais, empates, limites, entradas inválidas e
históricos insuficientes. Nenhum código, cadastro ou dado do PostgreSQL foi
alterado nesta subetapa.

Documento: `docs/CONTRATO_PADROES_MESMA_LINHA.md`.
