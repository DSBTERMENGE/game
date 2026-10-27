# Evidência de teste — Item 9.8

Data: 2026-10-26

## Fluxo integrado real dos padrões

Um database PostgreSQL temporário percorreu no Google Chrome:

1. inclusão de resultados históricos pela API;
2. detecção exclusiva dos três padrões sequenciais;
3. cálculo de ocorrências, intervalos, médias e desvios;
4. persistência das estatísticas;
5. consulta pela API e apresentação na grade;
6. edição de texto preservada após novo recálculo;
7. criação de padrão sem detector como `PD_004`;
8. edição e exclusão de `PD_004`;
9. criação seguinte como `PD_005`, sem reutilização;
10. exclusão de padrão implementado respeitada após alterar o histórico;
11. padrão sem detector mantido com estatísticas nulas.

O database temporário foi removido ao final.

## Ensaio de restauração e atualização

O backup `games_pos_importacao_20261026.dump` foi restaurado em database
temporário. SHA-256 conferido:
`96814C5A3D92D15EB9309697F6EF2DFD68526EBDCDE85112181FBEED7B73BA1F`.

Após a restauração:

- 3.069 resultados e 60 frequências estavam preservados;
- total de ocorrências das dezenas: 18.414;
- migração `001` já existia;
- migrações `002` e `003` foram aplicadas;
- os padrões foram recalculados com 1.192, 92 e 5 ocorrências;
- médias e desvios coincidiram exatamente com o banco local;
- o database temporário foi removido.

## Regressão completa

- 174 testes Python aprovados;
- 20 testes unitários de frontend aprovados;
- 4 fluxos no Google Chrome com API isolada aprovados em 3,3 segundos;
- 3 fluxos Google Chrome/PostgreSQL aprovados em 13,3 segundos;
- `git diff --check` sem erro de conteúdo;
- nenhum database ou servidor temporário permaneceu;
- PythonAnywhere não foi acessado.

## Banco local persistente

O `games` permaneceu com:

- 3.069 resultados;
- 60 linhas de frequência;
- três padrões operacionais;
- migrações `001`, `002` e `003` registradas.

Os testes CRUD mutáveis foram executados somente no database temporário.

## Conclusão

O fluxo completo da Etapa 9 está integrado, restaurável e sem pendência crítica
conhecida no escopo implementado.
