# Evidência da etapa 27.5

Data: 11/11/2026.

## Entregas

- botão `Registrar ideia ou problema` instalado pela navegação comum;
- modal disponível nas páginas que usam a barra principal;
- campos tipo, título, descrição, prioridade e referência;
- página de origem preenchida automaticamente;
- conferência e confirmação anteriores ao POST;
- chave de idempotência por solicitação;
- cancelamento explícito sem gravação;
- retorno ao formulário quando a API rejeita o registro;
- acesso à página completa de Gestão do desenvolvimento.

O botão não cria registros ao abrir, preencher, conferir ou cancelar.

## Validação

- 6 testes unitários específicos aprovados;
- 110 testes unitários do frontend aprovados no total;
- teste Playwright confirmou zero POST no cancelamento e na conferência;
- o mesmo teste confirmou exatamente um POST após a confirmação;
- a API foi interceptada no navegador e o banco real permaneceu com zero
  registros de manutenção.

## Validação

- 6 testes unitários específicos aprovados;
- 110 testes unitários do frontend aprovados no total;
- teste de navegador confirma zero POST ao cancelar ou apenas conferir e um
  único POST depois de `Confirmar e registrar`.
