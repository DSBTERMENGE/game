# Evidência — subetapa 22.17.6.5

Data: 02/11/2026

## Objetivo

Validar no navegador as ajudas contextuais dos três gráficos de frequência e
liberá-las para análise do usuário antes da documentação definitiva.

## Cenários confirmados

- O botão de ajuda de **Evolução dos intervalos** abre o texto correspondente.
- O botão de ajuda de **Curva de distribuição** abre o texto correspondente.
- O botão de ajuda de **Ocorrências em ordem crescente** abre o texto
  correspondente.
- As três ajudas reutilizam o mesmo formulário modal.
- Fechar a ajuda devolve o foco ao botão que a abriu.
- Fechar por `Esc` uma ajuda aberta sobre um gráfico auxiliar mantém o gráfico
  e seu modal abertos.
- Alternar entre as ajudas não deixa conteúdo residual da ajuda anterior.
- A abertura e o fechamento da ajuda não alteram os filtros, a consulta nem o
  gráfico exibido.
- O comportamento foi coberto nas larguras normal e estreita já exercitadas
  pela suíte de navegador.

## Testes executados

```text
npx playwright test frontend/tests/browser/frequencias.spec.mjs
10 passed

npm run test:frontend
79 passed, 0 failed

npm run test:browser
34 passed
```

## Resultado

Subetapa aprovada. As três ajudas estão liberadas para leitura e avaliação do
usuário. A subetapa 22.17.6.6, relativa à documentação definitiva, permanece
pendente de autorização e da aprovação dos textos pelo usuário.
