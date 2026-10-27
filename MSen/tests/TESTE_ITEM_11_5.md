# Evidência do Item 11.5 — recálculo no database local

Data: 2026-10-27.

## Backup anterior ao recálculo

- arquivo: `MSen/dados/backups/games_pre_recalculo_colunas_20261027_090452.dump`;
- tamanho: 117.894 bytes;
- SHA-256: `4FF31B6CFF1EEA32B916147CE469AABEC724E114F349AB2A1F78C200CB3C1C62`;
- formato PostgreSQL custom, gzip, com 78 entradas no catálogo;
- confirmado como ignorado pelo Git.

O backup foi concluído antes da abertura da transação de recálculo.

## Resultado provisório posteriormente substituído

Os 3.069 resultados e os seis cadastros foram preservados. Nomes, descrições e
grupos não foram alterados. As estatísticas sequenciais permaneceram iguais e
foram calculados:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_004` | 2.168 | 1,414859 | 0,766163 |
| `PD_005` | 306 | 10,042623 | 9,638455 |
| `PD_006` | 13 | 223,416667 | 233,685850 |

A API local permaneceu saudável e retornou os seis padrões com os novos
valores. Como o processo ativo ainda executa o código carregado antes do Item
11.4, ele continua informando `detector_implementado=false` para `PD_004`–
`PD_006`; o código novo já passou nos testes e será carregado no reinício
controlado do Item 11.6. Nenhuma alteração foi feita no esquema ou no
PythonAnywhere.

## Divergência textual encontrada

O usuário esclareceu no Item 11.6 que os textos estavam corretos quanto à
exigência de linhas subjacentes. Portanto, os valores acima foram considerados
provisórios e substituídos pelo recálculo correto documentado no Item 11.6. O
backup deste item preserva o estado anterior e continua válido.
