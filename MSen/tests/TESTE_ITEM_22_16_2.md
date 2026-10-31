# Evidência da subetapa 22.16.2

## Implementação

- A página auxiliar consulta `GET /api/frequencias/serie` com os mesmos quatro
  filtros da página de origem.
- `Evolução dos intervalos` mostra mínimo, média e máximo em concursos.
- `Faixa prevista e ocorrências reais` mostra faixa inferior/superior,
  previsão central e pontos reais na escala dos números dos concursos.
- Cada gráfico ocupa uma linha, usa a largura do cartão e possui 30 rem de
  altura, com SVG de 1.440 por 500.
- A consulta pode ser repetida após mudar dezena, evento ou período.
- Nenhuma rota, regra de cálculo ou tabela foi criada ou alterada.

## Verificação

- `npm run test:frontend`: 55 testes aprovados.
- `npx playwright test frontend/tests/browser/frequencias.spec.mjs`: 9 fluxos
  aprovados no Google Chrome.
- O fluxo específico confirmou dois cartões e dois SVG, altura visual mínima de
  450 px, duas ocorrências reais e inexistência de coordenadas `NaN`.
- A regressão da página continuou aprovada em 1.280 px e 520 px.

## Limite preservado

Foi mantida a escala vertical automática existente. Zoom vertical 10×, aviso
de recorte e alternância de escala pertencem somente à subetapa 22.16.3.
