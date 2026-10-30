# Teste da subetapa 20.5-A — perfis operacionais atuais

Data: 30/10/2026

## Escopo

Integração da chegada de novos resultados ao recálculo substitutivo dos perfis
estatísticos, geométricos, classificações e incidências de padrões. Não foram
criadas versões históricas dos perfis nem executadas as 200 provas matemáticas.

## Estrutura

A migração 015 criou `perfis_operacionais_atuais`, com uma linha por grandeza:

- código e categoria;
- quantidade total de resultados;
- quantidade com valor e quantidade ausente;
- média, desvio-padrão populacional, mínimo e máximo;
- instante do recálculo.

O código é a chave primária. Um novo recálculo substitui a linha anterior; não
existe versão de perfil operacional.

## Fluxo implementado

- antes do recálculo, o estado global é persistido como desatualizado;
- novos resultados continuam recebendo os valores derivados na inserção;
- os padrões `PD_001`–`PD_009` têm incidência e denominador recalculados;
- a classificação existente do grupo sequencial é refeita;
- as análises geométricas são reconciliadas para todos os resultados;
- quatro perfis estatísticos e seis geométricos são substituídos;
- uma assinatura SHA-256 identifica exatamente o conjunto de resultados usado;
- quantidade e assinatura são gravadas no estado global;
- avaliações e homologações das funções não são alteradas;
- o algoritmo permanece bloqueado até homologação e cobertura serem confirmadas.

## PostgreSQL temporário

O ensaio começou com três resultados e uma avaliação homologada. Confirmou:

- 10 perfis calculados para os três resultados;
- nove padrões com denominador três;
- avaliação homologada preservada integralmente;
- inclusão de um quarto resultado;
- bloqueio persistido antes do segundo recálculo;
- 10 perfis substituídos com quantidade quatro;
- mudança da assinatura do conjunto;
- nove padrões com denominador quatro;
- estado ainda bloqueado após o sucesso.

O database efêmero foi removido ao final.

## Aplicação local

Backup anterior:

- arquivo: `MSen/dados/backups/games_pre_perfis_20_5a_20261030_040121.dump`;
- tamanho: 267.404 bytes;
- SHA-256: `19A0BDE10AC8D4E83B089835A15D3BB0B6B619F893BD28FAA4C586A8D1290D4B`;
- catálogo: 160 itens.

No `games`:

- somente a migração 015 foi aplicada;
- 10 perfis foram calculados sobre os 3.069 resultados;
- os nove padrões usam denominador 3.069;
- assinatura do conjunto:
  `2b531e5d6b80fae13b6f969f29eac19cea19c654d0443c8cb5f0dab5eb422d48`;
- nenhuma avaliação foi criada ou alterada;
- estado global: desatualizado, motivo
  `HOMOLOGACAO_OU_COBERTURA_PENDENTE`.

## Regressão

Resultado: **533 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.5-A aprovada. Importações com novos resultados passam a bloquear o
algoritmo antes do processamento e a atualizar todos os perfis atuais dentro da
operação. A homologação matemática permanece independente e não é refeita por
causa do aumento do histórico.
