# Evidências do Item 10.3 — aplicação local da migração 004

Data: 2026-10-27.

## Backup

Antes da migração foi criado o backup local ignorado pelo Git:

```text
MSen/dados/backups/games_pre_migracao_004_20261027_075306.dump
```

- tamanho: 111.847 bytes;
- SHA-256: `1F3FE26CF8202F97A2CAF9909EF6669F1C6488563727DA08C3F57BF98B98A8ED`.

## Precaução descoberta

O `games` continha seis padrões. `PD_004`, `PD_005` e `PD_006` estudam dezenas
na mesma coluna e não poderiam ser associados a “Dezenas sequenciais”. Antes da
aplicação, a migração foi corrigida e novamente ensaiada em database temporário:

- `PD_001`–`PD_003` → `PG_001 — Dezenas sequenciais`;
- `PD_004`–`PD_006` → `PG_002 — Dezenas na mesma coluna`;
- qualquer outro código não classificado interrompe a migração;
- sequências foram recalibradas em `PG_002` e `PD_006`.

O ensaio preservou seis padrões e estatísticas e removeu o database temporário.
O esquema canônico criado do zero produziu dois grupos e três padrões iniciais.

## Aplicação no `games`

- migrações existentes: `001`, `002`, `003`;
- migração aplicada: `004`;
- resultados preservados: 3.069;
- frequências preservadas: 60;
- grupos: 2;
- padrões preservados: 6;
- estatísticas de `PD_001`, `PD_002` e `PD_003`: preservadas integralmente;
- `PD_004`, `PD_005` e `PD_006`: permaneceram com estatísticas nulas.

## Servidor local

Foi encontrado um processo Python antigo, PID 228, iniciado em 2026-10-26, que
compartilhava a porta 5050 e respondia com código antigo. Ele e a primeira
tentativa atual, PID 7356, foram encerrados. Uma única instância atualizada foi
iniciada:

- PID: 23176;
- endereço: `http://127.0.0.1:5050/`;
- `/api/saude`: HTTP 200;
- `/api/grupos-padroes`: HTTP 200, 2 grupos;
- `/api/padroes`: HTTP 200, 6 padrões;
- Painel e três páginas de cadastro: HTTP 200.

PythonAnywhere não foi acessado.
