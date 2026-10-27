# Teste do Item 7.2

Data: 2026-10-26

## Fluxo integrado local

```text
PostgreSQL games -> Flask -> GET /api/resultados -> Google Chrome -> gráficos
```

O Flask serviu `frontend/index.html`, CSS, JavaScript e API na mesma origem. O
teste Playwright iniciou e encerrou o servidor local automaticamente.

## Resultado

- 3.069 resultados antes do teste;
- 3.069 opções exibidas no seletor;
- primeiro concurso: 1;
- último concurso: 3069;
- seis marcas e uma média no resultado individual;
- navegação circular do último para o primeiro;
- voo validado no intervalo de 0,1 segundo;
- mancha com 18.414 marcas de dezenas;
- mancha com 3.069 marcas de média;
- limpeza removeu todas as 21.483 marcas;
- 3.069 resultados depois do teste;
- duração total do teste integrado: 4,3 segundos.

## Regressão

- 1 teste PostgreSQL/Chrome integrado aprovado;
- 3 testes Chrome com API simulada aprovados;
- 19 testes unitários de frontend aprovados;
- 138 testes Python aprovados.

O teste foi somente leitura em relação ao banco. Nenhuma porta ou processo de
servidor permaneceu ativo e o PythonAnywhere não foi acessado.
