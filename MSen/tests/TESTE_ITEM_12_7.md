# Evidência do Item 12.7 — regressão integrada e fechamento

Data: 2026-10-27.

## Regressão completa

- Python: 216 testes aprovados;
- frontend: 22 testes aprovados;
- Google Chrome: 8 fluxos aprovados;
- Google Chrome com PostgreSQL: 3 fluxos aprovados.

Na primeira execução, os três fluxos integrados falharam porque ainda esperavam
o catálogo antigo de seis padrões. As expectativas foram adaptadas para os nove
padrões atuais e para os próximos códigos livres `PG_004`, `PD_010` e
`PD_011`. Depois da adaptação, os três fluxos passaram. A falha inicial não
indicava defeito na aplicação.

## Auditoria operacional

- migrações `001` a `006` aplicadas, sem migração pendente;
- nenhum database temporário remanescente;
- banco `games` com 3.069 resultados;
- API saudável com nove padrões e nove detectores implementados;
- servidor local ativo no PID 12888;
- grade real validada com os nove registros.

Estatísticas das dezenas na mesma linha:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_007` | 2.053 | 1,495127 | 0,852399 |
| `PD_008` | 863 | 3,554524 | 2,902303 |
| `PD_009` | 93 | 33,141304 | 35,099728 |

PythonAnywhere não foi alterado. As mudanças da Etapa 12 permanecem sem commit
até autorização expressa do usuário.
