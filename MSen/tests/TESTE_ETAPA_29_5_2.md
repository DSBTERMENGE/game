# Teste da subetapa 29.5.2 — iteração contínua

Data: 11/11/2026

## Alteração

- o funil extensível deixou de executar `tuple(combinacoes)`;
- os dois funis passaram a contar aprovações independentemente da lista de
  combinações aprovadas;
- `guardar_aprovadas=False` permite relatório somente com contadores;
- a retenção permanece habilitada por padrão para compatibilidade;
- o total declarado do iterador é conferido ao término.

## Testes automatizados

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_contrato_funil_extensivel tests.test_funil_screener tests.test_api_screener
```

Resultado: 21 testes aprovados. Permaneceram somente avisos preexistentes sobre
arquivos de frontend abertos nos testes da API.

## Teste real de regressão

O serviço conectado ao banco local retornou:

- analisadas: 5.000;
- excluídas: 4.586;
- aprovadas: 414;
- reconciliação: correta.

A aplicação integral permaneceu desabilitada.
