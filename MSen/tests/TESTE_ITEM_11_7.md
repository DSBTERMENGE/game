# Evidência do Item 11.7 — regressão integrada e fechamento

Data: 2026-10-27.

## Incompatibilidade encontrada e corrigida

A primeira regressão integrada teve dois fluxos aprovados e um reprovado porque
uma instalação nova possuía apenas `PD_001`–`PD_003`; assim, um cadastro livre
recebia indevidamente o código reservado `PD_004` e aparecia como detector
implementado.

A migração `005_inicializar_padroes_colunas.sql` passou a reservar e cadastrar
`PD_004`–`PD_006` em `PG_002`, posicionando o primeiro código livre em `PD_007`.
Ela preserva registros oficiais existentes e interrompe a operação se um código
reservado pertencer a outro grupo. O esquema canônico foi atualizado.

## Validações finais

- 205 testes Python aprovados;
- 22 testes de frontend aprovados;
- 8 fluxos Chrome aprovados;
- 3 fluxos Chrome/PostgreSQL aprovados após a correção;
- migrações `001`–`005` validadas sobre estrutura anterior;
- seis padrões e duas associações de grupo preservados;
- esquema canônico criado do zero com dois grupos e seis padrões;
- sequência de padrões posicionada em `PD_006`;
- nenhum database temporário permaneceu;
- `games` confirmado na versão `005`;
- grade real validada no Chrome com seis padrões implementados.

## Estado local

O `games` permanece com 3.069 resultados. As estatísticas verticais finais são:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_004` | 1.037 | 2,960425 | 2,387099 |
| `PD_005` | 66 | 45,969231 | 42,006948 |
| `PD_006` | 4 | 696,666667 | 373,443734 |

O servidor local permanece saudável no PID 8556. PythonAnywhere não foi
acessado. As alterações da Etapa 11 ainda não foram commitadas.
