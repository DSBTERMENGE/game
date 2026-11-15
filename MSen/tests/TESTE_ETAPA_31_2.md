# Evidência da etapa 31.2 — Linha Poligonal e Polígono 1

Data: 12/11/2026

## Alteração

- a Linha Poligonal é uma camada aberta com cinco segmentos;
- o Polígono 1 é uma camada fechada completa com seis arestas;
- cada camada possui opção própria na configuração visual;
- cada camada possui cor própria;
- ambas podem ser apresentadas juntas ou separadamente;
- as preferências antigas de Linha e Fechamento são convertidas para a nova
  configuração visual ao serem carregadas.

## Validação

- 126 testes unitários do frontend aprovados;
- três fluxos Playwright aprovados: desenho inicial, persistência da aparência e
  alternância independente das duas camadas;
- APIs, cálculos Python e banco de dados não foram alterados.
