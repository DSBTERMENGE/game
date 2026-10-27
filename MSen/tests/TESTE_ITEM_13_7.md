# Evidência do Item 13.7 — desenho geométrico no painel

Data: 2026-10-27.

A resposta de `/api/resultados` passou a fornecer, calculada em memória:

- seis vértices em ordem crescente;
- contornos de todas as regiões fechadas;
- extensão aberta, perímetro, área total e quantidade de regiões;
- centro de gravidade único ou nulo para área zero.

O painel converte somente as coordenadas lógicas recebidas em pixels. Ele
desenha regiões com preenchimento transparente, linha aberta verde, fechamento
tracejado, seis pontos de aproximadamente 2 mm, média espacial e centro de
gravidade. Um resumo horizontal apresenta extensão, perímetro, área e regiões,
sem criar uma nova faixa vertical de comandos. O redimensionamento reutiliza as
coordenadas lógicas e redesenha todos os elementos.

Validações aprovadas:

- 250 testes Python, incluindo o contrato geométrico da API;
- 23 testes unitários do frontend;
- 8 fluxos reais no Google Chrome;
- figura cruzada com duas regiões, fechamento, CG e resumo numérico;
- navegação, voo, mancha e páginas de cadastro sem regressões.

Os testes de Chrome inicialmente revelaram seletores antigos das caixas de nome,
alteradas anteriormente para multilinha. Os seletores foram ajustados pelas
etiquetas acessíveis e os oito fluxos passaram. O banco `games`, a migração
`007` e o PythonAnywhere não foram alterados.
