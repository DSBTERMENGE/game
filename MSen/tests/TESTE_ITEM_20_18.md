# Evidência — subetapa 20.18

Data: 2026-10-30.

## Fechamento da Validação e auditoria

O modal de andamento passou a distinguir o término do processamento do
resultado da validação. Ao atingir 100%, apresenta total, aprovadas, reprovadas
e pendentes e informa explicitamente se a validação foi aprovada.

O cabeçalho da própria página também representa somente esse diagnóstico. Ele
exibe `Validação e auditoria aprovada` quando não há `N` nem pendências, sem
reutilizar no formulário o estado operacional posterior do Screener.

Quando existe `N` ou pendência, o modal informa que o processamento terminou,
mas a validação não foi aprovada, e orienta o uso do filtro `Situação`. Falha
técnica continua sendo apresentada como interrupção, sem ser confundida com
reprovação matemática.

## Bloqueio visível no Screener

Antes de habilitar sua execução, a página do Screener consulta o relatório de
Validação e auditoria. Critério novo, alterado, pendente ou reprovado mantém o
botão desabilitado e exibe somente a mensagem acordada:

> Screener bloqueado: há pendências na Validação e auditoria dos critérios de seleção.

A verificação trata exclusivamente da homologação dos critérios. Condições
operacionais posteriores do Screener permanecem separadas.

## Preservação

Nenhuma fórmula, referência esperada, valor calculado, assinatura ou aprovação
persistida foi alterada por esta subetapa.

## Regressão

- Python: 572 testes aprovados.
- Node: 37 testes aprovados.
- Chromium: 24 fluxos aprovados.
- Cenários específicos: tudo aprovado, reprovação, pendência, critério novo,
  critério alterado, falha técnica e bloqueio da execução.

Nenhum commit, push ou publicação externa foi executado.
