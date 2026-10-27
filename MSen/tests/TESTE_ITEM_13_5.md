# Evidência do Item 13.5 — persistência geométrica temporária

Data: 2026-10-27.

Foi criada a migração `007_criar_analise_geometrica_resultado.sql`. A nova
tabela mantém relação individual com `resultados` e armazena:

- extensão aberta e perímetro fechado com doze casas decimais;
- quantidade de regiões e área total;
- coordenadas opcionais do centro de gravidade;
- versão do cálculo e data de atualização.

As restrições garantem medidas não negativas, perímetro não inferior à extensão,
coerência entre quantidade de regiões e área, presença conjunta das coordenadas,
centro nulo exatamente quando a área é zero, limites da matriz e remoção em
cascata quando o resultado é excluído.

O repositório `RepositorioAnaliseGeometrica` consulta e grava as medidas por
`id_resultado`, arredonda somente na persistência e usa `ON CONFLICT` para
recalcular sem duplicar linhas.

Em PostgreSQL temporário foram confirmados:

- migrações `001` a `007`;
- área `36,000000000000` e CG `(4,125000000000; 2,500000000000)`;
- estado de área zero com centro nulo;
- salvamento idempotente;
- rejeição de área sem região e de resultado inexistente;
- exclusão em cascata;
- criação do esquema canônico com 3 grupos, 9 padrões e a tabela geométrica.

O database temporário foi removido e a listagem final ficou vazia. Os 249 testes
Python passaram. O banco local `games` e o PythonAnywhere não foram alterados.
