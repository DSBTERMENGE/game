# Teste do Item 16.10 — fechamento da Etapa 16

Data: 28/10/2026

## Proteção e aplicação no `games`

Antes da alteração, a auditoria confirmou:

- migrações `001` a `007`;
- 3.069 resultados;
- 60 linhas de frequência;
- 3.069 análises geométricas;
- ausência da tabela de classificações.

Foi criado o backup local ignorado pelo Git:

```text
MSen/dados/backups/games_pre_classificacao_20261028_100708.dump
```

- tamanho: 226.601 bytes;
- catálogo validado: 100 itens;
- SHA-256:
  `9C662ADC4EC8E94336C13E2D576AC91F6AD706C10D56DB8E3D4F78B1D389880E`.

Somente a migração `008` foi aplicada. O recálculo foi executado duas vezes e
preservou todas as identidades.

## Estado final do banco local

- migrações: `001` a `008`;
- resultados: 3.069, preservados;
- frequências: 60, preservadas;
- análises geométricas: 3.069, preservadas;
- classificações de `PG_001`: 3.069;
- `PD_001`: 1.192;
- `PD_002`: 92;
- `PD_003`: 5;
- `SEM_CORRESPONDENCIA`: 1.780;
- indicação experimental a 10%: `PD_002` e `PD_003`;
- screener: inativo para esses critérios.

## Servidor e Chrome

A porta 5050 possuía duas instâncias Python simultâneas: PID 29532, iniciado no
dia anterior, e a primeira instância nova PID 18528. Isso fez o Chrome alcançar
o código antigo e receber 404 na nova rota. As duas instâncias foram encerradas.

Foi iniciado um único servidor com o caminho local explícito:

- PID: 17116;
- endereço: `http://127.0.0.1:5050/`;
- API do perfil: 3.069 resultados, 1.289 classificados, 1.780 sem
  correspondência e `ativa_no_screener=false`.

O Google Chrome real confirmou quatro classes, dois padrões indicados, painel
absoluto, grade principal com 638 px de altura, rolagem interna e corte até o
concurso 100.

## Regressão final

- 410 testes Python: aprovados;
- 24 testes JavaScript: aprovados;
- 12 fluxos completos no Google Chrome: aprovados;
- 3 fluxos integrados Excel/API/PostgreSQL/Chrome: aprovados;
- nenhum database temporário remanescente;
- `git diff --check`: sem erro, somente avisos de conversão LF/CRLF.

PythonAnywhere não foi acessado. Nenhum commit foi criado nesta subetapa.
