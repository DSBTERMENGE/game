# Teste do Item 3.1 — dependência e arquivos Excel controlados

Data: 2026-10-26.

## Resultado

- `openpyxl>=3.1.5,<4` e `defusedxml>=0.7.1,<1` registrados no projeto;
- seis planilhas `.xlsx` geradas em `tests/fixtures`;
- todas abriram com `openpyxl` usando `read_only=True` e a folha `resultados`;
- todas possuem oito colunas e entre oito e dez linhas, conforme o cenário;
- os 57 testes matemáticos acumulados passaram;
- a fonte original não foi gravada nem usada como destino.

## Integridade da fonte original

Arquivo: `dados/fontes/Resultados_ate_concurso_3069_sorteio.xlsx`.

SHA-256 antes e depois:

`027726F33A89738AD9DC95FAC9A7ECCD390609F5C63CACBB2F00B3873724CE67`

## Observação da execução

A primeira tentativa usou caminhos relativos duplicados e não encontrou o
gerador nem o pacote `msen`. O comando foi corrigido para o diretório `MSen`.
Em seguida, os 57 testes passaram. A sandbox também bloqueou inicialmente a
gravação binária; após autorização específica, o gerador criou somente os seis
arquivos previstos dentro de `tests/fixtures`.

Nenhum código de leitura ou importação foi implementado nesta subetapa.
