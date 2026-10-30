# Contrato do gerador e screener experimental

> Contrato histórico da fase experimental. O Screener oficial e sua trava de
> homologação estão descritos em `docs/funcionamento.md`.

## Finalidade desta fase

O screener receberá combinações de seis dezenas distintas, entre 01 e 60,
sempre em ordem crescente. A Etapa 14 começa com ensaios reproduzíveis de no
máximo 5.000 combinações. O processamento das 50.063.860 combinações não está
autorizado.

O arquivo versionado é `MSen/config/screener.toml`. Ajustes da máquina podem
ser colocados em `MSen/config/screener.local.toml`, ignorado pelo Git. O arquivo
local substitui apenas as chaves que declarar.

## Execução

- `modo`: `amostra` ou `integral`; o padrão é `amostra`.
- `semente`: inteiro não negativo que permitirá reproduzir o ensaio.
- `limite_combinacoes`: obrigatoriamente 5.000 nesta fase.
- `confirmacao_processamento_integral`: trava adicional para a futura execução
  integral. Seu valor atual é falso e alterá-lo não executa nada por si só.

As Etapas 14.2 e 14.3 implementarão os geradores. A configuração criada aqui
não inicia laços nem grava combinações.

O Item 14.2 implementou o gerador amostral em memória. Ele usa um gerador
pseudoaleatório isolado, descarta eventuais repetições e encerra ao reunir
exatamente 5.000 combinações. Não aplica filtros nem grava a amostra.

O Item 14.3 adicionou o iterador lexicográfico definitivo baseado em
`itertools.combinations`. No modo experimental, `islice` garante o encerramento
em 5.000 itens. Para devolver o iterador de 50.063.860 possibilidades, são
obrigatórias a confirmação booleana na configuração e a frase explícita
`PROCESSAR_50063860_COMBINACOES`. Mesmo confirmado, o iterador é preguiçoso.

## Ordem inicial do funil

1. Padrões históricos.
2. Medidas estatísticas.
3. Medidas geométricas.

Quando um filtro excluir uma combinação, o funil contabilizará a exclusão e
passará imediatamente para a próxima combinação. Essa execução será criada
somente nas etapas posteriores.

O Item 14.4 implementou essa estrutura. Cada critério possui um código único e
devolve uma decisão com aprovação/reprovação, o mesmo código e os valores que
embasaram a resposta. O relatório registra quantas combinações chegaram a cada
critério, quantas ele excluiu e o saldo resultante. Naquela fase, sem critérios,
todas as combinações passavam e os critérios reais estavam desativados.

O Item 14.5 separou os adaptadores de padrões históricos, medidas estatísticas
e medidas geométricas. Cada um repassa combinação e tolerâncias para sua futura
função e transforma a resposta em decisão padronizada. Um adaptador inativo
não chama a função; um ativo exige uma função que devolva o contrato correto.
Na etapa 14, as funções reais ainda não estavam conectadas; esse estado foi
substituído pelo funil oficial descrito em `docs/funcionamento.md`.

## Tolerâncias e segurança

Os valores iniciais de 3% para ocorrência de padrões e 20% para variação da
média registram os exemplos discutidos. Eles não são regras aprovadas. Todos os
critérios ficam obrigatoriamente desabilitados na 14.1, inclusive o geométrico,
que ainda não possui faixa definida.

A validação rejeita limite diferente de 5.000, ordem incompleta, percentuais
fora de 0 a 100 e qualquer critério habilitado prematuramente. As futuras
execuções deverão registrar configuração, semente, ordem, contadores e tempo.

O Item 14.6 implementou esse quadro. Além dos totais e das linhas dos filtros,
ele conserva o relatório do funil e os valores de configuração necessários para
reproduzir o ensaio. Sua serialização usa tipos simples e pode ser enviada por
uma futura API ou exibida em tabela sem recalcular o ensaio.

O Item 14.7 integrou configuração, gerador amostral, funil vazio e quadro. A
execução recebeu e aprovou 5.000 combinações e pode ser repetida pelo script
`MSen/tests/executar_ensaio_5000.py`. Enquanto nenhuma regra de exclusão estiver
aprovada, o orquestrador rejeita categorias ativas; assim, ainda não existe
comparação legítima entre ordens de filtros.

O Item 14.8 mediu a amostra e manteve o limite de 5.000. A geometria projetou
cerca de 8,1 horas para o universo em um processo, antes de outros filtros e
I/O; tuplas Python projetaram aproximadamente 4,81 GB somente para combinações.
A estratégia escolhida para um futuro processamento integral é sequencial,
particionada e em fluxo, com descarte imediato e pontos de retomada. Paralelismo
será reconsiderado depois da aprovação e medição dos filtros reais.
