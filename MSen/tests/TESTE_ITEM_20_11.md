# Teste da subetapa 20.11 — motor de recálculo e comparação

Data: 30/10/2026

## Estado

**Concluída.** Sincronização, execução das três categorias, comparação e
consolidação foram reunidas em uma operação transacional.

## Motor integrado

`atualizar_validacao_e_auditoria` executa, nesta ordem:

1. sincronização do registro Python com o catálogo persistido;
2. criação somente dos pares amostra × critério faltantes;
3. execução dos critérios estatísticos;
4. execução dos critérios geométricos;
5. execução dos detectores de padrões;
6. consolidação por avaliação, critério e categoria;
7. gravação do motivo do bloqueio global.

Exclusões continuam exigindo confirmação explícita. Critério novo ou com regra
alterada permanece `PENDENTE`; o motor não usa a função aferida para fabricar
referências. Uma função com qualquer referência pendente não é executada nem
aprovada, enquanto as demais funções completas continuam sendo recalculadas.

O motor não declara o algoritmo global atualizado. Quando toda a homologação
passa, registra `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`, pois a liberação
também depende da cobertura operacional e da conferência do Screener.

## Aplicação no banco local

Backup anterior à execução:

- arquivo: `MSen/dados/backups/games_pre_motor_validacao_20_11_20261030_044222.dump`;
- tamanho: 311.906 bytes;
- SHA-256: `56C0837DED77EA89A1FC6F2926B7385D6C7727A459488B2B459A0D2CC7B9C638`;
- catálogo: 167 itens.

A sincronização foi idempotente: nenhum critério incluído, alterado ou excluído
e nenhuma avaliação criada. Resultado consolidado:

- critérios: 19 aprovados, zero reprovados e zero pendentes;
- avaliações: 3.800 `S`, zero `N` e zero pendentes;
- homologação matemática: concluída;
- estado global: desatualizado;
- motivo: `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`.

O hash das referências protegidas permaneceu
`2F87E7336BCEC9146DF36B165A599A11CAF7FE82EB22146438339A53C6FDED2E`
antes e depois.

## Cenários de bloqueio com rollback

Dois cenários foram executados no `games` dentro de transações obrigatoriamente
revertidas:

- uma única referência numericamente diferente produziu um `N`, marcou a função
  `REPROVADO` e gerou motivo `CRITERIOS_REPROVADOS`;
- uma única referência removida tornou a função inteira `PENDENTE`, deixou suas
  200 avaliações pendentes no relatório e gerou `REFERENCIAS_PENDENTES`.

Após os rollbacks, foram novamente confirmadas 3.800 avaliações `S` e 19
critérios `APROVADO`.

## Regressão

Resultado: **550 testes Python aprovados**. Houve somente três
`ResourceWarning` preexistentes sobre arquivos de frontend; nenhuma falha.

## Resultado

A subetapa 20.11 está encerrada. A 20.12 poderá criar o modal reutilizável de
andamento real para expor a execução do motor, mediante autorização separada.
