# API de perfis históricos dos grupos de padrões

## Endpoint

`GET /api/grupos-padroes/<grupo_cod>/perfil`

Na versão atual, somente `PG_001` possui classificador implementado.

## Parâmetros opcionais

- `limite_raridade`: percentual entre 0 e 100; padrão `10`;
- `numero_ap_ate`: último concurso incluído na amostra;
- `data_ate`: última data incluída, no formato `AAAA-MM-DD`.

Os cortes são inclusivos. `numero_ap_ate` e `data_ate` não podem ser enviados
juntos. Para um backtest do concurso N, o chamador deverá informar como corte o
último concurso que podia ser conhecido antes de N.

## Resposta

A resposta contém:

- identificação do grupo;
- total da amostra, total classificado e sem correspondência;
- primeiro e último concurso e data efetivamente incluídos;
- limite, operador estrito `<` e padrões apenas indicados como raros;
- versões das classificações usadas;
- contagem, percentuais, intervalo médio, desvio-padrão e indicação de raridade
  de cada padrão;
- classe `SEM_CORRESPONDENCIA`, sem estatística de intervalo e nunca rara.

`raridade.ativa_no_screener` permanece sempre `false` nesta etapa.

## Segurança

O endpoint é somente leitura. Perfis com corte são calculados em memória e não
substituem as estatísticas globais do catálogo. Erros de configuração ou banco
não expõem SQL, credenciais ou detalhes internos.
