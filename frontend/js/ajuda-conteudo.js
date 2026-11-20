export const secoesAjuda = [
  {
    id: "inicio",
    titulo: "Começar aqui",
    topicos: [
      {
        id: "inicio-game",
        titulo: "O que é o Game",
        aliases: ["visão geral", "sistema"],
        estado: "confirmado",
        resumo: "O Game reúne estudos sobre resultados, dezenas, distribuições, padrões, filtros e combinações.",
        blocos: [
          {
            titulo: "Finalidade",
            paragrafos: [
              "O sistema organiza resultados conhecidos e permite estudar seu comportamento por diferentes critérios. Os estudos ajudam a comparar configurações e filtrar combinações; eles não garantem o resultado de um sorteio.",
            ],
          },
          {
            titulo: "Como usar esta Ajuda",
            paragrafos: [
              "Escolha um assunto na lista lateral ou pesquise uma palavra. Cada resultado da busca abre diretamente o tópico correspondente.",
            ],
          },
        ],
        relacionados: ["inicio-atualizacao", "referencia-linha-tempo"],
      },
      {
        id: "inicio-atualizacao",
        titulo: "Resultados atualizados",
        aliases: ["último concurso", "base atualizada"],
        estado: "confirmado",
        resumo: "Os cálculos usam os resultados existentes no banco consultado.",
        blocos: [
          {
            titulo: "Por que conferir",
            paragrafos: [
              "O último concurso cadastrado determina até onde o sistema conhece os resultados. Se o banco estiver atrasado, o próximo concurso indicado pelo sistema também ficará diferente do concurso promovido pela operadora.",
            ],
          },
        ],
        relacionados: ["conceito-concurso-alvo", "conceito-corte-historico"],
      },
      {
        id: "inicio-localizar-assunto",
        titulo: "Localizar um assunto",
        aliases: ["pesquisa", "busca", "navegação"],
        estado: "confirmado",
        resumo: "A busca consulta títulos, nomes alternativos e o conteúdo dos tópicos.",
        blocos: [
          {
            titulo: "Navegação",
            paragrafos: [
              "A lista lateral agrupa conceitos, páginas e referências. O endereço do navegador conserva o tópico aberto, permitindo guardar ou compartilhar um link direto.",
              "Sem um tópico indicado no endereço, a Ajuda reabre o último assunto consultado neste navegador.",
            ],
          },
        ],
      },
    ],
  },
  {
    id: "conceitos",
    titulo: "Conceitos gerais",
    topicos: [
      {
        id: "conceito-concurso-resultado",
        titulo: "Concurso e resultado",
        aliases: ["sorteio", "dezenas sorteadas", "resultado cadastrado"],
        estado: "confirmado",
        resumo: "Concurso identifica o sorteio; resultado informa o que foi sorteado.",
        blocos: [
          {
            titulo: "Concurso",
            paragrafos: ["É o número sequencial que identifica um sorteio. O número do concurso também serve como posição temporal dos cálculos históricos."],
          },
          {
            titulo: "Resultado",
            paragrafos: ["É o registro do concurso, com data e seis dezenas sorteadas. Ao entrar no sistema, ele recebe cálculos estatísticos, geométricos e classificações produzidos pelas funções vigentes."],
          },
          {
            titulo: "Atualização da base",
            paragrafos: ["A importação acrescenta concursos novos, reconhece linhas iguais e separa divergências. Ela não deve sobrescrever silenciosamente um resultado histórico diferente."],
          },
        ],
        relacionados: ["inicio-atualizacao", "conceito-concurso-alvo", "referencia-linha-tempo"],
      },
      {
        id: "conceito-ocorrencia-intervalo",
        titulo: "Ocorrência e intervalo",
        aliases: ["última ocorrência", "distância entre concursos", "evento simples", "2VS", "3VS"],
        estado: "confirmado",
        resumo: "Ocorrência marca um evento; intervalo mede concursos entre ocorrências consecutivas.",
        blocos: [
          {
            titulo: "Ocorrência simples",
            paragrafos: ["Uma dezena tem ocorrência simples quando está presente no resultado do concurso. Para selecionar dezenas, é esse evento que importa."],
          },
          {
            titulo: "Intervalo",
            paragrafos: ["É a diferença entre os números de dois concursos consecutivos em que o mesmo evento ocorreu. Sua unidade é concurso, não dia."],
            formulas: ["intervalo = concurso da ocorrência atual − concurso da ocorrência anterior"],
          },
          {
            titulo: "Eventos 2VS e 3VS",
            paragrafos: ["Representam repetições consecutivas estudadas no módulo de Frequência e no Screener posterior de combinações. Eles não acrescentam nem retiram dezenas da primeira seleção de candidatas."],
          },
        ],
        relacionados: ["conceito-media-desvio", "pagina-frequencia-dezenas", "pagina-selecao-dezenas"],
      },
      {
        id: "conceito-media-desvio",
        titulo: "Média e desvio-padrão",
        aliases: ["μ", "sigma", "σ", "DP", "média dos intervalos"],
        estado: "confirmado",
        resumo: "A média indica a referência central observada; o desvio-padrão mede a dispersão.",
        blocos: [
          {
            titulo: "Na Seleção de dezenas",
            paragrafos: ["Para cada dezena, μ é a média dos intervalos simples já concluídos até o corte. σ é o desvio-padrão populacional desses mesmos intervalos. Ambos permanecem medidos em concursos."],
          },
          {
            titulo: "Como interpretar",
            paragrafos: ["Desvio pequeno indica intervalos históricos mais próximos da média. Desvio grande indica maior dispersão. Isso descreve o histórico e não transforma sorteios aleatórios em eventos garantidos."],
          },
        ],
        relacionados: ["conceito-ocorrencia-intervalo", "conceito-faixa-k-j"],
      },
      {
        id: "conceito-concurso-alvo",
        titulo: "Concurso-alvo",
        aliases: ["CA", "próximo concurso"],
        estado: "confirmado",
        resumo: "É o concurso que está sendo analisado.",
        blocos: [
          {
            titulo: "Definição",
            paragrafos: ["Na análise do próximo concurso, o concurso-alvo é o imediatamente posterior ao último concurso cadastrado no banco. Se L é o último cadastrado, CA = L + 1."],
            formulas: ["CA = último concurso cadastrado + 1"],
          },
          {
            titulo: "Um alvo de cada vez",
            paragrafos: ["A Seleção não calcula uma sequência de concursos ainda inexistentes. Depois que o resultado de CA entra no banco, o sistema pode recalcular a base e formar o novo alvo CA + 1."],
          },
        ],
        relacionados: ["conceito-corte-historico", "inicio-atualizacao"],
      },
      {
        id: "conceito-corte-historico",
        titulo: "Corte histórico",
        aliases: ["corte", "C menos 1", "C-1"],
        estado: "confirmado",
        resumo: "É o último concurso autorizado a participar de determinado cálculo.",
        blocos: [
          {
            titulo: "Uso",
            paragrafos: ["Ao avaliar um concurso-alvo C sem usar informação futura, a Seleção considera somente concursos menores que C. O resultado de C só é lido depois que a lista foi formada."],
            formulas: ["corte histórico do alvo C = C − 1"],
          },
          {
            titulo: "Exemplo",
            paragrafos: ["Para testar o concurso 500, a seleção é calculada com os concursos 1 a 499. Somente depois o resultado 500 é consultado para contar os acertos."],
          },
        ],
        relacionados: ["conceito-concurso-alvo", "referencia-linha-tempo"],
      },
      {
        id: "conceito-faixa-k-j",
        titulo: "Faixa ajustada, k e j",
        aliases: ["fator k", "fator j", "centro deslocado", "limite inferior", "limite superior", "LI ajustado", "LS ajustado"],
        estado: "confirmado",
        resumo: "k controla a largura admitida e j desloca essa faixa sobre a distribuição histórica.",
        blocos: [
          {
            titulo: "Dados usados",
            paragrafos: ["U é o concurso da última ocorrência conhecida, μ é a média dos intervalos e σ é o desvio-padrão. A curva e os intervalos históricos já ocorreram e não são alterados por k ou j."],
          },
          {
            titulo: "Fator k",
            paragrafos: ["k define a meia largura da faixa ajustada. O padrão é 1 e seu intervalo permitido é maior que zero e menor ou igual a 1. Reduzir k estreita a faixa e tende a tornar a aprovação mais restritiva."],
          },
          {
            titulo: "Fator j",
            paragrafos: ["j desloca a faixa inteira em unidades de desvio-padrão, sem alterar sua largura. Zero mantém a referência em U + μ; valor positivo desloca para concursos posteriores e valor negativo para anteriores. j deve permanecer entre −k e +k."],
          },
          {
            titulo: "Cálculo",
            paragrafos: ["Os limites inteiros são arredondados para fora e são inclusivos. A dezena é aprovada somente quando o concurso-alvo está dentro da faixa operacional."],
            formulas: [
              "centro_original = U + μ\ncentro_deslocado = U + μ + j × σ\nmeia_largura = k × σ",
              "LI ajustado = piso(centro_deslocado − meia_largura)\nLS ajustado = teto(centro_deslocado + meia_largura)\naprovada quando LI ajustado ≤ CA ≤ LS ajustado",
            ],
          },
          {
            titulo: "Experimentação",
            paragrafos: ["Os mesmos valores de k e j valem para todo o estudo. Escolhê-los separadamente depois de ver cada resultado usaria informação futura e invalidaria o Backtest. O objetivo é comparar pares completos, observando quantidade de dezenas, acertos e custo das combinações."],
          },
        ],
        relacionados: ["conceito-media-desvio", "conceito-backtest", "pagina-selecao-dezenas"],
      },
      {
        id: "conceito-configuracao-assinatura",
        titulo: "Configuração e assinatura",
        aliases: ["configuração salva", "imutável", "SHA-256", "versão do cálculo"],
        estado: "confirmado",
        resumo: "A configuração identifica os parâmetros usados; a assinatura protege sua integridade.",
        blocos: [
          {
            titulo: "Configuração",
            paragrafos: ["É o conjunto nomeado de parâmetros e da versão do cálculo. Na Seleção, inclui k, j, modo MAX ou FIXA e a quantidade fixa quando aplicável."],
          },
          {
            titulo: "Assinatura",
            paragrafos: ["É um identificador SHA-256 calculado pelo sistema a partir do conteúdo relevante. O usuário não precisa criar nem editar esse valor. Se o conteúdo mudar, a assinatura esperada também muda."],
          },
          {
            titulo: "Imutabilidade",
            paragrafos: ["Uma configuração salva e utilizada fica protegida contra alteração. Para testar outros valores, cria-se uma nova configuração. Isso permite saber exatamente quais parâmetros originaram cada estudo ou registro."],
          },
        ],
        relacionados: ["conceito-backtest", "conceito-dados-gravados"],
      },
      {
        id: "conceito-perfil-fotografia",
        titulo: "Perfil e fotografia",
        aliases: ["perfil operacional", "fotografia dos cálculos", "snapshot", "corte acumulado"],
        estado: "confirmado",
        resumo: "Perfil resume uma série; fotografia preserva o estado conhecido em determinado corte.",
        blocos: [
          {
            titulo: "Perfil operacional",
            paragrafos: ["Resume uma grandeza calculada sobre o conjunto vigente de resultados, como quantidade, média, desvio-padrão, mínimo e máximo. Os perfis usados pelo Screener precisam corresponder à quantidade e à assinatura atuais dos resultados."],
          },
          {
            titulo: "Fotografia da Frequência",
            paragrafos: ["Preserva, para um concurso de corte, o que era conhecido sobre as 60 dezenas e os eventos simples, 2VS e 3VS. A primeira fotografia é a do concurso 500, calculada sobre a base iniciada no concurso 1."],
          },
          {
            titulo: "Não confundir",
            paragrafos: ["Fotografia não é uma imagem do gráfico. É um estado numérico preservado para impedir que resultados posteriores entrem em um cálculo histórico."],
          },
        ],
        relacionados: ["referencia-linha-tempo", "conceito-atualizacao-calculo", "pagina-frequencia-dezenas"],
      },
      {
        id: "conceito-registro-selecao",
        titulo: "Seleção registrada",
        aliases: ["previsão", "registro do screener", "lista congelada", "próximo concurso"],
        estado: "confirmado",
        resumo: "É a lista de dezenas preservada antes do sorteio para conferência posterior.",
        blocos: [
          {
            titulo: "Como é formada",
            paragrafos: ["Usa uma configuração salva e somente resultados até o último concurso cadastrado. O alvo é o concurso imediatamente seguinte."],
          },
          {
            titulo: "Por que fica congelada",
            paragrafos: ["Depois de registrada, a lista, suas faixas e seu ranking não são recalculados quando o resultado chega. O sorteio serve apenas para conferir a seleção original. A base atualizada origina outra seleção para o concurso seguinte."],
          },
          {
            titulo: "Alcance",
            paragrafos: ["O registro é um estudo estatístico auditável, não uma promessa de acerto. Ele fornece as dezenas que poderão originar combinações submetidas ao Screener de combinações."],
          },
        ],
        relacionados: ["conceito-concurso-alvo", "conceito-configuracao-assinatura", "pagina-selecao-dezenas"],
      },
      {
        id: "conceito-backtest",
        titulo: "Backtest",
        aliases: ["estudo histórico", "teste histórico"],
        estado: "confirmado",
        resumo: "É um estudo de uma configuração em concursos já conhecidos.",
        blocos: [
          {
            titulo: "Como funciona",
            paragrafos: ["Em cada alvo, o Backtest usa apenas a base histórica permitida para aquele momento. O resultado já conhecido serve para conferir o desempenho, não para formar a seleção testada."],
          },
          {
            titulo: "Entrada e período",
            paragrafos: ["Na Seleção de dezenas, o usuário escolhe uma configuração previamente salva e um concurso inicial a partir de 500. O final é sempre o último resultado cadastrado."],
          },
          {
            titulo: "O que permanece",
            paragrafos: ["O relatório mantém na memória do navegador o concurso, a quantidade de dezenas retornadas e os acertos de 0 a 6. Ele não grava avaliações das 60 dezenas, listas, resumos ou pontos dos gráficos. Atualizar ou fechar a página elimina o relatório."],
          },
          {
            titulo: "Como comparar",
            paragrafos: ["Acertos devem ser avaliados junto com a quantidade de dezenas e o custo C(N,6). Uma lista maior pode acertar mais apenas por gerar muito mais combinações."],
          },
        ],
        relacionados: ["pagina-selecao-dezenas", "referencia-linha-tempo"],
      },
      {
        id: "conceito-screener",
        titulo: "Screener, teste e aplicação",
        aliases: ["Screener", "filtros", "funil", "Teste do Screener", "Aplicação do Screener", "Executar 5000"],
        estado: "confirmado",
        resumo: "É um conjunto encadeado de filtros aplicados às combinações.",
        blocos: [
          {
            titulo: "Regra geral",
            paragrafos: ["O Screener encadeia filtros estatísticos, geométricos e de padrões. Uma combinação somente é aprovada quando passa por todos os filtros exigidos; uma reprovação encerra sua passagem pelo funil."],
          },
          {
            titulo: "Teste do Screener",
            paragrafos: ["Usa uma amostra reproduzível das 5.000 primeiras combinações de 60 dezenas tomadas seis a seis. Serve para conferir funções, integração e comportamento dos filtros sem percorrer o universo integral."],
          },
          {
            titulo: "Aplicação do Screener",
            paragrafos: ["Executa o mesmo funil nas 50.063.860 combinações de 60 dezenas tomadas seis a seis. Antes de começar, o sistema exige a confirmação do usuário e verifica as condições de homologação e cobertura dos filtros."],
          },
          {
            titulo: "Uso posterior",
            paragrafos: ["O mesmo motor deverá filtrar as combinações formadas a partir das dezenas selecionadas. Nesse caso, o conjunto de entrada não é necessariamente nem a amostra de 5.000 nem o universo completo C(60,6)."],
          },
        ],
        relacionados: ["pagina-preparacao-screener", "referencia-quantidades"],
      },
      {
        id: "conceito-dados-gravados",
        titulo: "Dados gravados e momentâneos",
        aliases: ["persistência", "PostgreSQL", "temporário"],
        estado: "confirmado",
        resumo: "Nem todo resultado exibido é armazenado no banco de dados.",
        blocos: [
          {
            titulo: "Diferença",
            paragrafos: ["Um dado gravado permanece disponível depois da consulta. Um resultado momentâneo é calculado para exibição e desaparece quando a consulta termina. Cada página deve informar o efeito de seus comandos antes da confirmação."],
          },
          {
            titulo: "Exemplos",
            itens: [
              "Resultados importados, configurações salvas e seleções registradas são persistidos.",
              "A análise de uma configuração da Seleção e o relatório gráfico do Backtest são momentâneos.",
              "A simulação da Frequência usa o mesmo motor de cálculo, mas não grava quando Salvar dados está desmarcado.",
            ],
          },
        ],
        relacionados: ["referencia-persistencia"],
      },
      {
        id: "conceito-validacao",
        titulo: "Validação, homologação e cobertura",
        aliases: ["homologação", "cobertura", "bloqueio"],
        estado: "confirmado",
        resumo: "São controles usados para impedir a execução com critérios não conferidos.",
        blocos: [
          {
            titulo: "Diferenças",
            itens: [
              "Validação compara o valor calculado pela função real com uma referência esperada independente.",
              "Homologação aprova formalmente a função e a regra na versão e assinatura conferidas.",
              "Cobertura comprova que todos os critérios e casos exigidos participaram da conferência.",
            ],
          },
          {
            titulo: "Efeito no Screener",
            paragrafos: ["Função nova ou alterada, assinatura divergente, avaliação pendente ou reprovada, perfil antigo ou cobertura incompleta bloqueiam a execução. Não existe aprovação automática por ausência de teste."],
          },
        ],
        relacionados: ["pagina-validacao-auditoria-nova", "referencia-bloqueios"],
      },
      {
        id: "conceito-atualizacao-calculo",
        titulo: "Cálculo integral e incremental",
        aliases: ["reconstrução", "atualização incremental", "recalcular", "concurso novo"],
        estado: "confirmado",
        resumo: "Integral reconstrói a base calculada; incremental acrescenta somente a parte nova.",
        blocos: [
          {
            titulo: "Frequência das dezenas",
            paragrafos: ["A primeira carga ou uma mudança de configuração cria uma nova geração integral. Se apenas concursos novos foram acrescentados e a origem anterior continua íntegra, o sistema adiciona os novos cortes à geração ativa."],
          },
          {
            titulo: "Quando reconstruir",
            paragrafos: ["Alteração em resultado antigo, lacuna histórica, assinatura de origem incompatível ou mudança de configuração exigem reconstrução explícita. O sistema não deve chamar de incremental uma atualização cuja origem deixou de corresponder à base."],
          },
          {
            titulo: "Outros módulos",
            paragrafos: ["O termo incremental não deve ser generalizado. Resultados novos atualizam os perfis operacionais sobre a base completa, mas não obrigam a refazer provas matemáticas quando função, regra e precisão continuam com as mesmas assinaturas."],
          },
        ],
        relacionados: ["conceito-perfil-fotografia", "conceito-configuracao-assinatura", "referencia-linha-tempo"],
      },
    ],
  },
  {
    id: "paginas",
    titulo: "Ajuda por página",
    topicos: [
      {
        id: "pagina-painel",
        titulo: "Painel",
        aliases: ["resultados", "importação", "voo dos pássaros", "mancha", "aparência", "quadrantes", "Q1 Q2 Q3 Q4", "ocorrências das dezenas", "gradiente das dezenas"],
        estado: "confirmado",
        resumo: "Importa resultados e apresenta cada sorteio sobre a grade geométrica das 60 dezenas.",
        blocos: [
          {
            titulo: "Finalidade",
            paragrafos: ["O Painel é o ponto de entrada dos resultados. Ele também permite percorrer concursos e observar dezenas, linha geométrica, fechamento, regiões, média espacial e centro de gravidade."],
          },
          {
            titulo: "Importar resultados",
            itens: [
              "Selecionar Excel abre a escolha de uma planilha .xlsx.",
              "Importar, calcular e armazenar envia a planilha ao servidor, valida os dados, inclui concursos novos e calcula os campos derivados.",
              "Linhas iguais são reconhecidas; divergências não devem substituir silenciosamente o histórico.",
              "A mensagem abaixo dos comandos informa sucesso, rejeição ou inconsistência encontrada.",
            ],
          },
          {
            titulo: "Navegar pelos resultados",
            paragrafos: ["Resultado escolhe diretamente um concurso. Anterior e Próximo percorrem a lista e, ao ultrapassar uma extremidade, continuam pela outra. Tempo por resultado define o intervalo do Voo dos pássaros."],
          },
          {
            titulo: "Comandos de visualização",
            itens: [
              "Iniciar voo dos pássaros percorre automaticamente os resultados; o mesmo botão pausa o movimento.",
              "Desenhar mancha sobrepõe as ocorrências de todos os resultados carregados para mostrar concentração visual.",
              "Aparência escolhe cores, espessuras, transparência e elementos visíveis. Essa preferência fica somente neste navegador.",
              "Limpar gráfico remove o desenho atual, mas não apaga resultados do banco.",
            ],
          },
          {
            titulo: "Voo dos pássaros e camadas de cada concurso",
            paragrafos: ["O Voo dos pássaros apresenta um concurso por vez e avança no intervalo definido em Tempo por resultado. Durante o voo, o mesmo botão muda para Pausar voo dos pássaros e interrompe a sequência sem apagar os resultados."],
            itens: [
              "Média espacial mostra a média aritmética das coordenadas cartesianas das seis dezenas do concurso; não é a média dos números sorteados.",
              "Linha Poligonal liga as seis dezenas na sequência crescente e permanece aberta.",
              "Polígono 1 acrescenta o fechamento entre o último e o primeiro ponto da Linha Poligonal. Suas linhas podem formar regiões internas.",
              "Polígono 2 mostra o contorno fechado sem cruzamentos que utiliza as seis dezenas como vértices. O resumo informa Área P2 e CG2.",
              "Os marcadores permitem exibir ou ocultar cada uma dessas quatro camadas sem modificar o concurso nem os cálculos armazenados.",
            ],
          },
          {
            titulo: "Média espacial, CG1 e CG2",
            paragrafos: ["As três medidas são coordenadas do painel, mas possuem origens diferentes. A Média espacial é obtida diretamente das seis posições; CG1 é o centro de gravidade do Polígono 1; CG2 é o centro de gravidade do Polígono 2."],
            itens: [
              "No concurso individual, os pontos identificam a posição calculada para aquele resultado.",
              "No quadro Manchas, Média espacial, CG1 e CG2 reúnem as posições de todos os concursos carregados e podem ser vistas separadamente ou sobrepostas.",
              "Cada mancha usa uma cor própria para que as três distribuições continuem distinguíveis quando forem combinadas.",
            ],
          },
          {
            titulo: "Como ler as manchas históricas",
            paragrafos: ["Para cada medida marcada, o sistema desenha um círculo na coordenada decimal de cada concurso. Depois calcula a média dessas coordenadas, marca esse centro e traça referências circulares de 20%, 40% e 60% da maior distância observada até ele."],
            itens: [
              "A cor fica mais intensa perto do centro calculado e mais clara à medida que o ponto se afasta.",
              "O resumo informa a coordenada média e quantos concursos ficaram até 20%, entre 20% e 40%, entre 40% e 60% e além de 60% da distância máxima.",
              "A proporção 1:n no resumo facilita a leitura da frequência histórica dentro de cada faixa.",
              "Os círculos, faixas e proporções descrevem os resultados carregados; não garantem a posição do próximo concurso.",
            ],
          },
          {
            titulo: "Configuração visual e salvamento",
            paragrafos: ["Aparência permite ajustar cores, espessura das linhas, diâmetro dos vértices e pontos das manchas, transparência das regiões, fator de intensidade e elementos geométricos visíveis."],
            itens: [
              "Salvar aplica os valores e os conserva neste navegador para as próximas aberturas do sistema.",
              "Fechar sem salvar mantém a última configuração gravada.",
              "Restaurar padrão preenche o formulário com os valores originais; para torná-los efetivos e persistentes, escolha também Salvar.",
              "As opções do quadro Aparência mudam somente a apresentação. Elas não alteram resultados, áreas, centros de gravidade ou dados do banco.",
            ],
          },
          {
            titulo: "Camada Dezenas: ocorrências e gradiente",
            paragrafos: ["Ao marcar Dezenas e escolher Desenhar mancha, o sistema conta quantas vezes cada uma das 60 dezenas aparece em todos os resultados carregados. Cada ocorrência é representada por um pequeno círculo verde dentro da célula da respectiva dezena."],
            itens: [
              "Os círculos ocupam uma matriz de 10 por 10 dentro de cada dezena. Quando há mais de 100 ocorrências, as posições da matriz voltam a ser utilizadas e os novos círculos se sobrepõem aos anteriores.",
              "Todos os círculos possuem o mesmo tamanho. A tonalidade é calculada pela proximidade entre a quantidade daquela dezena e a média de ocorrências das 60 dezenas.",
              "Quanto mais próxima da média histórica estiver a quantidade, mais intensa será a tonalidade; quanto mais distante, mais clara ela será.",
              "O gradiente descreve o histórico carregado. Ele não classifica uma dezena como mais provável e não garante ocorrência futura.",
            ],
          },
          {
            titulo: "Tabela de ocorrências e combinação das manchas",
            paragrafos: ["O resumo à direita apresenta a quantidade exata de ocorrências de cada dezena. Para caber ao lado do painel sem deslocá-lo, as 60 dezenas são distribuídas em quatro colunas de quinze itens."],
            itens: [
              "A primeira coluna contém 01–15; a segunda, 16–30; a terceira, 31–45; e a quarta, 46–60.",
              "Cada item usa o formato dezena: quantidade. Por exemplo, 01: 301 informa que a dezena 01 apareceu 301 vezes nos resultados carregados.",
              "Quando somente Dezenas está marcada, o resumo mostra diretamente a tabela das 60 ocorrências.",
              "Quando Dezenas é combinada com Média espacial, CG1, CG2 ou Quadrantes, os resumos dessas análises permanecem acima e a tabela das dezenas aparece abaixo.",
              "Se o conteúdo combinado ultrapassar a altura do mapa, use a rolagem interna do resumo. O tamanho do Painel permanece inalterado.",
              "Depois de importar resultados novos, escolha Desenhar mancha novamente para atualizar os pontos e as quantidades.",
            ],
          },
          {
            titulo: "Quadrantes: origem e divisão",
            paragrafos: ["A camada Quadrantes divide o painel das dezenas com dois eixos verdes. O eixo vertical passa entre as dezenas 05 e 06. O eixo horizontal passa entre as dezenas 21 e 31. O encontro dessas linhas é a origem usada para desenhar os quatro quadrados."],
            itens: [
              "Q1 é a região superior direita: dezenas 06–10, 16–20 e 26–30.",
              "Q2 é a região superior esquerda: dezenas 01–05, 11–15 e 21–25.",
              "Q3 é a região inferior esquerda: dezenas 31–35, 41–45 e 51–55.",
              "Q4 é a região inferior direita: dezenas 36–40, 46–50 e 56–60.",
            ],
          },
          {
            titulo: "O que os quadrados representam",
            paragrafos: ["Ao desenhar a mancha, o sistema percorre todos os concursos carregados e conta em qual quadrante caiu cada dezena. Ele calcula primeiro as quatro quantidades e desenha somente um quadrado por quadrante. O lado maior indica maior incidência histórica; a área do quadrado não é o percentual, mas uma representação visual baseada no lado calculado."],
            formulas: [
              "referência = total de ocorrências ÷ 4",
              "passo = menor extensão disponível ÷ referência ÷ 2",
              "lado do quadrado = quantidade do quadrante × passo",
            ],
            itens: [
              "A menor extensão disponível impede que algum quadrado ultrapasse a região que pode ocupá-lo.",
              "A referência histórica ocupa aproximadamente metade da extensão disponível, deixando espaço para o crescimento após novos concursos.",
              "A contagem é refeita com os resultados carregados; os valores da visualização não são gravados no banco.",
            ],
          },
          {
            titulo: "Cores, números e empates",
            paragrafos: ["Dentro de cada quadrado aparecem a quantidade de dezenas contadas e seu percentual sobre o total. O resumo à direita repete Q1 a Q4 e informa também a posição classificatória."],
            itens: [
              "Verde-escuro identifica a maior quantidade.",
              "Verde claro, com 50% da intensidade do primeiro, identifica a segunda maior.",
              "Amarelo identifica a terceira maior e vermelho identifica a menor quantidade.",
              "Se dois ou mais quadrantes tiverem a mesma quantidade, recebem a mesma posição e a mesma cor.",
            ],
          },
          {
            titulo: "Como usar Quadrantes",
            itens: [
              "Marque Quadrantes no quadro Manchas e escolha Desenhar mancha.",
              "O marcador controla em conjunto os eixos, os quatro quadrados, seus textos e o trecho Quadrantes do resumo lateral.",
              "Quadrantes pode ser marcado junto com Dezenas, Média espacial, CG1 e CG2. As camadas são sobrepostas e seus resumos permanecem separados.",
              "Para retirar somente essa representação, desmarque Quadrantes e escolha novamente Desenhar mancha.",
              "Depois de importar concursos novos, desenhe a mancha novamente para recalcular a distribuição com o histórico atualizado.",
            ],
          },
          {
            titulo: "Sequência recomendada",
            paragrafos: ["Confira a planilha, importe, leia a mensagem final e selecione alguns concursos antes de usar voo ou mancha. Alterações na aparência não modificam os cálculos."],
          },
        ],
        relacionados: ["conceito-concurso-resultado", "pagina-distribuicoes"],
      },
      {
        id: "pagina-cadastros",
        titulo: "Cadastros",
        aliases: ["visão geral dos cadastros", "grupos", "padrões"],
        estado: "confirmado",
        resumo: "O menu Cadastros oferece acesso direto aos formulários de Grupo e Padrões.",
        blocos: [
          {
            titulo: "Acesso aos formulários",
            paragrafos: ["Abra Cadastros no menu principal e escolha Grupo ou Padrões. Não existe uma página intermediária: a opção escolhida abre diretamente o formulário correspondente."],
          },
          {
            titulo: "Ordem recomendada",
            paragrafos: ["Cadastre primeiro o Grupo. Depois abra Padrões, escolha esse Grupo e cadastre os padrões que pertencem a ele. Um nome e uma descrição não criam por si só uma função Python executável no Screener."],
          },
        ],
        relacionados: ["pagina-grupos-padroes", "pagina-padroes"],
      },
      {
        id: "pagina-grupos-padroes",
        titulo: "Grupos de padrões",
        aliases: ["grupo", "cadastro de grupos", "categorias de padrões"],
        estado: "confirmado",
        resumo: "Cria e mantém as categorias conceituais às quais os padrões pertencem.",
        blocos: [
          {
            titulo: "Localizar e consultar",
            paragrafos: ["A caixa Localizar permite selecionar um Grupo existente ou digitar parte de seu nome. A lista é reduzida aos nomes que contêm o trecho digitado. Escolher um nome carrega o registro no formulário sem alterar o banco."],
          },
          {
            titulo: "Criar e alterar",
            paragrafos: ["Use Novo registro para abrir um formulário vazio. Informe Nome do grupo e Descrição e escolha Salvar registro. A gravação somente ocorre depois da confirmação. Para alterar um Grupo existente, selecione-o, use Editar, faça a correção e confirme o salvamento."],
          },
          {
            titulo: "Excluir e proteger os dados",
            paragrafos: ["A exclusão também exige confirmação e pode ser recusada quando houver Padrões vinculados ao Grupo. Localizar, selecionar, abrir um registro ou cancelar uma edição não grava dados. O código do Grupo é controlado pelo sistema."],
          },
        ],
        relacionados: ["pagina-cadastros", "pagina-padroes"],
      },
      {
        id: "pagina-padroes",
        titulo: "Padrões",
        aliases: ["cadastro de padrões", "padrões por grupo", "função Python"],
        estado: "confirmado",
        resumo: "Cria e mantém Padrões, sempre vinculados ao Grupo ao qual pertencem.",
        blocos: [
          {
            titulo: "Escolher o Grupo",
            paragrafos: ["Escolha primeiro o Grupo. Esse campo é obrigatório e determina quais Padrões aparecem na caixa de seleção. Ao mudar o Grupo, a lista é atualizada imediatamente e passa a mostrar somente os registros vinculados à nova escolha."],
          },
          {
            titulo: "Localizar e consultar",
            paragrafos: ["Depois de escolher o Grupo, use Localizar para selecionar um Padrão ou digitar parte de seu nome. Escolher um nome carrega Nome do padrão e Descrição no formulário. A consulta não altera o registro."],
          },
          {
            titulo: "Criar, alterar e excluir",
            paragrafos: ["Use Novo registro somente depois de escolher o Grupo. Informe Nome do padrão e Descrição e confirme o salvamento. Editar preserva o vínculo com o Grupo escolhido. Excluir pede confirmação antes de remover o registro. Cancelar ou fechar uma confirmação não grava nem exclui dados."],
          },
          {
            titulo: "Limite importante",
            paragrafos: ["Cadastrar nome, descrição e Grupo organiza o Padrão, mas não implementa o critério do Screener. Cada filtro precisa de função Python, testes, homologação e integração próprias. Os dados estatísticos e a conferência do funcionamento pertencem à Validação e Auditoria, não a este formulário."],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["Somente a confirmação positiva de uma inclusão, alteração ou exclusão modifica o PostgreSQL. Consultar, trocar o Grupo, localizar um Padrão ou cancelar mantém os dados inalterados."],
          },
        ],
        relacionados: ["conceito-screener", "conceito-validacao", "pagina-preparacao-screener"],
      },
      {
        id: "pagina-distribuicoes",
        titulo: "Distribuições",
        aliases: ["distribuições históricas", "perfis operacionais", "configurar faixas", "faixa mínima", "faixa máxima", "múltiplos do desvio-padrão", "percentual da média"],
        estado: "confirmado",
        resumo: "Mostra como os parâmetros estatísticos e geométricos se distribuíram nos concursos conhecidos e permite estudar faixas de referência.",
        blocos: [
          {
            titulo: "Finalidade da página",
            paragrafos: ["A página reúne dez perfis calculados sobre os resultados cadastrados: soma, média aritmética, mediana, desvio-padrão das dezenas, extensão aberta, perímetro fechado, quantidade de regiões, área total e as coordenadas X e Y do centro de gravidade. Ela permite observar o comportamento histórico e estudar limites; não calcula a probabilidade de um concurso específico."],
          },
          {
            titulo: "Como ler cada gráfico",
            itens: [
              "As barras representam os valores realmente observados nos concursos cadastrados.",
              "A curva vermelha é somente uma referência visual de distribuição normal; ela não substitui as barras nem afirma que os dados seguem exatamente uma curva normal.",
              "A linha azul tracejada marca a média histórica do parâmetro.",
              "A área verde-clara mostra a faixa calculada para o estudo.",
              "As duas linhas verdes tracejadas marcam exatamente a Faixa mín. e a Faixa máx.",
            ],
          },
          {
            titulo: "Valores apresentados abaixo do gráfico",
            itens: [
              "Média e Desvio descrevem o conjunto de valores observados para aquele parâmetro.",
              "Mín. e Máx. são os menores e maiores valores que realmente ocorreram no histórico. Eles não são definidos pelo formulário.",
              "Faixa mín. e Faixa máx. são limites calculados pelo método e pelas margens escolhidas no formulário.",
              "Classes informa em quantos intervalos as barras do histograma foram organizadas.",
              "Soma e média aritmética são equivalentes neste jogo, pois cada resultado contém seis dezenas e média = soma ÷ 6; por isso não constituem dois filtros independentes.",
            ],
          },
          {
            titulo: "Resumo da janela histórica",
            paragrafos: ["Amostra informa quantos resultados participaram do cálculo. Concursos e Datas mostram o primeiro e o último registro considerados. Faixa identifica o método salvo e apresenta, entre parênteses, as margens inferior e superior. Se novos concursos forem cadastrados, use Atualizar para recalcular os perfis com o histórico disponível no servidor."],
          },
          {
            titulo: "Formulário Configuração das faixas do estudo",
            paragrafos: ["Configurar faixas abre o formulário usado para escolher como os limites serão calculados. A configuração vale para os dez perfis, mas cada perfil recebe limites próprios porque possui média e desvio diferentes."],
            itens: [
              "Método escolhe entre Múltiplos do desvio-padrão e Percentual da média.",
              "Margem inferior determina quanto será subtraído da média para formar a Faixa mín.",
              "Margem superior determina quanto será somado à média para formar a Faixa máx.",
              "As margens devem ser iguais ou maiores que zero e podem ser diferentes, criando uma faixa assimétrica.",
              "Os valores iniciais são método por desvio-padrão, margem inferior 1 e margem superior 1.",
            ],
          },
          {
            titulo: "Método Múltiplos do desvio-padrão",
            paragrafos: ["Neste método, cada margem representa uma quantidade de desvios-padrão. Ele é útil quando se deseja relacionar a largura da faixa à dispersão histórica de cada parâmetro."],
            formulas: [
              "Faixa mín. = média − margem inferior × desvio-padrão",
              "Faixa máx. = média + margem superior × desvio-padrão",
            ],
            itens: [
              "Exemplo simétrico: média 30, desvio 5 e margens 1 e 1 produzem faixa de 25 a 35.",
              "Exemplo assimétrico: média 30, desvio 5, margem inferior 0,5 e superior 1,5 produzem faixa de 27,5 a 37,5.",
            ],
          },
          {
            titulo: "Método Percentual da média",
            paragrafos: ["Neste método, as margens são percentuais aplicados ao valor absoluto da média. O desvio-padrão continua sendo mostrado como informação histórica, mas não define os limites."],
            formulas: [
              "Faixa mín. = média − | média | × margem inferior ÷ 100",
              "Faixa máx. = média + | média | × margem superior ÷ 100",
            ],
            itens: ["Exemplo: média 30, margem inferior 10% e superior 20% produzem faixa de 27 a 36."],
          },
          {
            titulo: "Calcular prévia",
            paragrafos: ["Calcular prévia consulta o histórico pela mesma API usada nos gráficos e exibe, em uma tabela, os limites inferior e superior dos dez parâmetros. A prévia serve para conferir o efeito das margens antes de salvar e não modifica o banco nem ativa o Screener. Se algum campo for alterado depois do cálculo, a prévia deixa de ser válida e deve ser calculada novamente."],
          },
          {
            titulo: "Salvar, cancelar e atualizar",
            itens: [
              "Salvar estudo somente fica disponível depois de uma prévia válida. Ele conserva o método e as margens neste navegador e aplica imediatamente a prévia aos gráficos.",
              "Cancelar, fechar pelo X ou sair sem salvar mantém a última configuração salva.",
              "Atualizar recarrega do servidor os dez perfis usando a configuração que está salva no navegador.",
            ],
          },
          {
            titulo: "Efeito nos dados e no Screener",
            paragrafos: ["A configuração deste formulário é um estudo visual salvo somente no navegador. Ela não altera os resultados cadastrados, não grava uma configuração operacional no PostgreSQL e não ativa nem executa o Screener. O aviso Estudo — screener inativo existe para tornar essa separação explícita."],
          },
        ],
        relacionados: ["conceito-perfil-fotografia", "pagina-preparacao-screener"],
      },
      {
        id: "pagina-preparacao-screener",
        titulo: "Preparação do Screener",
        aliases: ["Screener", "Executar 5000", "Teste do Screener", "Aplicação do Screener", "5.000", "limite de raridade", "amostra protegida"],
        estado: "confirmado",
        resumo: "Permite testar o funil em 5.000 combinações ou aplicá-lo às 50.063.860 combinações possíveis.",
        blocos: [
          {
            titulo: "Finalidade",
            paragrafos: ["A página usa o mesmo conjunto de filtros estatísticos, geométricos e de padrões em dois modos. O Teste do Screener permite uma conferência rápida em 5.000 combinações; a Aplicação do Screener percorre todas as 50.063.860 combinações possíveis."],
          },
          {
            titulo: "Limite de raridade",
            paragrafos: ["Define a porcentagem máxima para selecionar padrões raros que eliminam combinações. O valor deve ficar entre 0% e 100% e é lembrado neste navegador."],
          },
          {
            titulo: "Teste do Screener",
            paragrafos: ["Abre uma confirmação e, somente depois da autorização do usuário, solicita ao mesmo motor do Screener a análise das primeiras 5.000 combinações. Durante o cálculo, uma janela informa o progresso e permite solicitar o cancelamento. O cancelamento também exige confirmação; o servidor interrompe o laço no próximo ponto seguro e descarta as contagens parciais mantidas em memória."],
          },
          {
            titulo: "Aplicação do Screener",
            paragrafos: [
              "Analisa as 50.063.860 combinações com o mesmo motor e os mesmos filtros do teste. O comando abre uma confirmação que informa o tamanho do universo antes de iniciar o processamento.",
              "A janela de andamento apresenta progresso e duração. Como a operação pode ser longa, mantenha o computador e o servidor da aplicação funcionando e conserve a página aberta para acompanhar o resultado.",
              "O botão Cancelar solicita uma segunda confirmação. Se o cancelamento for confirmado, o servidor interrompe o laço no próximo ponto seguro e descarta as contagens parciais daquela execução.",
            ],
          },
          {
            titulo: "Quadros de resultado",
            itens: [
              "Universo possível informa o total de combinações existentes; Analisadas informa quantas participaram do teste.",
              "Total excluído resume as combinações eliminadas durante o funil.",
              "Combinações aprovadas mostra as que passaram por todos os filtros exigidos.",
              "Abrir detalhes e Fechar detalhes controlam a exposição das etapas depois de uma execução bem-sucedida.",
            ],
          },
          {
            titulo: "Validação anterior à execução",
            paragrafos: ["Antes do teste ou da aplicação, o sistema confere estado global, catálogo, assinaturas, avaliações, perfis e cobertura. Se a Validação e auditoria informar algoritmo desatualizado, assinatura divergente ou cobertura pendente, o comando fica bloqueado. Essa trava impede que filtros ainda não validados produzam um resultado aparentemente válido; não significa que o Screener não encontrou combinações."],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["O Teste e a Aplicação do Screener produzem quadros de análise. As combinações e as contagens parciais não são gravadas como resultados no banco de dados. O limite de raridade salvo no navegador é apenas uma preferência local."],
          },
        ],
        relacionados: ["conceito-screener", "conceito-validacao", "pagina-validacao-auditoria-nova", "referencia-quantidades"],
      },
      {
        id: "pagina-validacao-auditoria-nova",
        titulo: "Validação e auditoria",
        aliases: ["teste de filtros", "mil combinações", "teste dirigido", "inspeção visual"],
        estado: "confirmado",
        resumo: "Verifica se os filtros detectam seus padrões corretamente, sem eliminar combinações e sem alterar resultados sorteados.",
        blocos: [
          {
            titulo: "Passo a passo da Validação e auditoria",
            itens: [
              "1. Escolher os filtros: em Seleção de Filtros, escolha Todos, um grupo inteiro ou um filtro específico.",
              "2. Iniciar o teste: confira o resumo da seleção, clique em Iniciar teste e confirme. Cada filtro selecionado será aplicado independentemente às mesmas 1.000 combinações fixas.",
              "3. Acompanhar: observe o progresso total, o grupo e o filtro atual. Cancelar encerra o teste no próximo ponto seguro.",
              "4. Inspecionar um filtro: quando somente um filtro estiver selecionado, cada ocorrência encontrada será mostrada no painel. Confira as dezenas marcadas e o desenho correspondente e clique em Continuar.",
              "5. Ler o relatório: ao terminar, confira para cada filtro o total testado, o número de ocorrências e a incidência percentual nessa coleção.",
              "6. Fazer um teste dirigido: escolha obrigatoriamente um grupo e um filtro no bloco Teste dirigido e clique em Gerar 10 combinações.",
              "7. Testar as combinações dirigidas: depois da geração, clique em Iniciar teste dirigido. Analise cada combinação no painel e use Continuar até o resumo final informar quantas das 10 foram detectadas.",
            ],
          },
          {
            titulo: "Teste com 1.000 combinações",
            paragrafos: ["A coleção é fixa, possui 1.000 combinações diferentes de seis dezenas e serve para comparar execuções. Não há funil: todos os filtros selecionados recebem as mesmas 1.000 combinações, independentemente do resultado dos filtros anteriores."],
          },
          {
            titulo: "Seleção de Filtros",
            itens: [
              "Todos os grupos e Todos os filtros executam todo o catálogo disponível.",
              "Um grupo e Todos os filtros executam somente os filtros daquele grupo.",
              "Um grupo e um filtro executam somente o filtro escolhido e permitem a inspeção visual de suas ocorrências.",
            ],
          },
          {
            titulo: "Painel de inspeção",
            paragrafos: ["Os círculos identificam as seis dezenas da combinação. Os traços representam somente a geometria verificada pelo filtro. O processamento fica pausado até o usuário examinar o painel e clicar em Continuar."],
          },
          {
            titulo: "Teste dirigido",
            paragrafos: ["O sistema gera em memória 10 combinações construídas para atender sabidamente ao filtro escolhido. Geração e teste são comandos separados. O objetivo é confirmar que a função detectora reconhece casos conhecidos, especialmente quando o teste com 1.000 combinações encontra pouca ou nenhuma ocorrência."],
          },
          {
            titulo: "Como ler os resultados",
            itens: [
              "Total testado informa quantas combinações foram avaliadas pelo filtro.",
              "Ocorrências informa quantas combinações foram reconhecidas pelo filtro.",
              "Incidência é ocorrências divididas pelo total testado nessa coleção; não representa a raridade exata entre todas as 50.063.860 combinações possíveis.",
              "No teste dirigido, o resultado esperado é a detecção das 10 combinações geradas para o filtro.",
            ],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["A página não elimina combinações, não altera os resultados dos concursos e não grava as 10 combinações dirigidas. A tabela fixa de 1.000 combinações permanece no banco apenas como coleção de auditoria reutilizável."],
          },
        ],
        relacionados: ["pagina-preparacao-screener", "conceito-validacao"],
      },
      {
        id: "pagina-frequencia-dezenas",
        titulo: "Frequência das dezenas",
        aliases: ["fotografia", "intervalos", "2VS", "3VS", "histórico de frequência"],
        estado: "confirmado",
        resumo: "Preserva o que era conhecido em cada corte e analisa intervalos das 60 dezenas.",
        blocos: [
          {
            titulo: "Estado e configurações",
            paragrafos: ["Recarregar estado consulta novamente a geração ativa. Configuração gravada mostra a origem persistida; Configuração a calcular permite conferir nome, concurso inicial, tamanho inicial, eventos, multiplicador do desvio e versão antes de uma operação."],
          },
          {
            titulo: "Atualização do histórico",
            itens: [
              "Salvar dados marcado permite persistir a geração ou o incremento depois de confirmação.",
              "Salvar dados desmarcado executa uma simulação sem gravação.",
              "Permitir reconstrução se a origem mudou autoriza substituir a geração ativa somente quando a prévia identificar essa necessidade.",
              "Calcular prévia informa situação, operação, período, quantidade estimada e efeito no banco; ainda não inicia a tarefa.",
              "Prosseguir confirma e inicia a execução. Cancelar não cria tarefa.",
            ],
          },
          {
            titulo: "Fotografia atual",
            paragrafos: ["O seletor de ocorrência alterna Simples, 2VS e 3VS. Os seis gráficos mostram as 60 dezenas no último corte completo, preservando unidades e ausências de valor."],
          },
          {
            titulo: "Evolução por dezena",
            paragrafos: ["Escolha Dezena, Evento e período. Consultar dezena apresenta o resultado numérico, o Backtest simplificado e a tabela de cortes, evento anterior, faixa, ocorrência real e situação. Abrir gráficos leva à página ampliada com os mesmos filtros."],
          },
          {
            titulo: "Backtest da faixa",
            paragrafos: ["A avaliação usa somente faixas totalmente cobertas por resultados já conhecidos. Acerto significa que a ocorrência real ficou dentro dos limites inclusivos; faixas cujo futuro ainda não terminou ficam censuradas e não contam como erro."],
          },
          {
            titulo: "Cuidados",
            paragrafos: ["Não compare eventos com unidades diferentes como se fossem a mesma série. A faixa descreve o histórico observado e não garante a próxima ocorrência."],
          },
        ],
        relacionados: ["conceito-perfil-fotografia", "conceito-atualizacao-calculo", "pagina-graficos-frequencia"],
      },
      {
        id: "pagina-graficos-frequencia",
        titulo: "Gráficos de frequência",
        aliases: ["evolução dos intervalos", "curva de distribuição", "ocorrências em ordem crescente"],
        estado: "confirmado",
        resumo: "Amplia a análise histórica de uma dezena, evento e período escolhidos na Frequência.",
        blocos: [
          {
            titulo: "Seleção recebida",
            paragrafos: ["A página recebe Dezena, Evento, Concurso inicial e Concurso final da Frequência. Alterar os campos e usar Consultar gráficos refaz a consulta sem alterar a geração gravada."],
          },
          {
            titulo: "Evolução histórica",
            paragrafos: ["O gráfico principal mostra intervalos individuais em patamares, média histórica e os limites de um desvio-padrão. O eixo horizontal usa concursos; o vertical usa intervalos em concursos."],
          },
          {
            titulo: "Gráficos auxiliares",
            itens: [
              "Curva de distribuição compara a distribuição real dos intervalos com uma curva normal ilustrativa.",
              "Ocorrências em ordem crescente organiza os intervalos e suas posições percentuais, preservando repetições.",
              "Os gráficos possuem unidades e escalas próprias; não se deve comparar alturas como se compartilhassem o mesmo eixo.",
            ],
          },
          {
            titulo: "Retorno",
            paragrafos: ["Voltar para Frequência das dezenas preserva os filtros no endereço e retorna ao bloco histórico de origem."],
          },
        ],
        relacionados: ["pagina-frequencia-dezenas", "conceito-media-desvio"],
      },
      {
        id: "pagina-graficos-frequencia-evolucao",
        titulo: "Evolução dos intervalos",
        aliases: ["patamares", "intervalos individuais", "losango"],
        estado: "confirmado",
        resumo: "Mostra como os intervalos e suas estatísticas acumuladas evoluíram ao longo dos concursos.",
        blocos: [
          { titulo: "Como ler", itens: ["Eixo horizontal: número do concurso.", "Eixo vertical: duração do intervalo em concursos.", "A linha em patamares representa intervalos consecutivos; média e desvio-padrão são referências acumuladas."] },
          { titulo: "Consulta", paragrafos: ["Passe o mouse, use o teclado ou selecione um marcador para consultar os concursos inicial e final e a duração exata. O losango identifica um intervalo estreito demais para leitura direta na escala."] },
          { titulo: "Cuidado", paragrafos: ["O gráfico descreve o histórico e não garante quando acontecerá a próxima ocorrência."] },
        ],
        relacionados: ["pagina-graficos-frequencia", "conceito-media-desvio"],
      },
      {
        id: "pagina-graficos-frequencia-distribuicao",
        titulo: "Curva de distribuição dos intervalos",
        aliases: ["distribuição observada", "curva normal teórica"],
        estado: "confirmado",
        resumo: "Mostra com que frequência cada duração de intervalo ocorreu.",
        blocos: [
          { titulo: "Como ler", itens: ["Eixo horizontal: duração do intervalo em concursos.", "Eixo vertical: percentual das ocorrências com aquela duração.", "A distribuição observada é real; a curva normal é apenas uma referência teórica com a mesma média e o mesmo desvio-padrão."] },
          { titulo: "Consulta", paragrafos: ["Selecione um ponto para consultar duração, quantidade de ocorrências e percentual exato."] },
          { titulo: "Cuidado", paragrafos: ["A distribuição histórica pode ser assimétrica e não precisa acompanhar a curva normal. Ela não garante a próxima ocorrência."] },
        ],
        relacionados: ["pagina-graficos-frequencia", "conceito-media-desvio"],
      },
      {
        id: "pagina-graficos-frequencia-ordenado",
        titulo: "Ocorrências em ordem crescente",
        aliases: ["percentual acumulado", "patamares", "saltos"],
        estado: "confirmado",
        resumo: "Ordena os intervalos do menor para o maior, preservando todas as repetições.",
        blocos: [
          { titulo: "Como ler", itens: ["Eixo horizontal: percentual acumulado das ocorrências ordenadas.", "Eixo vertical: duração como percentual do maior intervalo.", "Repetições formam patamares; saltos indicam durações intermediárias que podem não ter ocorrido."] },
          { titulo: "Consulta", paragrafos: ["Selecione um ponto para ver ordem, percentual acumulado, duração em concursos e percentual do maior intervalo. O último ponto é sempre 100% por 100%."] },
          { titulo: "Cuidado", paragrafos: ["O gráfico descreve concentração e dispersão históricas; não classifica dezenas nem garante maior probabilidade futura."] },
        ],
        relacionados: ["pagina-graficos-frequencia", "conceito-media-desvio"],
      },
      {
        id: "pagina-selecao-dezenas",
        titulo: "Seleção de dezenas",
        aliases: ["configuração", "Backtest", "registro do screener", "formação de jogos", "k", "j"],
        estado: "limitacao",
        resumo: "Seleciona dezenas candidatas, compara configurações e preserva listas para o próximo concurso.",
        blocos: [
          {
            titulo: "Passo a Passo da Seleção de Dezenas",
            itens: [
              "1. Selecionar ou criar uma configuração: neste bloco você poderá selecionar uma configuração anteriormente salva ou criar uma nova. As configurações alteram os critérios utilizados para selecionar as dezenas e podem produzir conjuntos diferentes. Se uma configuração apresentar um resultado de seu interesse, como uma lista mais resumida de dezenas, ela poderá ser salva e reutilizada posteriormente.",
              "2. Selecionar Dezenas: clique em Selecionar dezenas para verificar o resultado produzido sem gravar dados. O sistema apresentará mensagem informando o último concurso utilizado, o próximo concurso previsto, as dezenas selecionadas e a quantidade de combinações de seis dezenas que poderá ser formada. Essa análise é momentânea.",
              "3. Avaliar as dezenas apresentadas: examine a quantidade e a relação de dezenas retornadas. Se o conjunto estiver muito amplo, muito reduzido ou diferente do desejado, altere os parâmetros da configuração e selecione novamente.",
              "4. Salvar a configuração: quando encontrar parâmetros que produzam resultados de seu interesse, utilize Salvar configuração. A configuração será preservada para reutilização. Salvar a configuração não registra uma previsão e não executa o Screener de combinações.",
              "5. Registrar a previsão: selecione uma configuração salva e clique em Registrar previsão do concurso. Não é obrigatório clicar antes em Selecionar dezenas, pois o sistema recalcula automaticamente a seleção e abre uma janela para conferência antes da gravação. Ao confirmar, as dezenas ficam preservadas para o concurso indicado. Se a previsão da mesma configuração, para o mesmo concurso e com a mesma base de resultados já estiver registrada, o sistema mantém o registro original sem alterar nem duplicar dados. Configurações diferentes podem manter previsões separadas, mesmo quando produzem as mesmas dezenas.",
              "6. Localizar a previsão na tabela: as previsões da configuração selecionada aparecem em Registros do screener de dezenas. A tabela informa o concurso previsto, o concurso utilizado como referência, a situação, as dezenas registradas e a quantidade total. Use Atualizar tabela quando desejar recarregar os registros.",
              "7. Escolher um conjunto de dezenas para formar os jogos: na coluna Próxima ação, clique em Formar jogos. As dezenas da previsão escolhida serão enviadas ao bloco Formação de jogos com as dezenas registradas. Nenhuma combinação será processada nesse momento.",
              "8. Informar a quantidade máxima e o valor: digite o número máximo de jogos aprovados que deseja obter e o valor unitário de uma aposta. O sistema apresentará o valor máximo previsto. A quantidade informada funciona como um teto, não como uma quantidade garantida: ao solicitar 100 jogos, por exemplo, o Screener poderá retornar somente 55 se apenas 55 combinações forem aprovadas pelos filtros.",
              "9. Solicitar as combinações aprovadas: clique em Combinações aprovadas. Se faltarem as dezenas de origem, o número máximo de jogos ou o valor unitário, uma janela informará cada item pendente para que seja corrigido. Quando todos os dados estiverem preenchidos, o sistema abrirá a conferência final com o concurso, as dezenas utilizadas, a quantidade bruta de combinações, o limite de jogos e o valor máximo previsto. Nenhuma combinação será processada antes da confirmação do usuário.",
              "10. Iniciar o Screener: na janela de confirmação, clique em Confirmar e iniciar Screener. O sistema formará as combinações de seis dezenas e aplicará sequencialmente os filtros estatísticos, geométricos e de padrões. Uma combinação reprovada será descartada; uma combinação aprovada continuará até o resultado final.",
              "11. Interpretar as combinações aprovadas: ao final, a página apresentará o universo bruto, a quantidade examinada, as exclusões e as combinações aprovadas. O número máximo informado limita a quantidade procurada, mas não obriga o sistema a completar esse total com combinações reprovadas. Se o limite for atingido, o processamento poderá terminar antes de examinar todo o universo. Se houver menos aprovadas — como 55 para um máximo solicitado de 100 — somente as 55 serão apresentadas. Se nenhuma combinação passar por todos os filtros, a lista ficará vazia.",
            ],
          },
          {
            titulo: "Configuração da pesquisa",
            itens: [
              "Configuração gravada escolhe uma configuração imutável ou Nova configuração.",
              "Nome identifica uma nova configuração e deve ser exclusivo.",
              "Fator k controla a meia largura; Fator j desloca a faixa.",
              "Quantidade MAX retorna todas as aprovadas; FIXA retorna no máximo o número informado, sem completar com reprovadas.",
              "Versão do cálculo identifica o algoritmo aplicado.",
            ],
          },
          {
            titulo: "Selecionar dezenas e salvar",
            paragrafos: ["Selecionar dezenas calcula os dados analíticos usando o último concurso cadastrado, mas não grava configuração, seleção ou Backtest. Salvar configuração abre uma conferência; somente Confirmar e salvar cria o registro. Configurações salvas ficam protegidas contra alteração."],
          },
          {
            titulo: "Registros do screener de dezenas",
            paragrafos: ["Registrar previsão do próximo concurso usa a configuração salva selecionada, recalcula automaticamente as dezenas para o concurso imediatamente seguinte e abre uma janela de conferência. Não é necessário executar antes o botão Selecionar dezenas. Confirmar e registrar seleção preserva dezenas, faixas, ranking, corte e configuração antes do sorteio. Se já existir uma previsão da mesma configuração, para o mesmo concurso e calculada com a mesma base de resultados, o registro original será mantido sem alterações ou duplicação. Configurações diferentes podem ter previsões próprias, ainda que retornem o mesmo conjunto de dezenas."],
          },
          {
            titulo: "Conferência posterior",
            paragrafos: ["Quando o resultado do alvo entra no banco, a seleção original é conferida sem ser recalculada. A tabela mostra concurso previsto, dados utilizados até, estado, dezenas, total, configuração e próxima ação."],
          },
          {
            titulo: "Backtest",
            paragrafos: ["Escolha uma configuração salva e um Concurso inicial a partir de 500. Gerar relatório gráfico primeiro abre a conferência; Confirmar e gerar relatório calcula até o último concurso cadastrado. O relatório mostra tamanho da seleção e acertos de 0 a 6, mas não fica gravado."],
          },
          {
            titulo: "Formação de jogos",
            paragrafos: ["Formar jogos em uma seleção registrada carrega concurso, configuração e dezenas preservadas. Número máximo de jogos é um teto, não uma quantidade garantida; o Screener pode retornar menos jogos quando menos combinações forem aprovadas. Valor de um jogo é o preço unitário. Combinações aprovadas verifica os dados: quando houver campos pendentes, uma janela indicará o que precisa ser corrigido; quando estiver tudo pronto, será aberta a conferência final. O processamento somente começa quando o usuário confirma Iniciar Screener na janela seguinte."],
          },
          {
            titulo: "Limitação atual",
            paragrafos: ["Confirmar e iniciar Screener fica disponível depois da conferência dos jogos. A execução aplica os filtros às combinações e apresenta as aprovadas; volumes acima do limite seguro são bloqueados antes do processamento."],
          },
          {
            titulo: "Sequência recomendada",
            paragrafos: ["Atualize os resultados, selecione dezenas com uma configuração, salve-a, compare-a no Backtest e só então registre a seleção do próximo concurso. Depois do sorteio, importe o resultado para conferir o registro original."],
          },
        ],
        relacionados: ["conceito-faixa-k-j", "conceito-backtest", "conceito-registro-selecao", "referencia-persistencia"],
      },
      {
        id: "pagina-gestao-desenvolvimento",
        titulo: "Gestão do desenvolvimento",
        aliases: ["registro", "ideia", "problema", "erro", "arquivar", "PythonAnywhere"],
        estado: "confirmado",
        resumo: "Registra problemas, modificações e novas funcionalidades para acompanhamento do desenvolvimento.",
        blocos: [
          {
            titulo: "Localizar e filtrar",
            paragrafos: ["Localizar oferece os títulos existentes e aceita parte do texto. Tipo, Trabalho e Publicação podem ser combinados. Consultar arquivados troca a lista ativa pela arquivada. A ordem é a de criação."],
          },
          {
            titulo: "Criar um registro",
            paragrafos: ["Use Novo registro, escolha Tipo, informe Título, Data, Situação do trabalho, Situação da publicação, Página relacionada, Descrição e, quando necessário, Observação da publicação. Salvar registro abre confirmação; a validação dos campos obrigatórios ocorre antes da chamada de criação."],
          },
          {
            titulo: "Consultar e editar",
            paragrafos: ["Selecionar uma linha abre o registro protegido para consulta. Editar habilita mudanças controladas. Cancelar preserva o registro original e pede decisão quando há alterações ainda não salvas."],
          },
          {
            titulo: "Trabalho e publicação",
            paragrafos: ["A situação do trabalho acompanha a execução local. A situação da publicação informa separadamente se a mudança está disponível no PythonAnywhere. Concluir o trabalho não significa publicá-lo."],
          },
          {
            titulo: "Arquivamento",
            paragrafos: ["Arquivar retira o registro da lista ativa sem apagá-lo. Consultar arquivados permite localizá-lo e desarquivá-lo. As alterações preservam histórico e usam a versão lida para evitar sobrescrita concorrente."],
          },
          {
            titulo: "Autorização",
            paragrafos: ["Registrar uma ideia ou problema não autoriza sua implementação. O trabalho continua sujeito ao planejamento e à autorização da etapa correspondente."],
          },
        ],
        relacionados: ["pagina-ajuda", "referencia-persistencia"],
      },
      {
        id: "pagina-ajuda",
        titulo: "Ajuda",
        aliases: ["busca", "tópicos", "link direto", "assunto"],
        estado: "confirmado",
        resumo: "Consulta central dos conceitos, páginas e referências funcionais do Game.",
        blocos: [
          {
            titulo: "Índice lateral",
            paragrafos: ["Os assuntos estão separados em Começar aqui, Conceitos gerais, Ajuda por página e Referência funcional. Escolher um título abre somente o assunto correspondente na área de leitura."],
          },
          {
            titulo: "Localizar assunto",
            paragrafos: ["Digite uma palavra ou expressão. A busca considera títulos, nomes alternativos e conteúdo sem diferenciar maiúsculas ou acentos. Limpar restaura o índice completo; Esc também limpa uma pesquisa ativa."],
          },
          {
            titulo: "Links e retomada",
            paragrafos: ["O endereço contém o identificador do tópico aberto e pode ser guardado. Sem um tópico no endereço, a página retoma o último assunto consultado neste navegador. Um identificador desconhecido abre o início com um aviso."],
          },
          {
            titulo: "Estados do conteúdo",
            paragrafos: ["Limitação conhecida identifica uma função existente com restrição relevante. Em desenvolvimento identifica conteúdo ou recurso ainda incompleto. A ausência do aviso indica funcionamento conferido para a versão atual."],
          },
        ],
        relacionados: ["inicio-localizar-assunto", "referencia-bloqueios"],
      },
    ],
  },
  {
    id: "referencias",
    titulo: "Referência funcional",
    topicos: [
      {
        id: "referencia-linha-tempo",
        titulo: "Linha do tempo dos cálculos",
        aliases: ["concurso 1", "concurso 500", "início"],
        estado: "confirmado",
        resumo: "Resultados, fotografias e alvos possuem marcos iniciais diferentes.",
        blocos: [
          {
            titulo: "Marcos confirmados",
            itens: [
              "Concurso 1: início da série de resultados cadastrados.",
              "Concursos 1 a 499: base conhecida para formar a primeira seleção histórica testável.",
              "Concurso 500: primeira fotografia acumulada da Frequência.",
              "Concurso 500: primeiro alvo permitido no Backtest da Seleção, calculado com corte 499.",
              "Depois do 500: cada fotografia da Frequência avança o corte em um concurso; cada alvo do Backtest usa seu próprio corte C − 1.",
            ],
          },
          {
            titulo: "Por que não começam todos no 1",
            paragrafos: ["A série começa no 1, mas os estudos precisam de uma base anterior para formar intervalos e estatísticas. O concurso 500 é o primeiro corte ou alvo escolhido para essas avaliações; ele não apaga nem ignora os concursos anteriores usados no cálculo."],
          },
        ],
        relacionados: ["conceito-corte-historico", "conceito-backtest"],
      },
      {
        id: "referencia-persistencia",
        titulo: "O que fica gravado",
        aliases: ["banco", "persistência", "consulta"],
        estado: "confirmado",
        resumo: "O sistema separa dados básicos preservados, estados históricos e relatórios recalculáveis.",
        blocos: [
          {
            titulo: "Resultados e classificações",
            paragrafos: ["Resultados, cálculos derivados de cada resultado, análises geométricas e ocorrências reais de padrões ficam gravados. A importação ou edição autorizada atualiza essa base e invalida resumos que deixarem de corresponder a ela."],
          },
          {
            titulo: "Validação e perfis",
            paragrafos: ["Amostras, critérios, referências esperadas, valores calculados, assinaturas, aprovações, perfis operacionais e o estado global do algoritmo são preservados para auditoria e proteção do Screener."],
          },
          {
            titulo: "Frequência",
            paragrafos: ["A configuração, as gerações e as fotografias históricas ficam gravadas quando a operação é confirmada com Salvar dados ativo. A simulação calcula o mesmo tipo de informação sem persistir a execução."],
          },
          {
            titulo: "Seleção de dezenas",
            itens: [
              "Configurações salvas permanecem no banco e ficam protegidas contra alteração.",
              "A análise de configuração exibida antes de salvar é momentânea.",
              "A seleção registrada para o próximo concurso fica preservada para conferência posterior.",
              "O relatório do Backtest, suas listas intermediárias e pontos dos gráficos não são gravados.",
              "Jogos somente poderão ser gravados por fluxo próprio, com prévia, autorização e confirmação.",
            ],
          },
          {
            titulo: "Gestão do desenvolvimento",
            paragrafos: ["Registros, alterações de estado, publicação e arquivamento ficam preservados. Arquivar retira da lista ativa, mas não apaga o registro."],
          },
        ],
        relacionados: ["conceito-dados-gravados", "conceito-atualizacao-calculo", "conceito-registro-selecao"],
      },
      {
        id: "referencia-bloqueios",
        titulo: "Mensagens e bloqueios",
        aliases: ["erro", "não foi possível", "travado"],
        estado: "em-desenvolvimento",
        resumo: "Os bloqueios serão organizados por causa e providência possível.",
        blocos: [{
          titulo: "Princípio",
          paragrafos: ["Um bloqueio de segurança não deve ser contornado. A Ajuda deverá informar por que a operação foi impedida e qual etapa de validação ou correção ainda falta."],
        }],
      },
      {
        id: "referencia-quantidades",
        titulo: "Amostra e universo de combinações",
        aliases: ["5000", "5.000", "50.063.860", "C(60,6)"],
        estado: "confirmado",
        resumo: "A amostra de teste e o universo integral têm finalidades e tamanhos diferentes.",
        blocos: [
          {
            titulo: "Universo integral",
            paragrafos: ["As 60 dezenas combinadas seis a seis, sem repetição, formam 50.063.860 combinações."],
            formulas: ["C(60, 6) = 50.063.860"],
          },
          {
            titulo: "Amostra de teste",
            paragrafos: ["As 5.000 primeiras combinações, geradas em ordem determinística pela biblioteca Python, formam uma amostra reproduzível para avaliar o código dos filtros. Elas não são uma estimativa aleatória nem o resultado final do Screener integral."],
          },
          {
            titulo: "Combinações das dezenas selecionadas",
            paragrafos: ["Se a Seleção retornar N dezenas, suas combinações possíveis de seis têm quantidade C(N,6). Esse conjunto é diferente tanto da amostra fixa de 5.000 quanto do universo C(60,6)."],
            formulas: ["combinações possíveis da seleção = C(N, 6)"],
          },
          {
            titulo: "Exemplo",
            paragrafos: ["Uma seleção com 26 dezenas forma C(26,6) = 230.230 combinações antes da aplicação dos filtros do Screener de combinações."],
          },
        ],
        relacionados: ["conceito-screener", "pagina-preparacao-screener"],
      },
    ],
  },
];

export const topicosAjuda = secoesAjuda.flatMap((secao) => (
  secao.topicos.map((topico) => ({ ...topico, secaoId: secao.id, secaoTitulo: secao.titulo }))
));
