# Teste da subetapa 29.5.3 — execução integral no servidor

Data: 11/11/2026

## Contrato implementado

- o endpoint assíncrono aceita `escopo=integral` somente com a confirmação
  técnica `PROCESSAR_50063860_COMBINACOES`;
- o executor integral é separado do executor da amostra;
- o total inicial informado é 50.063.860;
- as combinações são produzidas por iterador preguiçoso;
- combinações aprovadas não são mantidas na memória;
- cancelamento e descarte do resultado parcial reutilizam o gerenciador já
  validado;
- a comparação com o funil anterior permanece exclusiva do teste de 5.000;
- o botão da aplicação integral continua desabilitado.

## Testes

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_api_screener tests.test_contrato_funil_extensivel tests.test_funil_screener tests.test_gerador_integral_protegido tests.test_gerador_amostral
```

Resultado: 36 testes aprovados. O teste integral usou executor controlado e não
percorreu o universo real.

## Regressão real da amostra

- analisadas: 5.000;
- excluídas: 4.586;
- aprovadas: 414;
- fechamento: correto;
- processamento integral na interface: bloqueado.

As 50.063.860 combinações não foram executadas nesta subetapa.
