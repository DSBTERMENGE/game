# Evidência — subetapa 22.16.11.6

Data: 2026-11-02

## Documentação atualizada

- Ajuda modal de `graficos-frequencias.html`.
- `docs/funcionamento.md`.
- `docs/API_FREQUENCIAS.md`.
- `notas/decisoes.md`.
- `notas/funcionalidades.md`.

O conteúdo documenta patamares entre ocorrências consecutivas, transição
tracejada, média e desvio cumulativos, recorte no concurso 500, limiar visual de
8 pixels e consulta dos marcadores por mouse, teclado ou clique. A decisão
anterior de pontos individuais, mínimo e máximo foi registrada como
substituída.

## Testes

```text
npm run test:frontend
60 testes aprovados

npm run test:browser
34 testes aprovados no Chrome
```

A busca por descrições antigas (`círculo vermelho`, `pontos vermelhos`, curvas
de mínimo/média/máximo e mudanças de mínimo/máximo) não encontrou ocorrências
nos documentos vigentes nem na ajuda.
