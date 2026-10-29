# Teste da subetapa 18-D.5

Data: 2026-10-29

## Objetivo

Remover o mecanismo provisório de validação humana sem antecipar ou alterar a
futura funcionalidade de Validação e auditoria prevista para a Etapa 20.

## Alterações verificadas

- o montador legado não cria mais casos de validação humana;
- a resposta da rota antiga não contém a coleção `validacoes`;
- o parâmetro `limite_validacoes` foi retirado da rota antiga;
- o JavaScript antigo não cria seletores de resultado esperado nem calcula
  conformidade local;
- a página vazia `auditoria.html` não foi alterada;
- a rota e os arquivos restantes do screener legado foram preservados para a
  retirada controlada da subetapa 18-D.6.

## Testes executados

1. Testes direcionados da API e do quadro legado: 7 aprovados.
2. Regressão Python completa: 505 aprovados.
3. Regressão JavaScript: 36 aprovados.
4. Regressão em Chrome/Playwright: 19 aprovados.
5. Busca textual no código ativo: nenhuma implementação provisória restante;
   apenas relatórios históricos e testes que confirmam sua ausência.

## Resultado

Subetapa aprovada tecnicamente. O screener oficial continua sendo o funil em
três níveis, e a auditoria futura permanece separada e ainda sem implementação.
