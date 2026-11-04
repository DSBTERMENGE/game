# Evidência da subetapa 23.9 — API da Seleção de dezenas

## Resultado

A API foi registrada no servidor Flask existente com base
`/api/selecao-dezenas`. Nenhuma porta ou servidor adicional foi criado.

## Contratos validados

- listagem e preservação de configurações assinadas;
- prévia sem iniciar processamento ou gravação;
- backtest assíncrono com progresso, consulta e cancelamento;
- bloqueio de execução simultânea;
- resumo, detalhes e comparação de pesquisas;
- atualização e consulta das previsões futuras;
- identificação do alvo no detalhe;
- prévia combinatória e persistência autorizada de jogos;
- rejeição de campos, tipos e períodos inválidos;
- erro de banco controlado sem divulgação de detalhes internos.

## Testes dirigidos

O módulo `tests.test_api_selecao_dezenas` aprovou **12 testes** HTTP e do
gerenciador assíncrono.

## Integração em banco efêmero

O ensaio `tests.validar_api_selecao_dezenas` carregou os concursos 1 a 505 e
validou pelo cliente Flask:

1. criação e listagem de configuração;
2. prévia dos concursos 500 a 505;
3. execução assíncrona e consulta de backtest com seis alvos;
4. resumo e detalhe persistidos;
5. previsão futura para o concurso 506;
6. prévia de `C(7,6) = 7`;
7. recusa da gravação não autorizada;
8. gravação autorizada dos sete jogos;
9. remoção do database efêmero.

## Regressão

A suíte completa aprovou **674 testes**.
