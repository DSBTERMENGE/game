# Etapa 31.1 — Inventário e especificação do Painel

Data: 12/11/2026

## Elementos existentes que serão reutilizados

- a grade cartesiana possui 10 colunas e 6 linhas, com coordenadas lógicas
  `x=0..9` e `y=0..5`;
- a Linha Poligonal já liga as seis dezenas em ordem crescente por cinco
  segmentos;
- o fechamento entre a última e a primeira dezena já existe;
- o conjunto Linha Poligonal mais fechamento constitui o Polígono 1;
- o motor atual divide os cruzamentos do Polígono 1 em regiões, soma suas áreas
  e calcula o centro de gravidade consolidado, denominado CG1 nesta etapa;
- área, CG1, extensão aberta, perímetro e quantidade de regiões já possuem
  cálculo Python e consulta sob demanda pela API;
- média aritmética, desvio-padrão das dezenas e coordenadas da Média espacial já
  são calculados e armazenados em `resultados`;
- o Painel já possui seleção de concurso, anterior, próximo, voo, pausa, tempo,
  mancha, aparência e limpeza;
- o voo já percorre os concursos sem alterar dados;
- a mancha atual é montada no navegador sobre todos os resultados carregados e
  acumula ocorrências das dezenas e pontos da Média espacial;
- o histórico inicial é carregado sem geometria e a geometria do concurso
  visível é consultada sob demanda.

## Nomenclatura aprovada

- **Média aritmética:** média numérica das seis dezenas;
- **Média espacial:** ponto obtido pelas médias das coordenadas X e Y;
- **Linha Poligonal:** cinco segmentos ligando as dezenas em ordem crescente;
- **Polígono 1:** Linha Poligonal acrescida da aresta de fechamento;
- **CG1:** centro de gravidade das regiões do Polígono 1;
- **Polígono 2:** circuito fechado sem cruzamentos que passa uma vez por todas
  as seis dezenas e procura a maior área;
- **CG2:** centro de gravidade do Polígono 2.

## Condições de aceitação do Polígono 2

O resultado final deverá possuir simultaneamente:

1. as seis dezenas como vértices do circuito;
2. exatamente seis arestas;
3. exatamente duas arestas incidentes em cada dezena;
4. um único circuito fechado e conectado;
5. nenhuma interseção entre arestas não vizinhas;
6. maior área entre os circuitos válidos.

A primeira implementação experimental seguirá a técnica proposta de remover
ligações internas e apresentará os casos em que restarem ligações excedentes.
A regra de eliminação desses excedentes será aprovada depois da observação de
casos reais. A enumeração exata dos circuitos válidos será usada como mecanismo
de conferência do maior resultado, sem antecipar uma regra visual não aprovada.

## Quadrantes

- eixo vertical entre as colunas das dezenas 05 e 06;
- eixo horizontal entre as linhas 21–30 e 31–40;
- Q1 superior direito, seguindo Q2, Q3 e Q4 no sentido anti-horário;
- o código possui quatro posições na ordem Q1, Q2, Q3 e Q4; `3021` representa
  três dezenas em Q1, nenhuma em Q2, duas em Q3 e uma em Q4;
- o código será tratado como categoria, com contagem e percentual históricos;
- média e desvio-padrão serão calculados separadamente para as quantidades de
  Q1, Q2, Q3 e Q4, sem calcular média aritmética do código completo.

## Organização aprovada para o Painel

1. **Dados e navegação:** Excel, concurso, anterior, próximo, aparência e
   limpeza;
2. **Voo dos pássaros:** tempo, iniciar/pausar e camadas Média espacial, Linha
   Poligonal, Polígono 1 e Polígono 2;
3. **Manchas:** comando e camadas Média espacial, CG1 e CG2, combináveis;
4. **Ocorrência das dezenas:** gradiente e visualização separada ou conjunta
   com as manchas;
5. **Quadrantes:** eixos, código, frequência, resumo e mancha própria.

Os quadros usarão contorno com cantos arredondados. Marcar várias opções deverá
produzir sobreposição; desmarcar uma opção retirará somente sua camada.

## Dados e persistência

- nenhuma coluna ou tabela foi criada nesta subetapa;
- o banco atual já atende Média aritmética, Média espacial e Polígono 1/CG1;
- Polígono 2/CG2 e quadrantes ainda não possuem persistência própria;
- a estratégia de migração e atualização incremental será definida somente
  depois de os cálculos correspondentes estarem especificados e testados;
- a Ajuda do Painel será atualizada apenas depois de a interface ser aprovada.
