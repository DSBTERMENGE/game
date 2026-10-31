# Evidência da subetapa 22.16.4

## Ajuda e documentação

- A ajuda de `frequencias.html` explica abertura da página ampliada,
  preservação dos filtros, escala automática e ampliação 10×.
- `graficos-frequencias.html` possui ajuda própria, cobrindo filtros, gráficos,
  unidades, escalas, recorte e retorno.
- Foram atualizados `docs/funcionamento.md`, `docs/arquitetura.md`,
  `docs/API_FREQUENCIAS.md`, `notas/decisoes.md` e
  `notas/funcionalidades.md`.

## Regressão final

- Python: 629 testes aprovados em 16,470 segundos.
- JavaScript: 57 testes aprovados.
- Google Chrome: 34 fluxos aprovados.
- Os fluxos cobrem ida e volta, filtros preservados, dois gráficos, dimensões,
  ocorrências reais, escala automática, ampliação 10×, aviso de recorte,
  restauração, ajuda e telas de 1.280 px e 520 px. Na página auxiliar estreita,
  o gráfico permanece rolável sem alargar o documento.

## Observação sobre o ambiente Python

A primeira tentativa executou o interpretador global sem incluir `MSen/src` e
produziu erros de importação `No module named 'msen'`. Nenhum teste funcional
chegou a falhar. A suíte foi repetida a partir de `MSen`, incluindo `src` e a
raiz do pacote no caminho de importação, e todos os 629 testes passaram.

## Banco de dados

Nenhuma carga histórica, migração ou escrita no banco foi executada.
