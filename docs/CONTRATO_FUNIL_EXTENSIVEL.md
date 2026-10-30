# Contrato extensível do funil oficial

> O contrato estrutural continua válido. Afirmações intermediárias de que
> filtros reais ainda não estavam conectados são históricas; consulte
> `docs/funcionamento.md` para o estado executável.

O Screener oficial é composto por famílias ordenadas. Cada família contém qualquer
quantidade de filtros também ordenados. As famílias iniciais são:

1. valores estatísticos;
2. análise geométrica;
3. grupos de padrões históricos.

Essa relação não é fixa. Novos filtros e novas famílias podem ser registrados
por definição, sem criar colunas específicas no executor ou no quadro.

## Entrada e saída de um filtro

Todo filtro recebe uma combinação de seis dezenas e devolve:

- código estável do filtro;
- decisão de aprovação ou exclusão;
- motivo preenchido;
- evidências usadas na decisão.

As evidências são copiadas e congeladas. Isso impede que sejam alteradas depois
da decisão e prepara a futura auditoria.

## Ordem e interrupção

Famílias e filtros possuem ordens positivas e exclusivas no respectivo nível.
O executor ordena as definições recebidas. Quando um filtro exclui uma
combinação:

- a exclusão é atribuída somente a ele;
- nenhum filtro posterior avalia aquela combinação;
- o laço segue para a combinação seguinte.

## Contabilidade

Cada filtro registra avaliações, exclusões líquidas, saldo e dois percentuais:

- percentual sobre o total inicial;
- percentual sobre o saldo recebido pelo filtro.

Cada família registra entrada, soma de suas exclusões líquidas, saldo e os dois
percentuais equivalentes. O relatório exige:

`total inicial = total excluído + total aprovado`

## Extensibilidade

O quadro percorre as famílias e filtros do relatório, nunca uma
lista fixa de nomes. Códigos duplicados, ordens ambíguas, decisões sem motivo ou
decisões atribuídas ao filtro errado são rejeitados.

Na subetapa original, o contrato foi validado com avaliadores controlados. A
conexão posterior dos filtros reais está descrita em `docs/funcionamento.md`.
