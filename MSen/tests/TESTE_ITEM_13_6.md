# Evidência do Item 13.6 — serviço de cálculo histórico

Data: 2026-10-27.

Foi criado `msen.services.analise_geometrica`, responsável por converter as
medidas exatas e coordenar sua persistência. O serviço oferece:

- cálculo e gravação de um `ResultadoPersistido`;
- recálculo do histórico conhecido em uma única transação;
- relatório com quantidade processada e análises persistidas;
- versão explícita do algoritmo geométrico.

Inclusão e edição de resultado agora calculam a análise individual na mesma
transação das frequências e dos padrões. A importação incremental recalcula as
análises do histórico dentro de sua transação.

Em PostgreSQL temporário foram exercitados os fluxos reais:

- inclusão: área `36,000000000000`;
- importação incremental: uma linha nova, uma igual e área `4,500000000000`;
- edição: substituição da figura por uma colinear, área zero e CG nulo;
- recálculo integral executado duas vezes com resultado idêntico;
- dois resultados e duas análises, preservando a relação individual.

Os 249 testes Python passaram. O database temporário foi removido. O banco
local `games` não foi conectado ou alterado e permanece com seus 3.069
resultados e migrações somente até `006`. PythonAnywhere não foi alterado.
