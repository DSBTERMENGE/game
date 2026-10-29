# Teste da subetapa 18-D.6

Data: 2026-10-29

## Objetivo

Retirar com segurança as apresentações antigas do Screener e manter uma única
página e uma única API oficiais, sem apagar cálculos ainda utilizados.

## Componentes retirados

- `frontend/screener-extensivel.html`, página duplicada após a migração;
- `frontend/screener-prototipo.html` e seus JavaScripts com dados fictícios;
- `frontend/js/screener.js`, exclusivo da interface antiga;
- `GET /api/screener/quadro` e o nome transitório
  `POST /api/screener/quadro-extensivel`;
- `quadro_ativo.py` e seus testes, exclusivos do quadro antigo;
- testes de interface dedicados ao protótipo removido.

## Contrato consolidado

- página pública: `frontend/screener.html`;
- execução pública: `POST /api/screener/quadro`;
- amostra protegida: 5.000 combinações;
- relatório: três níveis de julgamento;
- comparação interna: primeiro funil preservado como referência matemática,
  sem página nem API pública própria.

## Verificações

- nenhuma referência operacional aponta para páginas, rota ou protótipo
  retirados;
- as URLs estáticas antigas não são mais servidas;
- a rota oficial aceita apenas POST;
- a documentação corrente aponta para o contrato oficial;
- nenhum acesso ou alteração de banco foi introduzido nesta subetapa.

## Testes executados

- regressão Python: 503 aprovados;
- regressão JavaScript: 32 aprovados;
- regressão Chrome/Playwright: 18 aprovados;
- integração: 5 testes, sendo 3 aprovados e 2 ignorados porque dependem do
  PostgreSQL local.

## Resultado

Subetapa aprovada tecnicamente. O usuário não encontra mais duas opções de
Screener nem o protótipo fictício; a comparação matemática interna permanece
funcional.
