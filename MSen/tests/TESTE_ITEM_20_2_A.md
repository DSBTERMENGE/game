# Teste da subetapa 20.2-A — estado global do algoritmo

Data: 30/10/2026

## Escopo

Criação exclusiva do DDL da linha única `estado_algoritmo_selecao`. Não foram
criados repositório, serviço de transição, API, frontend nem integração com a
importação ou com o Screener. O database local `games` e o PythonAnywhere não
foram alterados.

## Arquivos

- `database/migrations/013_criar_estado_algoritmo_selecao.sql`;
- `database/schema_postgresql.sql`;
- `database/README.md`;
- `MSen/tests/test_migracao_estado_algoritmo_selecao_ddl.py`;
- `MSen/tests/validar_migracao_estado_algoritmo_selecao.py`.

## Estrutura validada

- somente `id_estado = 1` é aceito;
- a linha inicial nasce com `atualizado = FALSE`;
- o motivo técnico inicial é `AGUARDANDO_HOMOLOGACAO_INICIAL`;
- são armazenadas as assinaturas SHA-256 do catálogo homologado e do conjunto
  de resultados usado pelos perfis;
- são armazenadas a quantidade de resultados e as datas de homologação,
  atualização dos perfis e confirmação da cobertura;
- o estado atualizado exige todas as evidências;
- quantidade negativa é rejeitada;
- a linha única não pode ser excluída nem ter sua identidade alterada.

## PostgreSQL temporário

A migração foi aplicada após 001 a 012 em database efêmero e repetida pelo
executor de migrações.

Resultados:

- somente a migração 013 foi aplicada na primeira execução;
- a segunda execução reconheceu 001 a 013 sem reaplicar nenhuma;
- estado inicial desatualizado confirmado;
- tentativa de segunda linha rejeitada;
- liberação sem evidências rejeitada;
- quantidade negativa rejeitada;
- exclusão da linha rejeitada;
- liberação com todas as evidências confirmada;
- retorno posterior ao estado desatualizado confirmado;
- o database efêmero foi removido pelo validador.

## Regressão

Resultado: **520 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

O comando `pytest` não foi usado porque o módulo não está instalado no Python
ativo. A suíte oficial foi executada com `unittest discover`, conforme a
estrutura atual dos testes.

## Resultado

Subetapa 20.2-A aprovada tecnicamente. A migração 013 ainda não foi aplicada ao
`games`. A subetapa 20.3 permanece dependente de autorização específica.
