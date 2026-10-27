# Evidência do Item 13.10 — distribuições e fechamento

Data: 2026-10-27.

## Histórico analisado

- 3.069 resultados e 3.069 análises geométricas.
- Regiões: 1 = 729; 2 = 1.221; 3 = 872; 4 = 247.
- Extensão aberta: mín. 6,414214; máx. 39,615072; média 18,398295;
  mediana 17,875351; desvio-padrão populacional 5,225258.
- Perímetro: mín. 10,019765; máx. 49,463929; média 24,202505;
  mediana 23,638749; desvio-padrão 5,627935.
- Área: mín. 1,500000; máx. 29,500000; média 9,577784;
  mediana 8,722222; desvio-padrão 4,639607.
- CG X: mín. 0,777778; máx. 7,943978; média 4,509214;
  mediana 4,489521; desvio-padrão 1,106985.
- CG Y: mín. 0,333333; máx. 4,693447; média 2,500198;
  mediana 2,500000; desvio-padrão 0,700265.

O script somente de leitura `analisar_distribuicoes_geometricas.py` gerou os
valores diretamente no PostgreSQL local.

## Desempenho

A resposta integral anterior tinha 3.807.101 bytes e a primeira carga visual
medida no Item 13.9 levou cerca de 8,1 s. A lista usada pelo painel passou a
solicitar `incluir_geometria=0`; três medições reais resultaram em 1.093.806
bytes e 525, 496 e 497 ms. A geometria do concurso 1 foi obtida separadamente
em 51 ms e 903 bytes. Isso reduz o corpo inicial em aproximadamente 71,3%.

## Regressão

- 254 testes Python: aprovados.
- 24 testes JavaScript: aprovados.
- 9 fluxos isolados no Google Chrome: aprovados.
- 3 fluxos Chrome/PostgreSQL: aprovados.
- Validação visual no banco real: concursos 1 e 2 aprovados.
- Bancos temporários remanescentes: nenhum.

O PostgreSQL local permaneceu migrado até `007`. PythonAnywhere não foi
alterado. A Etapa 13 está pronta para commit de segurança, se autorizado.
