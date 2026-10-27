# Evidência do Item 12.5 — recálculo de linhas no database local

Data: 2026-10-27.

## Backup anterior à migração e ao recálculo

- arquivo: `MSen/dados/backups/games_pre_recalculo_colunas_20261027_105900.dump`;
- tamanho: 118.044 bytes;
- SHA-256: `55DDB37760DC36DC8311A61061F188A389F2590A183625741633762F7277CED5`;
- formato PostgreSQL custom, gzip, com 78 entradas no catálogo;
- confirmado como ignorado pelo Git.

O nome do arquivo conserva o prefixo legado `colunas`; o utilitário foi ajustado
para usar `games_pre_recalculo_padroes` nos próximos backups.

## Migração e resultado

A migração `006` foi aplicada depois do backup. As versões `001`–`005` já
estavam registradas. Os 3.069 resultados, nove padrões, grupos, nomes e
descrições foram preservados.

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_007` | 2.053 | 1,495127 | 0,852399 |
| `PD_008` | 863 | 3,554524 | 2,902303 |
| `PD_009` | 93 | 33,141304 | 35,099728 |

A API local permaneceu saudável e retornou os novos valores. O processo ativo
ainda executa o código carregado antes da Etapa 12 e, por isso, informa os três
detectores como pendentes. O reinício e a validação no Chrome ficam para a
próxima subetapa. PythonAnywhere não foi alterado.
