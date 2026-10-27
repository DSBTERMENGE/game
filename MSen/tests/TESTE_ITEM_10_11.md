# Evidências do Item 10.11 — integração completa

Data: 2026-10-27.

## Fluxos Chrome/PostgreSQL

Três testes integrados foram executados sequencialmente no Google Chrome:

1. Excel → API → cálculos → PostgreSQL temporário → relatório → reimportação
   sem duplicidade.
2. Histórico → estatísticas → grupos → padrões → API → páginas CRUD em
   PostgreSQL temporário.
3. PostgreSQL local `games` → Painel → navegação → voo → mancha → página de
   padrões, exclusivamente para leitura.

O segundo fluxo criou `PG_003`, criou `PD_004` associado, transferiu o padrão
para `PG_001`, preservou estatísticas, excluiu o padrão e depois excluiu o grupo
vazio. Também confirmou código não reutilizado e exclusão respeitada após novo
recálculo.

Resultado: 3 testes integrados aprovados em 16 segundos.

## Auditoria final

- databases temporários restantes: zero;
- `games.resultados`: 3.069;
- `games.frequencia_de_resultado`: 60;
- grupos: 2;
- padrões: 6;
- `PG_001`: 3 padrões;
- `PG_002`: 3 padrões;
- estatísticas de `PD_001`–`PD_003`: preservadas;
- servidor `http://127.0.0.1:5050/`: saudável.

PythonAnywhere não foi acessado e o teste integrado não escreveu no `games`.
