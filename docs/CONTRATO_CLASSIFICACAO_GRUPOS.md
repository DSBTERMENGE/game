# Contrato de classificação dos resultados por grupo

> Correção vigente desde 29/10/2026: as propostas históricas abaixo que tratam
> a diferença até 100% como uma classe estão revogadas. Somente ocorrências de
> padrões reais são persistidas. Um resultado que não atenda aos padrões
> estudados não gera linha nem percentual próprio. O estado homônimo usado em
> `avaliacoes_validacao` é outro contexto: resultado válido de um classificador
> sem subgrupo identificado.
> Cada percentual usa como denominador todos os sorteios da amostra.

Data: 28/10/2026
Subetapa: 16.1
Estado: contrato conceitual aprovado após os esclarecimentos; nenhum DDL criado.

## Finalidade

Para cada resultado real e grupo classificável, aplicar todos os padrões
cadastrados e registrar o padrão identificado ou o estado
`SEM_CORRESPONDENCIA`. Essa classificação permitirá obter as frequências reais,
descobrir o que é comum ou raro e fundamentar decisões futuras do screener.

## Nome proposto

`resultado_classificacao_padrao`

O nome descreve uma classificação de um resultado em um padrão pertencente a
um grupo. Não será usado para armazenar combinações experimentais do screener.

## Cardinalidade proposta

- Um resultado terá exatamente um registro de classificação em cada grupo
  classificável.
- O registro conterá um padrão identificado ou `SEM_CORRESPONDENCIA`.
- Um grupo poderá possuir qualquer quantidade de subgrupos.
- Os padrões usados como subdivisões do grupo deverão ser mutuamente exclusivos,
  mas não precisarão cobrir todos os resultados.
- A futura restrição lógica será única por `id_resultado` e `id_grupo`.
- O padrão registrado deverá pertencer ao grupo registrado.

Estrutura conceitual, ainda sem tipos SQL aprovados:

- `id_classificacao`;
- `id_resultado`;
- `id_grupo`;
- `id_padrao`, nulo somente quando o estado for `SEM_CORRESPONDENCIA`;
- `estado_classificacao`, inicialmente `PADRAO_IDENTIFICADO` ou
  `SEM_CORRESPONDENCIA`;
- `versao_calculo`;
- `calculado_em`.

## Quando um grupo pode ser classificado

Um grupo criado pelo usuário não será automaticamente considerado
classificável. Para participar da classificação, deverá possuir:

1. função classificadora Python aprovada;
2. regras claras para impedir ou resolver correspondências múltiplas;
3. versão de cálculo identificável;
4. casos de aceitação aprovados.

Grupo sem classificador continuará disponível para cadastro e estudo, mas não
produzirá linhas silenciosamente incompletas na tabela de classificação.

## Regra dos três grupos atuais

Os detectores existentes já são exclusivos dentro de cada grupo porque usam o
maior valor encontrado. A função classificadora do grupo deverá calcular esse
valor uma única vez e mapear o resultado para uma classe, em vez de tratar os
três detectores como decisões independentes.

### PG_001 — Dezenas sequenciais

Métrica: comprimento do maior bloco de dezenas consecutivas após ordenação.

- maior bloco = 1: `SEM_CORRESPONDENCIA`;
- maior bloco = 2: `PD_001`;
- maior bloco = 3: `PD_002`;
- maior bloco entre 4 e 6: `PD_003`.

### PG_002 — Dezenas na mesma coluna

Métrica: comprimento da maior sequência vertical na mesma coluna e em linhas
imediatamente subjacentes.

- maior sequência vertical = 1: `SEM_CORRESPONDENCIA`;
- maior sequência vertical = 2: `PD_004`;
- maior sequência vertical = 3: `PD_005`;
- maior sequência vertical entre 4 e 6: `PD_006`.

Dezenas na mesma coluna mas separadas por linhas não formam a sequência deste
grupo e, se nenhum padrão corresponder, resultam em `SEM_CORRESPONDENCIA`.

### PG_003 — Dezenas na mesma linha

Métrica: maior quantidade de dezenas em uma mesma linha da matriz.

- maior ocupação = 1: `SEM_CORRESPONDENCIA`;
- maior ocupação = 2: `PD_007`;
- maior ocupação = 3: `PD_008`;
- maior ocupação entre 4 e 6: `PD_009`.

## Resultado que pertence a classes diferentes em grupos diferentes

Isso não é ambiguidade. Um resultado terá uma linha de classificação por grupo.
Por exemplo, ele poderá ser `PD_001` em PG_001, `PD_006` em PG_002 e `PD_008`
em PG_003 ao mesmo tempo.

Ambiguidade somente existiria se o mesmo resultado pudesse receber dois
subgrupos dentro do mesmo grupo. Os três grupos atuais evitam isso usando o
maior bloco ou a maior ocupação.

## Sem correspondência não representa erro nem padrão

`SEM_CORRESPONDENCIA` será registrado quando todas as funções do grupo forem
executadas corretamente e nenhuma retornar correspondência. Ele não receberá
código `PD`, não será cadastrado como subgrupo e não será tratado como padrão.

