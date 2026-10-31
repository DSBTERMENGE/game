# Evidência da subetapa 22.16.1

## Implementação

- Criada `frontend/graficos-frequencias.html` com cabeçalho, seleção recebida,
  área reservada aos gráficos e duas formas de retorno.
- Incluído `Abrir gráficos` no bloco `Evolução histórica por dezena`.
- Criado contrato de navegação em
  `frontend/js/navegacao-graficos-frequencias.js`.
- Preservados dezena, tipo de evento, concurso inicial e concurso final na ida e
  na volta.
- O retorno usa a âncora `#evolucao-historica-dezena`.
- Nenhuma API foi acrescentada e nenhum dado ou configuração foi persistido.

## Verificação

- `npm run test:frontend`: 55 testes aprovados.
- `npx playwright test frontend/tests/browser/frequencias.spec.mjs`: 9 fluxos
  aprovados no Google Chrome.
- O fluxo de navegador verificou ida, filtros recebidos, retorno, filtros
  restaurados e posicionamento no bloco de origem.
- A regressão da página também passou em 1.280 px e 520 px.

## Limite preservado

Os gráficos ampliados e as escalas não foram implementados. Permanecem,
respectivamente, nas subetapas 22.16.2 e 22.16.3.
