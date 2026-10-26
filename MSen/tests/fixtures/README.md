# Planilhas controladas do Item 3.1

Estas planilhas pequenas são entradas exclusivas dos testes futuros de importação.
Nenhum teste deve escrever nelas nem utilizar como destino a fonte real em
`MSen/dados/fontes`.

- `resultados_validos.xlsx`: duas linhas válidas;
- `sem_cabecalho.xlsx`: nomes de colunas não reconhecidos;
- `linha_invalida.xlsx`: uma linha válida e outra com data inválida, dezena
  repetida e dezena fora do intervalo de 1 a 60;
- `linhas_repetidas.xlsx`: duas linhas idênticas do mesmo concurso;
- `base_existente.xlsx`: estado inicial para testes de comparação;
- `linha_existente_alterada.xlsx`: um concurso igual, um alterado e um novo em
  relação à base existente.

O script `criar_planilhas.py` recria somente esses arquivos nesta pasta. Ele não
lê nem modifica a planilha fonte do projeto.
