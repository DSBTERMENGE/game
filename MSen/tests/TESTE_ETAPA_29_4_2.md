# Teste da subetapa 29.4.2 — liberação controlada da cobertura

Data: 11/11/2026

## Resultado

O procedimento de confirmação da cobertura somente aceita o estado
`HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`. Antes da liberação, ele repete as
verificações de catálogo, assinaturas das funções e regras, avaliações,
perfis operacionais e correspondência entre filtros carregados e homologados.

A atualização exige que a quantidade de resultados permaneça igual, que a
assinatura do conjunto de resultados exista e que os perfis possuam data de
atualização. Alteração concorrente do estado cancela a liberação.

O banco local não foi modificado nesta subetapa.

## Teste executado

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_homologacao_screener tests.test_api_screener tests.test_contrato_funil_extensivel tests.test_funil_screener
```

Resultado: 24 testes aprovados. Permaneceram somente avisos preexistentes de
arquivos de frontend abertos pelos testes.
