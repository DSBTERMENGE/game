# Contrato da Gestão do desenvolvimento

Data do contrato: 11/11/2026.

## Objetivo

Registrar problemas, decisões de aprimoramento e novas funcionalidades do Game
em uma fonte consultável pelo usuário e pela IA. O cadastro complementa o plano:

- a manutenção registra o que precisa ser entendido ou realizado;
- o plano divide e autoriza a execução;
- as evidências demonstram o que foi concluído.

O título da página será `Gestão do desenvolvimento`. O nome físico principal
proposto permanece `manutencao_sistema`.

## Campos do registro

| Campo | Finalidade |
|---|---|
| `id_manutencao` | identificador técnico não exibido como numeração funcional |
| `tipo` | natureza do registro |
| `titulo` | identificação humana e campo principal de pesquisa |
| `data_registro` | data escolhida pelo usuário no calendário |
| `descricao` | explicação atual e completa |
| `criterios_conclusao` | condições observáveis para considerar o trabalho concluído |
| `status_trabalho` | situação do desenvolvimento |
| `status_publicacao` | situação no PythonAnywhere |
| `pagina_origem` | página relacionada, quando houver |
| `referencia` | arquivos, etapa, erro ou outra localização útil |
| `observacao_publicacao` | detalhe de publicação ou falha |
| `versao_registro` | controle de concorrência |
| datas operacionais | criação, atualização, início, conclusão, publicação e arquivamento |

Título, data e descrição são obrigatórios. Página e referência são opcionais, pois um
registro pode tratar de uma ideia geral ou de funcionalidade ainda inexistente.

## Tipos

- `ERRO`: exceção ou falha objetiva;
- `MAU_FUNCIONAMENTO`: execução possível com comportamento incorreto ou confuso;
- `MODIFICACAO`: aprimoramento de algo existente;
- `NOVA_FUNCIONALIDADE`: capacidade ainda inexistente;
- `NAO_CLASSIFICADO`: registro ainda não analisado.

## Estados do trabalho

- `NAO_INICIADO`;
- `EM_ANALISE`;
- `EM_ANDAMENTO`;
- `AGUARDANDO_VALIDACAO`;
- `CONCLUIDO`;
- `CANCELADO`.

Conclusão exige critérios preenchidos ou uma justificativa registrada. Reabrir
um concluído o devolve a `EM_ANDAMENTO`. Arquivamento é uma condição separada e
não apaga o status alcançado.

## Estados da publicação

- `NAO_APLICAVEL`;
- `AGUARDANDO_PUBLICACAO`;
- `PUBLICADO`;
- `FALHA_PUBLICACAO`.

`PUBLICADO` exige data de publicação. `FALHA_PUBLICACAO` exige observação.
Concluir localmente não significa publicar no PythonAnywhere.

## Pesquisa e filtros

A consulta padrão mostra não arquivados, com pesquisa parcial pelo título. A
página permite filtrar por:

- tipo;
- status do trabalho;
- status da publicação;
- arquivamento.

A ordem é fixa pela criação do registro, sem seletor de ordenação.

## Histórico e trabalho da IA

Alterações relevantes de texto, data, estado, publicação, arquivamento e
reabertura deverão produzir eventos de histórico. O histórico não será editado
pela interface comum.

Ao retomar uma sessão relacionada, a IA poderá consultar registros ativos,
ler descrição, critérios e referências, e propor melhoria do texto. Alterações
continuam dependendo da autorização aplicável ao trabalho em andamento.

O cadastro não autoriza automaticamente implementar o conteúdo registrado.

## Primeiro registro previsto

A reorganização da página Screener poderá ser cadastrada posteriormente como
`MODIFICACAO`, com a descrição distinguindo preparação histórica, avaliação com
amostra de 5.000 e aplicação integral do gabarito. A etapa 27.1 não cria esse
registro nem qualquer tabela.
