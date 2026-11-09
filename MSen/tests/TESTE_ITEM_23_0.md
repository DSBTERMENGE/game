# Evidência — subetapa 23.0

Data: 03/11/2026

> Registro histórico: o horizonte configurável descrito nesta evidência foi
> substituído na Etapa 24 pelo concurso-alvo único `CA = último cadastrado + 1`.
> A decisão original é mantida abaixo apenas para auditoria.

## Objetivo

Fechar o contrato matemático e temporal da futura página `Seleção de dezenas`
antes de criar tabelas ou código executável.

## Decisões verificadas

- corte do alvo `C` igual a `C - 1`;
- centro original igual a última ocorrência mais média dos intervalos;
- centro ajustado por `j × desvio-padrão`;
- meia largura igual a `k × desvio-padrão`;
- `0 < k <= 1`, padrão 1;
- `-k <= j <= +k`, padrão 0;
- limites externos inteiros e inclusivos;
- modos compostos por união, com justificativas preservadas;
- horizonte futuro configurável, padrão 1;
- desvio zero, ausência de base e faixa passada tratados explicitamente;
- alvo 500 calculado com resultados até 499.

## Casos manuais

O contrato contém exemplos de faixa sem deslocamento, deslocamentos à direita
e à esquerda, limites inclusivos, união de `SIMPLES` com `2VS`, proteção do
concurso 500 e horizontes posteriores ao último concurso real.

## Arquivos

- `docs/CONTRATO_SELECAO_DEZENAS.md`;
- `docs/INDICE_DOCUMENTACAO.md`;
- `notas/decisoes.md`;
- `PLANO_ETAPAS_E_TESTES.md`.

## Resultado

Subetapa 23.0 concluída exclusivamente no nível contratual. Não foram criadas
tabelas, migrações, APIs, páginas ou funções de seleção.
