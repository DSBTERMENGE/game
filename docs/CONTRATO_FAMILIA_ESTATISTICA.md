# Contrato da família estatística

A família estatística inicial do novo funil possui três filtros ordenados:

1. `EST_SOMA_MEDIA` — soma e média como uma única decisão;
2. `EST_MEDIANA` — mediana das seis dezenas;
3. `EST_DESVIO_PADRAO` — desvio-padrão populacional das seis dezenas.

Os cálculos são realizados pelas mesmas funções do domínio usadas para salvar e
auditar resultados. Cada faixa é um intervalo fechado: valores exatamente nos
limites são aceitos; somente valores abaixo ou acima são excluídos.

## Soma e média

Como `média = soma / 6`, as duas medidas não são filtros independentes. A soma é
comparada com sua faixa e a média, juntamente com os limites equivalentes
divididos por seis, é registrada como evidência. Há uma única decisão e no máximo
uma exclusão contabilizada.

## Contabilidade

Os filtros obedecem ao funil: uma exclusão interrompe a combinação. Mediana só
recebe o saldo aprovado por soma/média, e desvio só recebe o saldo aprovado pelos
dois filtros anteriores. Assim, o subtotal estatístico contém exclusões líquidas.
