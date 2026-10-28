# Teste da subetapa 17.4 — perfis geométricos

## Figuras controladas

Foram usadas três combinações já cobertas pelos cálculos geométricos reais:

- uma figura com uma região e área 36;
- uma figura com duas regiões e área 4,5;
- uma figura sem região, área zero e centro de gravidade inexistente.

## Casos automatizados

1. criação dos seis parâmetros na ordem estável do catálogo;
2. reconciliação de área e regiões com as funções geométricas reais;
3. centro ausente contabilizado sem substituição por zero;
4. zeros válidos participando dos perfis de área e regiões;
5. coleção vazia sem medidas inventadas;
6. rejeição de identificador repetido e centro incoerente;
7. rejeição de coleção ou item inválido.

## Resultado

- 7 testes específicos aprovados.
- 437 testes Python de regressão aprovados.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- Banco, API, interface e regras do screener permaneceram inalterados.
