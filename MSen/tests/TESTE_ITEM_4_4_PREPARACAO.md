# Preparação do Item 4.4 — importação inicial controlada

Data: 2026-10-26.

## Estado

A implementação e a homologação em ambiente descartável foram concluídas. A
importação no PostgreSQL persistente ainda não foi executada, pois faltam a
configuração `GAME_DB_*`, a confirmação do database de destino e a confirmação
do backup.

## Testes automatizados

- três testes específicos aprovados;
- 109 testes acumulados aprovados;
- conversão do resultado calculado para histórico preserva todos os dados;
- relatório JSON gravado e lido sem campos de senha ou conexão;
- objeto inválido rejeitado pelo gravador de relatório.

## Homologação com a planilha real

Ambiente: PostgreSQL 16.11 temporário, database `games_test`, porta 55444.

Primeira importação:

- registros antes: 0;
- linhas analisadas: 3.069;
- linhas inseridas: 3.069;
- iguais: 0;
- alteradas: 0;
- inválidas: 0;
- registros depois: 3.069.

Amostras armazenadas:

- concurso 1: soma `165`, média `27.500000`, mediana `31.5`, desvio
  `17.689451`, média X `3.166667`, média Y `2.333333`;
- concurso 3069: soma `194`, média `32.333333`, mediana `33.0`, desvio
  `18.217818`, média X `4.666667`, média Y `2.666667`.

Frequências:

- linhas: 60;
- dezenas com ocorrência: 60;
- soma de ocorrências: 18.414, equivalente a 3.069 resultados × 6 dezenas.

Segunda importação:

- registros antes e depois: 3.069;
- inseridas: 0;
- iguais: 3.069;
- alteradas: 0;
- inválidas: 0.

Os dois relatórios JSON foram gerados e validados dentro do ambiente de teste. O
resumo permanente está neste documento, sem credenciais e sem os 3.069 números
repetidos desnecessariamente.

## Isolamento

O cluster temporário foi parado e removido, e a porta 55444 ficou sem resposta.
Os PostgreSQL persistentes 16 e 18 e o PythonAnywhere não foram alterados.
