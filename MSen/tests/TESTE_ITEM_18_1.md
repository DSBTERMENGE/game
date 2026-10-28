# Teste da subetapa 18.1 — contrato extensível do funil

## Exemplo manual

O conjunto controlado contém oito combinações:

- estatística exclui duas e entrega seis;
- geometria exclui uma e entrega cinco;
- padrões exclui duas e entrega três;
- três combinações são aprovadas.

Fechamento: `8 = 2 + 1 + 2 + 3`.

## Verificações

- percentuais sobre total inicial e saldo recebido;
- interrupção na primeira exclusão;
- cada exclusão contabilizada uma única vez;
- inclusão dinâmica de um novo filtro geométrico;
- ordenação por metadados, sem códigos fixos;
- motivo obrigatório e evidências imutáveis;
- rejeição de código duplicado e decisão divergente;
- fechamento correto também com entrada vazia.

## Resultado

- 7 testes específicos aprovados.
- 453 testes Python de regressão aprovados.
- Foram emitidos somente avisos preexistentes sobre três arquivos do screener
  não fechados por um teste; nenhum teste falhou.
- O funil atual, banco, API e interface permaneceram sem integração nova.
