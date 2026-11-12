# Contrato do motor de formação de jogos

## Finalidade

O motor recebe as dezenas de uma seleção registrada e encaminha todas as
combinações de seis, uma única vez, ao adaptador fornecido. Ele prepara a etapa
de integração com o Screener sem assumir regras de filtragem ou classificação.

## Entrada

- de 6 a 60 dezenas inteiras, distintas e entre 1 e 60;
- adaptador chamável que recebe uma combinação por vez;
- retorno opcional de progresso;
- consulta opcional de cancelamento;
- intervalo positivo de atualização do progresso.

## Processamento

- calcula previamente `C(N,6)`;
- usa `itertools.combinations` em ordem lexicográfica;
- não converte as combinações em lista ou tupla global;
- verifica o cancelamento antes de encaminhar a próxima combinação;
- informa progresso no início, nos intervalos definidos e no encerramento;
- converte falhas do adaptador em erro operacional identificado.

## Saída

O relatório contém estado `CONCLUIDA` ou `CANCELADA`, quantidade de dezenas,
total previsto, quantidade efetivamente encaminhada, percentual e duração.
Ele não contém as combinações.

## Limites desta etapa

- o adaptador real do Screener ainda não está conectado;
- não existe rota ou botão de execução;
- não existe tarefa em segundo plano;
- nenhuma combinação é persistida;
- classificação e seleção financeira permanecem para etapas posteriores.

## Segurança

O cancelamento ocorre entre combinações e não deixa lote parcial porque o motor
não grava dados. Uma execução com 26 dezenas encaminhou 230.230 combinações com
pico inferior a 2 MiB no teste automatizado. A seleção real de 16 dezenas
encaminhou 8.008 combinações sem alterar qualquer tabela.
