# Contrato de detecção e exclusão do screener

## 1. Princípio central

Detectar um padrão e excluir uma combinação são operações diferentes.

- O **detector** responde somente se a combinação pertence ao padrão.
- A **política** consulta a evidência histórica e decide o que aconteceria.
- O **modo de execução** determina se essa decisão apenas informa ou realmente
  interrompe a combinação no funil.

Uma ocorrência rara não se transforma automaticamente em regra de exclusão.
Cada detector, operador e tolerância exige autorização explícita.

## 2. Contrato do detector

O detector recebe exatamente seis dezenas distintas, inteiras, entre 01 e 60.
A ordem recebida não altera a resposta. Ele devolve exclusivamente um booleano:

- `true`: a combinação possui o padrão;
- `false`: a combinação não possui o padrão.

O detector deve ser puro: não consulta banco, não grava dados, não usa semente
aleatória e não depende do nome editável do cadastro. Sua ligação estável é o
código `PD_NNN`.

Entrada malformada deve produzir erro explícito, nunca `false`, pois `false`
poderia esconder defeito nos dados.

## 3. Base histórica e denominador

O percentual histórico de um padrão é:

```text
percentual = 100 × resultados em que o detector retornou true
                 / resultados históricos válidos avaliados
```

O denominador é a quantidade total de resultados válidos persistidos e
efetivamente submetidos à mesma versão do detector. Não pode ser uma seleção de
datas, a amostra de 5.000 combinações nem somente os resultados que possuem
algum padrão. No inventário de 2026-10-27, o denominador observado foi 3.069.

Antes da primeira ativação, o Item 15.6 deve recalcular e reconciliar o
detector com todos os resultados. Uma alteração futura no detector ou no
histórico invalida a reconciliação anterior até novo cálculo.

## 4. Precisão e arredondamento

A comparação usa a razão completa entre inteiros, sem arredondar previamente.
Para exibição, o percentual terá seis casas decimais com arredondamento
`ROUND_HALF_UP`. O valor exibido não substitui o valor exato da decisão.

Exemplo: 92 ocorrências em 3.069 resultados representam aproximadamente
2,997719%. Se uma tolerância de 3% vier a ser aprovada, a comparação exata
considerará esse valor menor que 3%, sem depender do texto arredondado.

## 5. Operador proposto

Para uma futura política de baixa ocorrência, o operador contratual é inclusivo:

```text
detector encontrou o padrão
E percentual_histórico <= tolerância_aprovada
```

`Menor ou igual` significa que um percentual exatamente igual à tolerância
também atende à política. Este contrato define a semântica do operador, mas não
aprova o valor de 3%, nenhum padrão e nenhuma exclusão.

Quando o detector retornar `false`, a combinação passa por esse critério,
independentemente do percentual histórico do padrão.

## 6. Modos da política

- **Inativo:** o detector não é chamado e a combinação passa.
- **Sombra:** a decisão hipotética e sua justificativa são contabilizadas, mas
  a combinação não é removida.
- **Ativo:** uma decisão de reprovação interrompe a combinação no funil. Esse
  modo depende de autorização posterior e individual.

O caminho obrigatório é `inativo -> sombra -> ativo`. Não existe transição
automática baseada apenas nos dados.

## 7. Dados ausentes, insuficientes ou inconsistentes

A política falha de forma conservadora: ela **não exclui** e informa o motivo
quando ocorrer qualquer uma destas situações:

- detector inexistente ou com erro;
- total histórico igual a zero;
- quantidade de ocorrências ausente, negativa ou maior que o total;
- estatística calculada com outra versão do detector;
- histórico alterado depois da reconciliação;
- tolerância ausente, fora de 0% a 100% ou não aprovada;
- divergência entre estatística recalculada e persistida.

Zero ocorrências não significa automaticamente dado insuficiente. Ele pode ser
uma evidência válida somente quando todos os resultados foram avaliados pela
mesma versão reconciliada do detector.

Intervalo, intervalo médio e desvio-padrão dos intervalos descrevem a ocorrência
do padrão, mas não participam da política percentual sem regra própria. Mediana
dos seis resultados pertence à categoria separada de critérios estatísticos.
Medidas como área e centro de gravidade pertencem aos critérios gráficos.

## 8. Justificativa obrigatória da decisão

Cada avaliação deve informar no mínimo:

- código do padrão e modo da política;
- combinação avaliada e resposta do detector;
- ocorrências, denominador e percentual exato/exibido;
- operador e tolerância configurada;
- versão ou identificação da reconciliação histórica;
- decisão (`passou`, `marcaria em sombra`, `reprovou` ou `não avaliável`);
- motivo legível da decisão.

O quadro do ensaio continuará atribuindo uma exclusão somente ao primeiro
critério ativo que reprovar a combinação.

## 9. Limites deste contrato

Este documento não escolhe o piloto, não corrige detectores, não recalcula o
histórico, não define tolerância e não ativa filtros. Critérios estatísticos e
geométricos terão contratos específicos quando forem estudados.
