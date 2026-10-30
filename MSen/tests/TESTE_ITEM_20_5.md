# Teste da subetapa 20.5 — registro e sincronização dos critérios

Data: 30/10/2026

## Escopo

Criação do registro executável único, assinaturas automáticas da implementação e
da regra, sincronização incremental com `criterios_validacao` e aplicação local
controlada. Não foram executados cálculos sobre amostras nem preenchidos valores
esperados ou calculados.

## Registro de produção

Foram registrados 19 critérios:

- 4 estatísticos: soma, média, mediana e desvio-padrão populacional;
- 6 geométricos: extensão, perímetro, quantidade de regiões, área e coordenadas
  X/Y do centro de gravidade;
- 9 detectores dos padrões `PD_001` a `PD_009`, relacionados aos grupos atuais.

Os adaptadores escalares geométricos apenas extraem resultados das funções
oficiais; nenhuma fórmula foi duplicada.

## Sincronização validada

- critério novo entra `PENDENTE` e recebe avaliações para amostras ativas;
- repetição não duplica catálogo nem avaliações;
- mudança somente da implementação preserva esperado e conferência, mas limpa
  calculado, execução e aprovação;
- mudança da regra preserva a linha, mas limpa esperado, calculado e aprovação;
- mudança estrutural de categoria, tipo, precisão ou grupo para o mesmo código é
  recusada, exigindo novo código estável;
- critério ausente do registro não é excluído sem confirmação explícita;
- exclusão confirmada usa a cascata já aprovada;
- qualquer alteração mantém o estado global desatualizado.

## Assinaturas

- `assinatura_funcao`: SHA-256 do código-fonte da função e das dependências
  declaradas;
- `assinatura_regra`: SHA-256 do código, categoria, tipo, precisão, grupo e
  descrição inequívoca da regra matemática.

A migração 014 adicionou `assinatura_regra` obrigatória ao catálogo.

## PostgreSQL temporário

O ensaio confirmou inclusão, avaliações automáticas, alteração de implementação,
alteração de regra, proteção contra exclusão não confirmada, exclusão confirmada,
idempotência e atualização do estado global. O database efêmero foi removido.

## Aplicação local

Antes da aplicação foi criado o backup:

- arquivo: `MSen/dados/backups/games_pre_registro_criterios_20_5_20261030_035349.dump`;
- tamanho: 264.601 bytes;
- SHA-256: `918D32E4E91EA33F71495BA6C1FAF327813441BD5A842ACF7D93877924C45740`;
- catálogo do backup: 159 itens.

No `games`:

- somente a migração 014 foi aplicada;
- foram incluídos 19 critérios pendentes;
- totais por categoria: 4 estatísticos, 6 geométricos e 9 de padrões;
- avaliações: 0, pois as amostras ainda não foram carregadas;
- estado global: desatualizado, motivo `CATALOGO_DE_CRITERIOS_ALTERADO`;
- a segunda sincronização não alterou dados.

## Regressão

Resultado: **531 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.5 aprovada. O registro e o catálogo estão prontos para a atualização
dos perfis da 20.5-A e para a carga das amostras da 20.6. Nenhuma função foi
homologada antecipadamente.
