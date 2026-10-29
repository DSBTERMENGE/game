# Teste da subetapa 18-C.5 — consulta parametrizada dos padrões raros

Data: 2026-10-29

## Objetivo

Selecionar, antes da execução do screener, somente os padrões que:

- possuem detector Python aprovado no catálogo oficial;
- pertencem à fotografia histórica esperada;
- possuem estatística completa e atualizada;
- têm `percentual_ocorrencia < limite_percentual`.

A igualdade não elimina: um padrão cujo percentual seja exatamente igual ao
limite fica fora da seleção.

## Implementação

- `RepositorioPadroes.listar_raros` executa consulta SQL parametrizada.
- A consulta restringe os códigos aos detectores aprovados pelo catálogo.
- Uma verificação anterior à seleção recusa fotografia incompleta, percentual
  nulo ou denominador diferente do esperado.
- `selecionar_padroes_raros` oferece o contrato de serviço e devolve também o
  limite normalizado, o denominador e o operador `<`.
- O limite aceita valores entre 0 e 100 e é normalizado para seis casas
  decimais.

## Validação no banco local

Fotografia histórica: 3.069 sorteios.

| Limite | Padrões selecionados |
|---:|---|
| 0% | nenhum |
| 3% | PD_002, PD_003, PD_005 e PD_006 |
| 10% | PD_002, PD_003, PD_005, PD_006 e PD_009 |
| 100% | PD_001 a PD_009 |

Validação da fronteira do PD_003, cujo percentual armazenado é 0,162920%:

- limite 0,162920%: PD_003 não foi selecionado;
- limite 0,162921%: PD_003 foi selecionado.

Ao informar denominador esperado de 3.068, o serviço recusou a consulta com o
código funcional `FOTOGRAFIA_INCOMPATIVEL`.

## Testes automatizados

- 8 testes direcionados do serviço e repositório: aprovados.
- 496 testes Python da regressão completa: aprovados.
- O `ResourceWarning` já existente em testes que abrem arquivos do frontend não
  causou falhas.

## Resultado

Subetapa 18-C.5 aprovada tecnicamente. A seleção é feita pelo percentual
armazenado, usa comparação estrita `<`, não cria classe complementar e impede o
uso silencioso de uma fotografia histórica incompatível.
