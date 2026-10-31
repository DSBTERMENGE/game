# Funcionalidades vigentes e pendentes

Itens marcados foram confirmados por implementação e testes. Itens sem marca
continuam pendentes ou pertencem a ciclos posteriores.

## Dados e importação

- [x] Importar a planilha de resultados sem modificar o arquivo original.
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

- [x] Calcular e armazenar a soma dos seis resultados de cada linha.
- [x] Calcular e armazenar a média aritmética dos seis resultados de cada linha.
- [x] Calcular e armazenar a mediana dos seis resultados de cada linha.
- [x] Calcular e armazenar o desvio-padrão populacional dos resultados.
- [x] Calcular a frequência de cada número de 01 a 60 em todo o histórico ou em
  um período.
- [x] Calcular os intervalos entre as ocorrências de cada número de 01 a 60.
- [x] Calcular o intervalo médio de ocorrência de cada número.
- [x] Calcular o desvio-padrão dos intervalos de ocorrência de cada número.
- [ ] Comparar uma combinação de seis dezenas com concursos anteriores.
- [x] Apresentar estatísticas descritivas sem tratá-las como promessa de previsão
  de sorteio.

## Representações gráficas

- [x] Plotar um resultado colocando um círculo verde-claro sobre cada número
  ocorrido, preservando a leitura do número abaixo da marca.
- [x] Plotar a média do resultado na mesma escala visual de 01 a 60.
- [x] Calcular a média das coordenadas dos seis pontos sem arredondamento,
  admitindo posições decimais como `(2; 4,33)`.
- [x] Usar o centro de `01` como `(0; 0)` e o centro de `60` como `(9; 5)`.
- [x] Converter coordenadas lógicas em pixels usando as distâncias reais entre
  os centros das células.
- [x] Animar os resultados individualmente em intervalos de 0,5 segundo,
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
- [x] Implementar na API a leitura do Excel, os cálculos e o armazenamento.
- [x] Integrar a interface HTML/JavaScript à API Python.
- [x] Exibir filtros, resultados e mensagens de validação.
- [ ] Funcionar com PostgreSQL local e no PythonAnywhere.
- [x] Executar somente migrações pendentes, preservando os dados existentes.
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

- [x] Mostrar somente os estados globais `Algoritmo de seleção de combinações
  atualizado` e `Algoritmo de seleção de combinações desatualizado`.
- [x] Após cada importação, atualizar os perfis atuais com todos os resultados
  sem repetir as 200 avaliações das funções cujas assinaturas não mudaram.
- [x] Bloquear o Screener quando o perfil tiver sido calculado para uma
  quantidade anterior de resultados.
- [x] Verificar que o Screener carregou todos os filtros estatísticos e
  geométricos aprovados e somente os padrões aprovados eleitos pela incidência.
- [x] Relacionar por FK os primeiros 200 registros de `resultados` às amostras
  de validação, sem copiar as seis dezenas, e permitir novas amostras.
- [x] Relacionar cada amostra a cada função estatística, geométrica ou
  classificadora, com esperado, calculado e aprovação `S/N`. A categoria
  estatística está concluída com 800 de 800 aprovações e a geométrica com 1.200
  de 1.200; os padrões também estão concluídos com 1.800 de 1.800.
- [x] Manter referências independentes protegidas e comparar com valores
  produzidos pelas funções reais do sistema. A proteção e as 3.800 referências
  iniciais estão concluídas e foram comparadas com as funções reais.
- [x] Sincronizar critérios novos ou alterados e remover critérios excluídos com
  seus dados associados.
- [x] Preservar esperados quando somente a implementação mudar e invalidá-los
  quando mudar a regra matemática do critério.
- [x] Bloquear no Screener toda função nova, alterada, pendente ou com qualquer
  divergência; liberar somente a assinatura aprovada em todas as amostras.
- [x] Mostrar nomes legíveis de função, grupo e subgrupos esperado/calculado.
- [x] Recalcular valores obtidos sem sobrescrever os resultados esperados.
- [x] Mostrar modal com operação, etapa, progresso real, duração e erro durante
  ações demoradas. Implementado primeiro na Validação e auditoria; reutilização
  no Screener permanece para etapa posterior.
- [ ] Selecionar uma das amostras relacionadas ou acrescentar uma nova
  combinação de teste.
- [ ] Mostrar as seis dezenas, função, assinatura executada e precisão usada.
- [ ] Detalhar fórmulas, valores substituídos e resultados intermediários de
  cada critério estatístico.
- [ ] Permitir confirmar manualmente operações como a soma das seis dezenas.
- [ ] Detalhar coordenadas, segmentos, extensão, perímetro, áreas e centro de
  gravidade dos critérios geométricos.
- [ ] Mostrar ocorrências encontradas, subgrupo identificado e decisão de cada
  grupo de padrões.
- [ ] Exibir a ordem percorrida no funil e marcar os estágios posteriores como
  não avaliados quando houver exclusão anterior.
- [x] Registrar resultado esperado, resultado obtido, conformidade, observação
  e revisor humano, IA ou teste automatizado.
- [x] Disponibilizar visão resumida e abertura dos detalhes da validação.
- [x] Relatar por função os totais aprovados, divergentes e pendentes e listar
  combinação, função/filtro, esperado e calculado para cada `N`.
- [x] Permitir análise diagnóstica da divergência pela IA sem alteração
  automática do gabarito, da função ou da aprovação.
- [x] Exportar a auditoria em JSON técnico e CSV seguro para planilha.
- [x] Garantir que o relatório seja reproduzível com as mesmas amostras,
  referências, assinaturas das funções e precisões.
- [ ] Mostrar no cadastro de grupos se existe função Python classificadora,
  sua versão e se os testes de integração foram aprovados.

## Frequência das dezenas em construção

- [x] Criar estrutura, configuração, motor acumulado, carga incremental e API.
- [x] Criar item de menu e página própria com estado da base, configuração
  gravada, configuração a calcular, prévia, simulação, gravação e cancelamento.
- [x] Manter `Salvar dados` marcado inicialmente e exigir confirmação explícita
  antes de persistir.
- [x] Criar gráficos de colunas da fotografia atual das 60 dezenas, selecionando
  ocorrência simples, 2VS ou 3VS e preservando unidades e valores nulos.
- [x] Criar gráfico histórico por dezena, tipo de evento e período, separando
  evolução dos intervalos da faixa prevista e sobrepondo ocorrências reais.
- [x] Avaliar a assertividade das faixas contra ocorrências futuras, com acertos,
  erros, censura, erro absoluto e erro percentual pelo intervalo real.
- [x] Oferecer ajuda modal independente da API, explicando a página de cima para
  baixo, o fluxo recomendado, a finalidade do estudo e os cuidados operacionais.
- [x] Exibir a prévia em diálogo momentâneo com situação atual, operação,
  período, totais e gravação, exigindo `Prosseguir` antes de criar a tarefa.
- [x] Navegar do bloco histórico para a página auxiliar e retornar ao mesmo
  ponto, preservando dezena, evento e período sem persistência no banco.
- [x] Abrir os gráficos históricos em página auxiliar, um por linha e em
  largura ampliada, preservando filtros na ida e na volta ao bloco de origem.
- [x] Alternar os gráficos históricos entre escala vertical automática e zoom
  visual 10×, sem modificar valores e com aviso quando houver recorte.

## Fora do escopo inicial

- apostas automáticas;
- promessa de previsão de resultados aleatórios;
- alteração direta do banco pela interface;
- armazenamento de senhas no código ou no Git.
