# Evidência da subetapa 23.8 — combinações de seis dezenas

## Resultado

A subetapa foi concluída com um serviço independente para prévia, geração,
exportação e persistência autorizada de jogos de seis dezenas.

## Contratos verificados

- `C(60,6) = 50.063.860` é calculado sem materializar o universo.
- As dezenas são validadas, normalizadas e não podem se repetir.
- As combinações são únicas e geradas em ordem lexicográfica determinística.
- A geração usa iterador e não carrega todos os jogos antecipadamente.
- Gravação e exportação exigem autorização explícita.
- Operações com 10.000 jogos ou mais exigem confirmação adicional de volume.
- A divisão arbitrária em lotes de cobertura continua adiada conforme o plano.

## Persistência

A migração `022_criar_jogos_selecao_dezenas.sql` criou:

- `lotes_jogos_selecao`, ligado por chave estrangeira ao alvo da pesquisa;
- `jogos_selecao_dezenas`, ligado ao lote, com ordem determinística e seis
  dezenas estritamente crescentes.

Como o alvo pertence a uma execução e a execução pertence à configuração, o
lote mantém a rastreabilidade até configuração, pesquisa e concurso-alvo sem
duplicar essas chaves.

## Ensaios executados

Os testes dirigidos aprovaram **13 testes** de matemática, proteção operacional
e DDL. O ensaio em database efêmero confirmou:

1. tentativa sem autorização recusada e sem registros;
2. seleção real de sete dezenas vinculada ao alvo;
3. persistência autorizada de exatamente sete jogos;
4. sete jogos distintos, numerados de 1 a 7;
5. remoção do database efêmero ao final.

A regressão completa aprovou **662 testes**.

## Banco local

A migração 022 foi aplicada ao database local `games`. Nenhum lote ou jogo foi
gerado no banco persistente durante a subetapa.
