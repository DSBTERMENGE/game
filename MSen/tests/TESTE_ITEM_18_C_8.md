# Teste da subetapa 18-C.8 — relatório detalhado por padrão

Data: 2026-10-29

## Objetivo

Manter o resumo compacto do screener e permitir a expansão da família de
padrões até o nível de cada `PD_nnn` selecionado pela consulta, reconciliando
padrão, grupo, família e total geral.

## Conteúdo apresentado

Para cada padrão retornado pela consulta de raridade são exibidos:

- código e nome;
- quantidade, denominador e percentual de ocorrência histórica;
- operador e limite da execução;
- estado `APLICADO_RARO`;
- avaliações;
- correspondências;
- exclusões;
- saldo após o filtro.

Um grupo ou padrão ausente não foi selecionado pela consulta de raridade e não
foi aplicado. Não se cria linha artificial para ele no relatório do screener.

## Organização visual

- As três famílias continuam recolhidas inicialmente.
- Dentro da família de padrões existe um bloco recolhível para cada grupo
  retornado pela consulta.
- As tabelas extensas usam rolagem horizontal interna, sem alargar a página.
- A própria presença da linha confirma que o padrão foi aplicado.

## Execução real

Com limite de 10%, foram apresentados somente PD_002, PD_003, PD_005, PD_006 e
PD_009. A mesma consulta já forneceu a identificação do padrão, seu grupo e as
informações históricas necessárias para localizar o detector correto.

Fechamentos:

| Grupo | Entrada | Exclusões | Saldo |
|---|---:|---:|---:|
| PG_001 | 423 | 3 | 420 |
| PG_002 | 420 | 3 | 417 |
| PG_003 | 417 | 3 | 414 |
| Família de padrões | 423 | 9 | 414 |

O total geral permaneceu 5.000 = 4.586 excluídas + 414 aprovadas.

## Testes

- 2 testes Python específicos do detalhamento e adulteração contábil;
- 505 testes Python aprovados;
- 35 testes JavaScript aprovados;
- 18 fluxos completos no Google Chrome aprovados;
- execução real somente leitura aprovada;
- banco de dados não alterado.

## Resultado

Subetapa 18-C.8 aprovada tecnicamente.