Falha de cálculo, padrão sem função, dado inválido ou versão desconhecida não
serão registrados como `SEM_CORRESPONDENCIA`. Esses casos deverão interromper
ou marcar erro explícito no relatório de processamento.

## Denominador oficial dos percentuais

Proposta principal:

- usar todos os resultados históricos válidos existentes no intervalo;
- calcular cada frequência aplicando as funções aos resultados do intervalo;
- calcular `SEM_CORRESPONDENCIA` como total elegível menos a soma das
  classificações nos padrões do grupo;
- exigir que padrões mais `SEM_CORRESPONDENCIA` sejam iguais ao total elegível;
- consequentemente, os percentuais do grupo deverão somar 100%, salvo pequenas
  diferenças de arredondamento.

As frequências observadas dirão quais padrões são comuns ou raros. A raridade
não será presumida pelo nome, código ou posição do padrão.

Como informação secundária, a interface poderá mostrar o percentual apenas
entre resultados com algum padrão. Esse percentual deverá ser identificado
como `percentual entre correspondências`, nunca como o percentual principal.

## Uso das frequências pelo screener

- Um padrão frequente, como duas dezenas sequenciais, normalmente não será bom
  candidato a exclusão por raridade.
- Padrões com baixa frequência, como três ou mais dezenas sequenciais, poderão
  ser estudados para exclusão.
- A baixa frequência não ativa o filtro automaticamente; a decisão continuará
  configurada e aprovada pelo usuário.
- Resultado `SEM_CORRESPONDENCIA` passará pelo grupo, pois não caiu em nenhum
  teste selecionado para exclusão.
- O screener contabilizará a exclusão somente quando uma função de padrão
  configurada para excluir retornar correspondência.

## Seleção de padrões raros por limite configurável

As frequências serão calculadas antes de processar as combinações. Uma
configuração da execução poderá definir um limite de raridade.

Exemplo experimental:

- limite de raridade: 10%;
- operador: estritamente menor que `<`;
- frequência menor que 10%: padrão selecionado para exclusão;
- frequência igual ou maior que 10%: padrão preservado.

O valor de 10% é apenas hipótese inicial e não ficará fixo no código. Cada
execução deverá registrar:

- limite percentual;
- operador usado;
- total de resultados do espaço amostral;
- primeiro e último concurso ou datas do intervalo;
- frequência calculada de cada padrão;
- padrões que ficaram abaixo do limite;
- versão das funções classificadoras.

A lista de padrões excludentes será calculada uma única vez no início da
execução. Isso evita recalcular frequências para cada combinação e garante que
todo o lote utilize a mesma referência.

O estado `SEM_CORRESPONDENCIA` não é padrão, não participa da seleção por
limite e passa pelo grupo.

Antes do processamento, a interface deverá mostrar a lista produzida pela
regra para conferência do usuário. A confirmação não altera as frequências;
apenas autoriza o uso daquela fotografia histórica e configuração no funil.

## Intervalo histórico

O perfil completo atual poderá usar todos os resultados persistidos. Toda
consulta deverá aceitar futuramente um concurso ou data de corte.

No backtest, o denominador e as classificações de referência usarão somente
resultados anteriores ao resultado avaliado.

## Regras de desempate

Não há desempate entre subgrupos nos três grupos atuais:

- PG_001 usa o comprimento do maior bloco horizontal;
- PG_002 usa o comprimento do maior bloco vertical subjacente;
- PG_003 usa a maior ocupação de linha.

Se dois blocos diferentes tiverem o mesmo tamanho máximo, a classe permanece a
mesma, pois o grupo classifica pelo tamanho máximo e não pela posição do bloco.
As evidências de auditoria poderão listar todos os blocos máximos encontrados.

## Invariantes que a implementação deverá testar

- exatamente seis dezenas inteiras, distintas e entre 01 e 60;
- exatamente um registro por resultado e grupo classificável;
- no máximo um padrão identificado dentro do grupo;
- padrão sempre pertencente ao grupo informado;
- `SEM_CORRESPONDENCIA` somente após todas as funções executarem sem erro;
- soma das contagens dos padrões mais `SEM_CORRESPONDENCIA` igual ao total;
- percentuais principais somando 100% por grupo;
- mesma entrada e mesma versão produzindo a mesma classificação;
- nenhuma informação futura usada quando houver corte histórico.

## Decisões consolidadas

1. Nome: `resultado_classificacao_padrao`.
2. Um registro por resultado e grupo, com padrão ou `SEM_CORRESPONDENCIA`.
3. Não criar automaticamente PD_010, PD_011 e PD_012.
4. Usar todos os resultados válidos como denominador e mostrar a diferença até
   100% como `SEM_CORRESPONDENCIA`.
5. Fazer `SEM_CORRESPONDENCIA` passar pelo grupo no screener.
6. Calcular as frequências aplicando as funções ao histórico disponível.
7. Selecionar padrões raros por limite percentual configurável; 10% permanece
   apenas como exemplo experimental inicial.
8. Usar operador estrito `<`: frequência igual ao limite não será excluída.
9. Calcular a lista excludente uma vez por execução e guardar sua fotografia.

Com essas decisões, a subetapa 16.2 poderá preparar o DDL mediante autorização.
