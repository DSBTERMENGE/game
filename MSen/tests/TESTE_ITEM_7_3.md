# Evidência de teste — Item 7.3

Data: 2026-10-26

## Regressão completa local

- Python: 140 testes aprovados com `unittest`.
- Frontend unitário: 19 testes aprovados.
- Google Chrome com API isolada: 3 fluxos aprovados.
- Google Chrome com PostgreSQL real: 2 fluxos aprovados.
- Fluxo Excel até PostgreSQL: importação, cálculos, frequências, relatório e
  reimportação sem duplicidade aprovados.
- Fluxo PostgreSQL até gráficos: carregamento, navegação, voo, mancha e limpeza
  aprovados.

## Ensaio de restauração

Backup local utilizado:
`MSen/dados/backups/games_pos_importacao_20261026.dump`.

- Tamanho: 105.199 bytes.
- SHA-256:
  `96814C5A3D92D15EB9309697F6EF2DFD68526EBDCDE85112181FBEED7B73BA1F`.
- PostgreSQL/`pg_restore`: versão 16 instalada localmente.
- Destino: database efêmero com nome protegido pelo padrão de testes.
- Resultados restaurados: 3.069.
- Registros em `frequencia_de_resultado`: 60.
- Total de ocorrências: 18.414.
- O database efêmero foi removido automaticamente após a conferência.
- A listagem antes e depois do ensaio confirmou ausência de databases de teste
  residuais.

## Conclusão

Os critérios do Item 7.3 foram atendidos. Não foi encontrada pendência crítica
no escopo implementado. Nenhuma publicação ou alteração no PythonAnywhere foi
realizada.
