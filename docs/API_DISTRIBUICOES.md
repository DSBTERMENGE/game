# API das distribuições

`GET /api/perfis/distribuicoes`

A rota é somente leitura e retorna os dez parâmetros catalogados, a janela
histórica, histogramas, curva normal de referência, médias, desvios e faixas.
Ela nunca ativa o screener.

## Parâmetros opcionais

- `numero_ap_antes_de`: corte exclusivo por concurso;
- `data_antes_de`: corte exclusivo por data no formato `AAAA-MM-DD`;
- `classes`: 1 a 50, padrão 10;
- `metodo_faixa`: `desvio_padrao` ou `percentual_media`;
- `margem_inferior` e `margem_superior`: números não negativos.

Os dois cortes são mutuamente exclusivos. A janela vazia é recusada. Se alguma
linha não possuir análise geométrica, a API responde `GEOMETRIA_INCOMPLETA`, em
vez de comparar amostras estatísticas e geométricas de tamanhos diferentes.

A curva normal é identificada como `REFERENCIA_VISUAL`. O histograma representa
os dados reais. Em séries de desvio zero, a curva normal fica indisponível.

Soma e média são declaradas dependentes (`média = soma / 6`) e não devem ser
tratadas como filtros independentes.
