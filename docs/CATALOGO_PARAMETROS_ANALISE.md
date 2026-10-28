# Catálogo dos parâmetros de análise

Este catálogo define os valores já calculados pelo sistema que poderão formar
os perfis históricos da Etapa 17. Ele não ativa critérios de exclusão.

As dezenas de cada resultado são distintas, variam de 01 a 60 e, nos cálculos
geométricos, são ligadas em ordem crescente sobre a grade de 10 colunas por 6
linhas. O centro da dezena 01 é `(0, 0)` e o da 60 é `(9, 5)`.

| Código | Parâmetro | Fórmula ou regra | Unidade | Precisão armazenada | Fonte no banco | Função Python |
|---|---|---|---|---|---|---|
| `EST_SOMA` | Soma | `S = x1 + ... + x6` | unidade de dezena | inteiro exato (`SMALLINT`) | `resultados.soma_res` | `calcular_soma` |
| `EST_MEDIA` | Média aritmética | `M = S / 6` | dezena | 6 casas (`NUMERIC(10,6)`) | `resultados.media_aritmetica_res` | `calcular_media_aritmetica` |
| `EST_MEDIANA` | Mediana | média entre a 3ª e a 4ª dezenas ordenadas | dezena | 1 casa (`NUMERIC(4,1)`) | `resultados.mediana_res` | `calcular_mediana` |
| `EST_DESVIO_PADRAO` | Desvio-padrão populacional | `sqrt(sum((xi - M)^2) / 6)` | dezena | 6 casas (`NUMERIC(10,6)`) | `resultados.desvio_padrao_media` | `calcular_desvio_padrao_media` |
| `GEO_EXTENSAO_ABERTA` | Extensão aberta | soma euclidiana dos 5 segmentos sucessivos | unidade lógica da grade | 12 casas (`NUMERIC(20,12)`) | `analise_geometrica_resultado.extensao_aberta` | `calcular_extensao_aberta` |
| `GEO_PERIMETRO_FECHADO` | Perímetro fechado | extensão aberta mais o segmento da última à primeira dezena | unidade lógica da grade | 12 casas (`NUMERIC(20,12)`) | `analise_geometrica_resultado.perimetro_fechado` | `calcular_perimetro_fechado` |
| `GEO_AREA_TOTAL` | Área total | soma das áreas positivas das faces limitadas formadas após dividir os cruzamentos | unidade lógica quadrada | 12 casas (`NUMERIC(20,12)`) | `analise_geometrica_resultado.area_total` | `calcular_area_e_centro_gravidade().area_total` |
| `GEO_QUANTIDADE_REGIOES` | Quantidade de regiões | número de faces limitadas identificadas | contagem | inteiro exato (`SMALLINT`) | `analise_geometrica_resultado.quantidade_regioes` | `len(calcular_area_e_centro_gravidade().regioes)` |
| `GEO_CENTRO_GRAVIDADE_X` | Centro de gravidade X | média dos centroides das faces ponderada pelas áreas | coordenada lógica horizontal | 12 casas (`NUMERIC(20,12)`) ou nulo | `analise_geometrica_resultado.centro_gravidade_x` | `calcular_area_e_centro_gravidade().centro_gravidade.x` |
| `GEO_CENTRO_GRAVIDADE_Y` | Centro de gravidade Y | média dos centroides das faces ponderada pelas áreas | coordenada lógica vertical | 12 casas (`NUMERIC(20,12)`) ou nulo | `analise_geometrica_resultado.centro_gravidade_y` | `calcular_area_e_centro_gravidade().centro_gravidade.y` |

## Regras de interpretação

- `EST_SOMA` e `EST_MEDIA` são linearmente equivalentes porque todo resultado
  possui exatamente seis dezenas: `M = S / 6`. Podem ser mostradas juntas,
  mas não devem contar como dois filtros estatísticos independentes.
- Apesar do nome histórico da coluna `desvio_padrao_media`, seu conteúdo é o
  desvio-padrão populacional **das seis dezenas do resultado**. Ele não é o
  desvio-padrão de uma série de médias históricas. O perfil histórico da Etapa
  17 calculará separadamente a média e o desvio-padrão de cada parâmetro.
- Extensão e perímetro são relacionados, mas não equivalentes: o perímetro
  acrescenta o segmento de fechamento.
- Área e quantidade de regiões consideram todas as faces limitadas criadas
  pelos cruzamentos. Não se usa a área assinada bruta de um polígono que cruza
  a si próprio.
- Quando a área total é zero, não há centro de gravidade de área; por isso X e
  Y são ambos nulos.
- Uma curva normal futura será apenas referência visual. A distribuição real
  de cada parâmetro deve continuar visível e não será presumida normal.

## Limites desta subetapa

O catálogo apenas identifica fórmulas, unidades, precisão, colunas e funções
existentes. Não muda banco, API, interface nem as regras atuais do screener.
