# API — Seleção de dezenas

Base: `/api/selecao-dezenas`. Todas as respostas de erro usam:

```json
{"erro": {"codigo": "CODIGO_ESTAVEL", "mensagem": "Mensagem pública"}}
```

Falhas de conexão retornam HTTP 503 sem incluir host, credenciais ou mensagem
interna do PostgreSQL.

## Configurações e prévia

- `GET /configuracoes`: lista configurações preservadas.
- `POST /configuracoes`: cria ou reutiliza configuração de mesma assinatura.
- `POST /previa`: apresenta os dados analíticos da configuração, a base
  disponível, o período do backtest e o concurso-alvo atual, sem iniciar
  cálculo nem gravação.

A configuração possui exatamente `nome`, `fator_k`, `fator_j`,
`modo_quantidade`, `quantidade_dezenas` e `versao_calculo`. O concurso-alvo
não é configurável: ele é sempre o concurso imediatamente posterior ao último
resultado cadastrado no banco.

## Backtest

O backtest produz um relatório do Backtest e não persiste execução, pontos ou
resumo no banco:

- `POST /backtests/previa`: recebe
  `id_configuracao_selecao` e `concurso_inicial`; valida a configuração salva e
  resolve o final para o último concurso cadastrado, sem iniciar cálculo ou
  gravação;
- `POST /backtests`: inicia o cálculo assíncrono e retorna HTTP 202
  com identificador UUID do cálculo;
- `GET /backtests/{id}`: informa estado, etapa, progresso, duração,
  erro público e, quando concluído, pontos e resumo;
- `POST /backtests/{id}/cancelamento`: solicita cancelamento em
  ponto seguro;
- `DELETE /backtests/{id}`: descarta da memória um relatório já
  concluído, cancelado ou falho.

O corpo de início aceita somente o identificador de uma configuração salva e o
concurso inicial. Não aceita concurso final, objeto de configuração nem cria
configuração implicitamente. O servidor consulta novamente o último concurso
cadastrado ao iniciar e o adota como final do estudo.

Somente o relatório do Backtest mais recente permanece no processo. Iniciar
outro descarta o anterior; a operação `DELETE` permite liberação explícita. O
servidor não grava execução, progresso, pontos ou resumo no PostgreSQL. Toda a
leitura do motor ocorre em transação `READ ONLY`.

O resultado concluído contém:

- `pontos`: concurso, quantidade de dezenas e quantidade de acertos;
- `resumo`: testes efetuados, classes exclusivas de 0 a 6, mínimo, máximo,
  médias e concursos nas classes 4, 5 ou 6;
- `persistido: false`.

Uma tentativa simultânea recebe HTTP 409 e
`BACKTEST_EM_ANDAMENTO`. Depois do descarte ou da substituição, a
consulta recebe HTTP 404 e `BACKTEST_NAO_ENCONTRADO`.

## Previsão do próximo concurso

- `POST /previsoes`: recebe somente `id_configuracao_selecao` de uma
  configuração salva e disponível, confere a previsão pendente quando seu
  resultado já está cadastrado e emite exatamente uma previsão para
  `último concurso + 1`. Não cria configuração implicitamente.
- `GET /previsoes/{id}/detalhes`: retorna o alvo da execução, inclusive
  `id_alvo_selecao`, necessário para operações de jogos.

## Jogos de seis dezenas

- `GET /alvos/{id}/jogos/previa`: retorna dezenas e `C(N,6)` sem materializar.
- `POST /alvos/{id}/jogos`: persiste jogos somente quando
  `autorizar_persistencia=true`. Volumes elevados também exigem
  `confirmar_volume_elevado=true`.

Os jogos permanecem vinculados ao alvo, à execução e à configuração de origem.

Essas rotas pertencem ao fluxo inicial de materialização bruta. A página não
chama mais o `POST /jogos`. O novo processo usará `formacoes_jogos_selecao` e
`jogos_finais_selecao`, mas suas rotas somente serão publicadas quando geração,
Screener, classificação e confirmação estiverem integrados e validados.

## Fluxo da página

1. `GET /configuracoes` preenche configurações preservadas.
2. `POST /previa` alimenta o diálogo de conferência sem criar tarefa.
3. Após confirmação, `POST /backtests` inicia o cálculo.
4. A página consulta `GET /backtests/{id}` até estado terminal e
   pode solicitar cancelamento seguro.
5. O relatório e os gráficos são montados somente após a conclusão.
6. `POST /previsoes` confere a pendência coberta por resultado novo e emite a
   previsão para o próximo concurso da série cadastrada.
7. Jogos exigem primeiro `/jogos/previa` e depois autorização explícita.

Uma execução simultânea recebe HTTP 409. O cliente acompanha o cálculo pelo
identificador do cálculo retornado.

## Interpretação

`PENDENTE` significa previsão congelada aguardando resultado. `AVALIADO`
significa seleção conferida contra o resultado real. `NAO_AVALIAVEL` indica
ausência ou incompatibilidade de base e fica fora das taxas de acerto.

As classes zero a seis são exclusivas. A API não escolhe automaticamente uma
configuração vencedora: acertos, quantidade média de dezenas e custo
combinatório precisam ser examinados juntos.
