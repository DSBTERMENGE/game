# Evidência — Etapa 33.1

Data: 14/11/2026

## Problema corrigido

Ao desenhar somente a mancha Dezenas, o resumo lateral continuava apresentando
informações da última camada visualizada. Isso ocorria porque o código somente
substituía o conteúdo quando Média espacial, CG1, CG2 ou Quadrantes produziam um
novo resumo.

## Resultado

- somente Dezenas passa a exibir “Ocorrências das dezenas”;
- qualquer resumo anterior é removido;
- nenhuma frequência individual foi apresentada ainda;
- os resumos das outras camadas continuam inalterados quando elas estão
  marcadas.

## Testes

- 29 testes direcionados do Painel aprovados;
- conferência no servidor real com 3.069 resultados aprovada;
- 157 testes do frontend aprovados.
