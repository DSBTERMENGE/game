# Teste da etapa 25.8

## Ambiente

- aplicação real em `http://127.0.0.1:5050`;
- PostgreSQL real com 3.069 concursos;
- configurações salvas 2 (`k=1`, `j=0`) e 3 (`k=0,5`, `j=0`);
- navegador Chrome controlado pelo Playwright, sem respostas simuladas.

## Fluxos validados

1. Configuração 3, período completo de 500 a 3.069:
   - prévia exibiu 2.570 concursos;
   - relatório, resumo, sete classes e os dois gráficos foram exibidos;
   - identificação da configuração e período ficaram visíveis;
   - a interface informou que nenhum resultado foi gravado.
2. Configuração 2, início personalizado em 2.500:
   - o final foi resolvido automaticamente como 3.069;
   - a prévia exibiu 570 concursos;
   - o relatório foi concluído e exibiu o período correto.
3. Validação direta da API:
   - período completo com 2.570 pontos;
   - cancelamento e descarte confirmados;
   - cardinalidades do banco permaneceram inalteradas.
4. Auditoria posterior:
   - nenhuma execução, alvo ou avaliação do tipo `BACKTEST` no banco;
   - nenhuma rota persistente antiga disponível.

## Resultado

Os dois testes reais de navegador foram aprovados. O backtest em memória atende
ao fluxo aprovado e não grava resultados derivados. Nenhum ajuste funcional foi
necessário; o contrato documental foi atualizado para registrar que o concurso
final é sempre o último cadastrado e não é escolhido pelo usuário.
