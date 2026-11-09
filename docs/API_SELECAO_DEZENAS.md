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

## Backtests

- `POST /backtests`: inicia tarefa assíncrona.
- `GET /execucoes/{id}`: consulta estado, progresso, duração e resultado da
  tarefa.
- `POST /execucoes/{id}/cancelamento`: solicita cancelamento seguro.
- `GET /backtests/{id}/resumo`: consulta consolidado e classes de 0 a 6.
- `GET /backtests/{id}/detalhes`: consulta os concursos e dezenas congeladas.
- `POST /backtests/comparacao`: compara duas ou mais execuções persistidas.

A API impede dois backtests simultâneos no mesmo processo. O motor preserva no
banco o progresso por alvo, permitindo retomada por nova solicitação idempotente.

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

## Fluxo da página

1. `GET /configuracoes` preenche configurações preservadas.
2. `POST /previa` alimenta o diálogo de conferência sem criar tarefa.
3. Após confirmação, `POST /backtests` cria a execução assíncrona.
4. A página consulta `GET /execucoes/{id}` até estado terminal e pode solicitar
   cancelamento seguro.
5. Resumo e detalhes são carregados somente após conclusão.
6. `POST /previsoes` confere a pendência coberta por resultado novo e emite a
   previsão para o próximo concurso da série cadastrada.
7. Jogos exigem primeiro `/jogos/previa` e depois autorização explícita.

Uma execução simultânea recebe HTTP 409 e código `EXECUCAO_EM_ANDAMENTO`. O
cliente não deve repetir automaticamente uma operação de gravação após resposta
incerta; deve consultar o estado pelo identificador retornado.

## Interpretação

`PENDENTE` significa previsão congelada aguardando resultado. `AVALIADO`
significa seleção conferida contra o resultado real. `NAO_AVALIAVEL` indica
ausência ou incompatibilidade de base e fica fora das taxas de acerto.

As classes zero a seis são exclusivas. A API não escolhe automaticamente uma
configuração vencedora: acertos, quantidade média de dezenas e custo
combinatório precisam ser examinados juntos.
