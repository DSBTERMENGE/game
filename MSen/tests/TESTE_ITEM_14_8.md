# Evidência do Item 14.8 — revisão do processamento integral

Data: 2026-10-27.

## Medição controlada

Foram processadas somente 5.000 combinações:

- geração aleatória: 0,0126 s;
- iteração lexicográfica: 0,000322 s;
- geometria completa: 2,8978 s, cerca de 1.725 combinações/s.

A extrapolação linear para 50.063.860 projetou 3,22 s para apenas iterar e
29.015 s (aproximadamente 8,1 h) para calcular geometria em um processo. Essa
projeção não inclui filtros históricos/estatísticos, serialização, banco, tela
ou contenção e não é promessa de tempo final.

## Armazenamento estimado das combinações

- Tuplas e referências Python: aproximadamente 4,81 GB (4,48 GiB).
- CSV compacto `01,02,03,04,05,06`: aproximadamente 901 MB (859 MiB).
- Formato binário teórico de seis bytes: aproximadamente 300 MB (286 MiB).

Esses valores não incluem resultados geométricos, metadados, índices nem
sobrecarga do PostgreSQL. Portanto, a coleção integral não deve ser mantida em
memória nem gravada sem um projeto específico de persistência.

## Decisão

O caminho recomendado é sequencial, particionado e em fluxo, descartando cada
combinação reprovada e mantendo contadores/pontos de retomada por partição. A
paralelização deve ser avaliada somente depois que filtros reais forem aprovados
e medidos, porque a ordem do funil alterará fortemente o custo.

O limite de 5.000 permanece obrigatório. Nenhuma execução integral foi feita ou
autorizada.

## Testes

- 3 testes específicos da extrapolação aprovados.
- Regressão Python completa: 297 testes aprovados.
- Banco de dados e PythonAnywhere permaneceram inalterados.
