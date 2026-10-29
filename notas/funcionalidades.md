# Funcionalidades planejadas

Este arquivo descreve o que o produto deverá fazer. Os itens ainda precisam de
aprovação e priorização antes da implementação.

## Dados e importação

- [ ] Importar a planilha de resultados sem modificar o arquivo original.
- [x] Reconhecer as colunas `Concurso`, `Data` e `bola 1` a `bola 6`.
- [x] Validar concurso, data e dezenas antes de gravar.
- [x] Atualizar o histórico sem duplicar concursos já existentes.
- [x] Informar quantos registros foram importados, ignorados ou rejeitados.
- [x] Permitir substituir a planilha por uma versão atualizada e importar apenas
  os concursos ainda inexistentes.
- [x] Comparar linhas existentes e separar resultados iguais de divergências,
  sem atualizar silenciosamente dados históricos.

## Consultas

- [ ] Consultar um concurso pelo número.
- [ ] Listar concursos por intervalo de números ou datas.
- [ ] Pesquisar concursos que contenham uma ou mais dezenas.
- [ ] Exibir as dezenas na ordem original e em ordem crescente.

## Análises

- [ ] Calcular e armazenar a soma dos seis resultados de cada linha.
- [ ] Calcular e armazenar a média aritmética dos seis resultados de cada linha.
- [ ] Calcular e armazenar a mediana dos seis resultados de cada linha.
- [ ] Calcular e armazenar o desvio-padrão dos resultados em relação à média.
- [ ] Calcular a frequência de cada número de 01 a 60 em todo o histórico ou em
  um período.
- [ ] Calcular os intervalos entre as ocorrências de cada número de 01 a 60.
- [ ] Calcular o intervalo médio de ocorrência de cada número.
- [ ] Calcular o desvio-padrão dos intervalos de ocorrência de cada número.
- [ ] Comparar uma combinação de seis dezenas com concursos anteriores.
- [ ] Apresentar estatísticas descritivas sem tratá-las como previsão de sorteio.

## Representações gráficas

- [ ] Plotar um resultado colocando um círculo verde-claro sobre cada número
  ocorrido, preservando a leitura do número abaixo da marca.
- [ ] Plotar a média do resultado na mesma escala visual de 01 a 60.
- [ ] Calcular a média das coordenadas dos seis pontos sem arredondamento,
  admitindo posições decimais como `(2; 4,33)`.
- [ ] Usar o centro de `01` como `(0; 0)` e o centro de `60` como `(9; 5)`.
- [ ] Converter coordenadas lógicas em pixels usando as distâncias reais entre
  os centros das células.
- [ ] Animar os resultados individualmente em intervalos de 0,5 segundo,
  limpando as marcas antes de desenhar o próximo.
- [x] Plotar todos os resultados como pequenos círculos, inicialmente com cerca
  de 3 mm de diâmetro, dentro do retângulo correspondente a cada número.
- [x] Organizar os pequenos círculos lado a lado e, ao atingir o limite do
  retângulo, retornar ao início da linha seguinte.
- [x] Formar uma mancha visual cuja densidade represente a quantidade de
  ocorrências de cada número.
- [x] No modo mancha, preservar as marcas anteriores ao avançar pelos resultados.
- [x] Criar uma representação equivalente para a distribuição das médias.

## Interface e operação

- [x] Criar painel com seleção do Excel, navegação, voo, mancha e limpeza.
- [x] Permitir configurar o tempo de cada resultado entre 0,1 e 30 segundos.
- [x] Implementar no frontend a marcação das seis dezenas e da média espacial.
- [x] Implementar controles de resultado anterior, seguinte e seleção direta.
- [x] Implementar os modos visuais voo dos pássaros e mancha acumulada.
- [ ] Implementar na API a leitura do Excel, os cálculos e o armazenamento.
- [ ] Integrar a interface HTML/JavaScript à API Python.
- [ ] Exibir filtros, resultados e mensagens de validação.
- [ ] Funcionar com PostgreSQL local e no PythonAnywhere.
- [ ] Executar somente migrações pendentes, preservando os dados existentes.
- [ ] Permitir diagnóstico da versão do aplicativo e do esquema do banco.

## Organização de padrões concluída

- [x] Organizar padrões em grupos conceituais relacionados.
- [x] Cadastrar grupos em grade CRUD compacta.
- [x] Vincular obrigatoriamente cada padrão a um grupo.
- [x] Filtrar e transferir padrões entre grupos.
- [x] Proteger estatísticas calculadas contra edição manual.
- [x] Separar Painel e Cadastros em páginas com menu horizontal e Voltar.
- [x] Conter rolagens vertical e horizontal dentro das grades.

## Screener de padrões históricos concluído

- [x] Calcular e armazenar quantidade, total de sorteios e percentual histórico
  para todos os padrões, inclusive os que tenham zero ocorrências.
- [x] Não criar classe ou registro para resultados que não correspondam a um
  dos padrões estudados.
- [x] Selecionar somente padrões com função Python aprovada e incidência
  histórica estritamente menor que o limite configurado.
- [x] Aplicar os padrões selecionados em funil, interrompendo a combinação na
  primeira exclusão e contabilizando o filtro responsável.
- [x] Exibir somente grupos e padrões realmente selecionados e executados, com
  incidência, limite, avaliações, exclusões e saldo.
- [x] Mostrar código e nome legível do padrão e do grupo no relatório.
- [x] Executar amostra protegida e reproduzível de 5.000 combinações, mantendo
  bloqueado o processamento integral.
- [x] Reunir estatística, geometria e padrões em um único funil oficial de três
  níveis, acessível por `/screener.html`.
- [x] Expor uma única execução pública em `POST /api/screener/quadro` e retirar
  as telas antigas e o protótipo fictício.
- [x] Preservar internamente o primeiro funil somente para a comparação exibida
  no relatório oficial.

## Auditoria do screener e dos backtests

- [ ] Selecionar um sorteio histórico ou uma combinação experimental para
  auditoria.
- [ ] Mostrar as seis dezenas, origem, intervalo histórico, configuração e
  versões das funções usadas.
- [ ] Detalhar fórmulas, valores substituídos e resultados intermediários de
  cada critério estatístico.
- [ ] Permitir confirmar manualmente operações como a soma das seis dezenas.
- [ ] Detalhar coordenadas, segmentos, extensão, perímetro, áreas e centro de
  gravidade dos critérios geométricos.
- [ ] Mostrar ocorrências encontradas, subgrupo identificado e decisão de cada
  grupo de padrões.
- [ ] Exibir a ordem percorrida no funil e marcar os estágios posteriores como
  não avaliados quando houver exclusão anterior.
- [ ] Registrar resultado esperado, resultado obtido, conformidade, observação
  e revisor humano, IA ou teste automatizado.
- [ ] Disponibilizar visão resumida e abertura dos detalhes dos três níveis.
- [ ] Exportar futuramente a auditoria em JSON, CSV ou planilha.
- [ ] Garantir que o relatório seja reproduzível com os mesmos dados,
  configurações, versões e intervalo histórico.
- [ ] Mostrar no cadastro de grupos se existe função Python classificadora,
  sua versão e se os testes de integração foram aprovados.

## Fora do escopo inicial

- apostas automáticas;
- promessa de previsão de resultados aleatórios;
- alteração direta do banco pela interface;
- armazenamento de senhas no código ou no Git.
