# Teste da etapa 34.3 — Validação final de Distribuições

Data: 14/11/2026.

## Ambiente

- aplicação local real em `http://127.0.0.1:5050`;
- Chrome controlado pelo Playwright;
- 3.069 resultados cadastrados;
- armazenamento local isolado no contexto do navegador de teste.

## Fluxo validado

1. abertura da página Distribuições;
2. carregamento dos dez gráficos;
3. presença de dez limites inferiores e dez superiores verdes;
4. abertura da configuração das faixas;
5. escolha do método percentual com margens 10% e 20%;
6. cálculo da prévia dos dez parâmetros;
7. salvamento do estudo no navegador;
8. recarga da página e recuperação do método e das margens;
9. confirmação pela API de que o Screener permaneceu inativo;
10. abertura direta do tópico Distribuições na Ajuda e conferência das
    explicações e exemplos.

## Resultados

- `distribuicoes_local_real.spec.mjs`: 1 teste integrado aprovado;
- `npm run test:frontend`: 164 testes aprovados, nenhuma falha;
- nenhuma escrita no PostgreSQL;
- nenhuma ativação ou execução do Screener.
