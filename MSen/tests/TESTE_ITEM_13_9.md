# Evidência do Item 13.9 — aplicação controlada no histórico local

Data: 2026-10-27.

## Proteção e migração

Antes de alterar o `games`, o script confirmou 3.069 resultados, migrações
`001–006` e ausência da tabela geométrica. Foi criado o backup custom:

```text
MSen/dados/backups/games_pre_geometria_20261027_132845.dump
Tamanho: 118.150 bytes
SHA-256: 4A39BE414502479081F53048FF4F7AA88309BDAD192629140821212C90AFA8FC
Itens no catálogo pg_restore: 89
```

O catálogo do backup foi lido pelo `pg_restore` e contém `resultados`. O arquivo
está ignorado pelo Git. Em seguida, somente a migração `007` foi aplicada.

## Recálculo

As 3.069 análises foram gravadas em relação individual com os 3.069 resultados.
Nenhum resultado foi incluído, alterado ou removido. Resumo inicial obtido:

- área mínima: `1,500000000000`;
- área máxima: `29,500000000000`;
- área média: `9,5777839879303392`;
- regiões por resultado: mínimo 1 e máximo 4;
- centros de gravidade nulos: 0.

Uma segunda auditoria confirmou que não existem migrações pendentes e que o
histórico está nas versões `001–007`.

## Servidor e Google Chrome

O servidor foi reiniciado no PID 37548 e permaneceu saudável em
`http://127.0.0.1:5050`. A API retornou 3.069 resultados com seis vértices,
regiões, área e CG. A primeira carga completa levou aproximadamente 8,1
segundos, ponto que será revisto no fechamento da etapa.

O validador real no Google Chrome confirmou, nos dois primeiros concursos:

- linha aberta, fechamento, seis vértices, regiões, média e CG;
- concurso 1: área 12,625 e duas regiões;
- concurso 2: área 7,000 e duas regiões;
- resumo numérico e diálogo de aparência.

Nenhum dado foi modificado durante a validação visual. PythonAnywhere não foi
alterado.
