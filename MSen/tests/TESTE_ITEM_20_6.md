# Teste da subetapa 20.6 — carga das 200 amostras iniciais

Data: 30/10/2026

## Escopo

Relacionamento dos primeiros 200 resultados, ordenados por `numero_ap`, com a
base de amostras de validação. A carga não copiou dezenas e não preencheu valores
esperados, calculados ou aprovações.

## Comportamento implementado

- consulta dos primeiros resultados por `numero_ap, id_resultado`;
- exigência de exatamente 200 resultados para a carga padrão;
- gravação somente de `id_resultado`, ordem, estado ativo e data automática;
- sincronização da matriz amostra × critério;
- verificação das posições existentes antes de qualquer inclusão;
- recusa de posição inicial ligada a resultado diferente;
- repetição idempotente;
- preservação de amostras adicionais com ordem posterior a 200;
- estado global mantido como desatualizado.

## PostgreSQL temporário

O ensaio criou 205 resultados e sincronizou os 19 critérios atuais. Confirmou:

- 200 amostras iniciais;
- 3.800 avaliações pendentes;
- extremos `numero_ap` 1 e 200 nas ordens 1 e 200;
- nenhuma coluna de dezena em `amostras_validacao`;
- leitura das dezenas por `JOIN` com `resultados`;
- nenhum esperado, calculado ou aprovado preenchido;
- segunda carga sem inclusão;
- inclusão e preservação de uma amostra adicional na ordem 201.

O database efêmero foi removido ao final.

## Aplicação local

Backup anterior:

- arquivo: `MSen/dados/backups/games_pre_amostras_20_6_20261030_040513.dump`;
- tamanho: 271.325 bytes;
- SHA-256: `43751385F36F41A0DBAAEE405CC5D766200836503AD67B948783E4E4961F68DD`;
- catálogo: 165 itens.

No `games`:

- 200 amostras relacionadas aos concursos 1–200;
- 200 concursos distintos;
- 3.800 avaliações, correspondentes a 200 × 19;
- zero avaliações preenchidas ou aprovadas;
- segunda execução idempotente;
- estado global desatualizado, motivo
  `AMOSTRAS_AGUARDANDO_REFERENCIAS_E_CALCULOS`.

## Regressão

Resultado: **533 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

Subetapa 20.6 aprovada. A base de amostras e a matriz pendente estão prontas
para a construção e conferência independente dos valores esperados na 20.7.
