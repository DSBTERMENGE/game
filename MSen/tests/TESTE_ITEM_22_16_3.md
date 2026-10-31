# Evidência da subetapa 22.16.3

## Implementação

- Adicionado seletor de escala vertical com `Automática` e `Ampliação 10×`.
- A ampliação preserva o centro e reduz a amplitude do domínio visual a um
  décimo; os valores originais permanecem inalterados.
- Cada SVG usa recorte restrito à área de plotagem.
- Valores fora do domínio ampliado são contabilizados e produzem aviso visível.
- O aviso orienta o uso da escala automática para recuperar a visão completa.
- Alternar a escala apenas redesenha a série já recebida, sem nova consulta ou
  gravação.

## Verificação

- `npm run test:frontend`: 57 testes aprovados.
- `npx playwright test frontend/tests/browser/frequencias.spec.mjs`: 9 fluxos
  aprovados no Google Chrome.
- Os testes matemáticos confirmaram que o domínio 0–100 se torna 45–55 no modo
  10×, sem alterar o objeto original.
- O Chrome confirmou aviso no modo ampliado, dois recortes SVG e desaparecimento
  do aviso ao restaurar a escala automática.

## Limites

Não foram introduzidas escalas logarítmicas, deslocamento vertical, alteração
de cálculo, nova API ou persistência de preferência visual.
