# Evidências do Item 10.6 — API de grupos de padrões

Data: 2026-10-27.

## Implementação

A fábrica Flask passou a registrar `/api/grupos-padroes` e quatro serviços
configuráveis para listar, criar, editar e excluir grupos. A API valida o JSON,
protege identificador e código, limita os textos e converte erros do repositório
em respostas funcionais sem expor detalhes técnicos.

## Testes direcionados

- 11 testes próprios da API de grupos: aprovados;
- 10 testes da API existente de padrões: aprovados;
- 7 testes de configuração e fábrica Flask: aprovados.

Foram cobertos listagem, criação, edição, exclusão, código inválido, JSON
inválido, campos desconhecidos e protegidos, textos vazios, duplicidade, grupo
ocupado, registro ausente e ocultação de mensagem interna do banco.

Os testes usaram serviços simulados e não acessaram `games`. A integração HTTP
com PostgreSQL ficou reservada para o marco de integração da Etapa 10.
