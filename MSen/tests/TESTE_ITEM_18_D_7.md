# Teste da subetapa 18-D.7

Data: 2026-10-29

## Objetivo

Executar a regressão final, reconciliar a documentação e encerrar a consolidação
do Screener sem iniciar backtest nem a implementação futura da auditoria.

## Estado final documentado

- página pública única: `/screener.html`;
- execução pública única: `POST /api/screener/quadro`;
- interface única em três níveis: estatística, geometria e padrões;
- limite protegido: 5.000 combinações;
- processamento integral de 50.063.860 combinações: bloqueado;
- primeiro funil: preservado apenas para comparação matemática interna;
- protótipo fictício e interfaces antigas: retirados;
- auditoria: página vazia reservada à Etapa 20;
- backtest: expressamente adiado.

## Ensaio real confirmado no Chrome

- combinações analisadas: 5.000;
- excluídas pelo funil oficial: 4.586;
- aprovadas pelo funil oficial: 414;
- saldos após as famílias: 2.001, 423 e 414;
- fechamento contábil: correto;
- aprovação do primeiro funil na mesma amostra: 4.409, exibida somente como
  comparação interna.

## Regressão

- Python: 503 testes aprovados;
- JavaScript: 32 testes aprovados;
- Chrome/Playwright: 18 testes aprovados;
- integração: 5 testes, sendo 3 aprovados e 2 ignorados porque dependem do
  PostgreSQL local;
- `git diff --check`: sem erro de formatação;
- busca operacional: nenhuma página, rota ou script antigo ainda referenciado
  pelo produto.

## Resultado

Subetapa 18-D.7 e Etapa 18-D aprovadas tecnicamente. Nenhum commit ou push foi
feito, pois essas ações exigem autorização específica do usuário.
