# Teste do Item 4.4 — importação inicial controlada

Data: 2026-10-26.

## Destino confirmado

- PostgreSQL: 16.11;
- host: `127.0.0.1`;
- porta: 5432;
- usuário: `postgres`;
- database exclusivo: `games`;
- database `games` antes da operação: inexistente.

Os valores foram definidos em `MSen/.env`, ignorado pelo Git. A senha não foi
exibida nem registrada nos relatórios.

## Criação e migração

O database `games` foi criado em UTF-8 a partir de `template0`. A migração `001`
foi aplicada e registrada com checksum
`dfa29d6966b260b719e30bcb63ae58b0a98d744d44cdfcfd648eafd0f1a9bd87`.

## Importação inicial

- registros antes: 0;
- linhas analisadas: 3.069;
- inseridas: 3.069;
- iguais: 0;
- alteradas: 0;
- inválidas: 0;
- registros depois: 3.069;
- menor e maior concurso: 1 e 3069;
- soma de `soma_res`: 561.917.

Foram atualizadas as 60 linhas de `frequencia_de_resultado`. Todas possuem
ocorrências, e a soma de `num_oco` é 18.414, exatamente 3.069 × 6.

## Amostragem

- concurso 1: soma `165`, média `27.500000`, mediana `31.5`, desvio
  `17.689451`, X `3.166667`, Y `2.333333`;
- concurso 3069: soma `194`, média `32.333333`, mediana `33.0`, desvio
  `18.217818`, X `4.666667`, Y `2.666667`.

## Reimportação

- registros antes e depois: 3.069;
- inseridas: 0;
- iguais: 3.069;
- alteradas: 0;
- inválidas: 0.

Os relatórios completos estão em `MSen/dados/relatorios`, ignorados pelo Git e
sem parâmetros de conexão ou credenciais.

## Backup

Não houve backup anterior porque o database `games` não existia. Após a
importação foi criado e validado com `pg_restore --list`:

- arquivo: `MSen/dados/backups/games_pos_importacao_20261026.dump`;
- tamanho: 105.199 bytes;
- SHA-256: `96814C5A3D92D15EB9309697F6EF2DFD68526EBDCDE85112181FBEED7B73BA1F`.

O dump é ignorado pelo Git.

## Testes finais

- três testes específicos da preparação aprovados;
- 109 testes acumulados aprovados;
- hash da planilha fonte preservado:
  `027726F33A89738AD9DC95FAC9A7ECCD390609F5C63CACBB2F00B3873724CE67`.

O database `financas`, os outros projetos e o PythonAnywhere não foram
alterados.
