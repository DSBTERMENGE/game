# Evidência — subetapa 23.2-A

Data: 03/11/2026

## Objetivo

Corrigir o contrato da quantidade de dezenas para impedir complementação com
dezenas que não atenderam à faixa.

## Regras consolidadas

- quantidade integrada à configuração;
- modo `MAX` para todas as aprovadas;
- modo `FIXA` para no máximo `N` aprovadas;
- ranking usado somente quando há mais de `N` aprovadas;
- retorno de todas as aprovadas quando sua quantidade é inferior a `N`;
- nenhuma complementação com dezenas fora da faixa;
- log com o máximo atingido pelo critério;
- relatório com quantidade configurada, aprovada e retornada.

## Casos

- `MAX` com 15 aprovadas retorna 15;
- `FIXA=8` com 15 aprovadas retorna as 8 mais bem classificadas;
- `FIXA=8` com 5 aprovadas retorna 5 e registra que o máximo possível foi 5.

## Resultado

Subetapa 23.2-A concluída no nível contratual. Nenhuma tabela, função, API ou
página foi criada.
