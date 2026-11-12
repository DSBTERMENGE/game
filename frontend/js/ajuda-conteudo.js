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
            paragrafos: ["Significa executar o funil no conjunto completo definido pela operação. O processamento integral das 50.063.860 combinações permanece bloqueado enquanto as condições de homologação e cobertura não estiverem liberadas."],
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
        relacionados: ["pagina-validacao-auditoria", "referencia-bloqueios"],
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
        aliases: ["resultados", "importação", "voo dos pássaros", "mancha", "aparência"],
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
        resumo: "Reúne os acessos aos cadastros usados para organizar os padrões.",
        blocos: [
          {
            titulo: "Uso",
            paragrafos: ["A página é um índice. Grupos de padrões abre a organização conceitual; Padrões abre o cadastro das formas classificadas. Entrar nesta visão geral não grava nem altera dados."],
          },
          {
            titulo: "Ordem recomendada",
            paragrafos: ["Cadastre primeiro o grupo e depois o padrão ligado a ele. Um nome e uma descrição não criam por si só uma função Python executável no Screener."],
          },
        ],
        relacionados: ["pagina-grupos-padroes", "pagina-padroes"],
      },
      {
        id: "pagina-grupos-padroes",
        titulo: "Grupos de padrões",
        aliases: ["grupo", "subgrupo", "cadastro de grupos"],
        estado: "confirmado",
        resumo: "Cria e mantém as categorias conceituais às quais os padrões pertencem.",
        blocos: [
          {
            titulo: "Novo grupo",
            paragrafos: ["Preencha Nome e Descrição e use Adicionar. Os dois campos identificam o grupo para o usuário; o código exibido na tabela é controlado pelo sistema."],
          },
          {
            titulo: "Grade e ações",
            paragrafos: ["A grade mostra Código, Nome do grupo, Descrição e Ações. As ações permitem editar ou excluir conforme as proteções do banco. A exclusão pede confirmação e pode ser recusada quando existirem dependências."],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["Adicionar, editar e excluir são operações persistentes no PostgreSQL. Apenas abrir a página ou percorrer a grade não altera registros."],
          },
        ],
        relacionados: ["pagina-cadastros", "pagina-padroes"],
      },
      {
        id: "pagina-padroes",
        titulo: "Padrões",
        aliases: ["subgrupos", "raridade", "perfil de padrões", "função Python"],
        estado: "confirmado",
        resumo: "Cadastra padrões, consulta suas ocorrências históricas e avalia sua raridade.",
        blocos: [
          {
            titulo: "Cadastrar um padrão",
            paragrafos: ["Escolha o Grupo, informe Nome e Descrição e use Adicionar. O grupo é obrigatório porque todo padrão pertence a uma categoria conceitual."],
          },
          {
            titulo: "Filtro e grade",
            paragrafos: ["Filtrar grupo restringe as linhas exibidas. A grade informa código, grupo, nome, descrição, ocorrências, intervalo médio, desvio-padrão, situação da função Python e ações de manutenção."],
          },
          {
            titulo: "Perfil de padrões",
            itens: [
              "Limite % define o teto usado para consultar classes raras.",
              "Corte escolhe o histórico completo ou limita a consulta até um concurso ou uma data.",
              "Atualizar recalcula a consulta do perfil para os filtros informados.",
              "A tabela resume quantidade, porcentagens, intervalos e diagnóstico; consultar o perfil não cria a função do filtro.",
            ],
          },
          {
            titulo: "Limite importante",
            paragrafos: ["Cadastrar nome, descrição e grupo não implementa o critério do Screener. Cada padrão precisa de função Python registrada, testes, homologação e integração. A coluna Função Python mostra essa situação."],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["Inclusões e edições do cadastro são persistentes. O perfil é uma consulta sobre classificações já gravadas; a execução do Screener continua protegida pelas validações próprias."],
          },
        ],
        relacionados: ["conceito-screener", "conceito-validacao", "pagina-preparacao-screener"],
      },
      {
        id: "pagina-distribuicoes",
        titulo: "Distribuições",
        aliases: ["distribuições históricas", "perfis operacionais", "configurar faixas"],
        estado: "confirmado",
        resumo: "Apresenta os perfis estatísticos e geométricos calculados sobre os resultados conhecidos.",
        blocos: [
          {
            titulo: "Gráficos",
            paragrafos: ["A página mostra os dez perfis operacionais: quatro grandezas estatísticas e seis geométricas. Cada gráfico apresenta a distribuição histórica usada para estudar limites de aceitação."],
          },
          {
            titulo: "Atualizar",
            paragrafos: ["Atualizar recarrega do servidor os perfis correspondentes ao histórico completo. O comando não executa o Screener e não significa liberar seus filtros."],
          },
          {
            titulo: "Configurar faixas",
            itens: [
              "Método define como as margens serão interpretadas no estudo.",
              "Margem inferior e Margem superior ajustam cada lado da faixa.",
              "Calcular prévia consulta os perfis e mostra os limites antes de qualquer salvamento local.",
              "Salvar estudo somente fica disponível após uma prévia válida.",
            ],
          },
          {
            titulo: "Onde a configuração fica",
            paragrafos: ["Salvar estudo guarda essa configuração apenas neste navegador. Ela não é uma configuração operacional do PostgreSQL e não ativa o Screener. Cancelar ou fechar descarta a edição aberta."],
          },
        ],
        relacionados: ["conceito-perfil-fotografia", "pagina-preparacao-screener"],
      },
      {
        id: "pagina-preparacao-screener",
        titulo: "Preparação do Screener",
        aliases: ["Screener", "Executar 5000", "Teste do Screener", "Aplicação do Screener", "5.000", "limite de raridade", "amostra protegida"],
        estado: "limitacao",
        resumo: "Testa o funil de filtros nas primeiras 5.000 combinações; a aplicação integral permanece bloqueada.",
        blocos: [
          {
            titulo: "Finalidade atual",
            paragrafos: ["A página permite verificar a integração dos filtros estatísticos, geométricos e de padrões em 5.000 combinações reproduzíveis. Ela ainda não oferece a aplicação integral em 50.063.860 combinações."],
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
            paragrafos: ["Usará o mesmo motor até a última combinação possível. O comando permanece desabilitado enquanto o teste, o acompanhamento do progresso e o cancelamento seguro não forem validados nas etapas próprias."],
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
            titulo: "Bloqueio atual",
            paragrafos: ["Antes do teste, o sistema confere estado global, catálogo, assinaturas, avaliações, perfis e cobertura. Se a Validação e auditoria informar algoritmo desatualizado, assinatura divergente ou cobertura pendente, o comando fica bloqueado. Essa trava impede que filtros ainda não validados produzam um resultado aparentemente válido; não significa que o Screener não encontrou combinações."],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["O Teste do Screener produz um quadro de estudo e não grava as 5.000 combinações como resultados. O limite de raridade salvo no navegador é apenas uma preferência local."],
          },
        ],
        relacionados: ["conceito-screener", "conceito-validacao", "pagina-validacao-auditoria", "referencia-quantidades"],
      },
      {
        id: "pagina-validacao-auditoria",
        titulo: "Validação e auditoria",
        aliases: ["homologação", "cobertura", "esperado", "calculado", "S N pendente"],
        estado: "confirmado",
        resumo: "Confere as funções de produção contra referências independentes e explica por que o Screener pode estar bloqueado.",
        blocos: [
          {
            titulo: "Estado do algoritmo",
            paragrafos: ["O cabeçalho mostra se o conjunto está atualizado e o motivo vigente. Atualizar Validação e auditoria aparece quando há trabalho de sincronização ou execução a realizar."],
          },
          {
            titulo: "Atualização",
            paragrafos: ["O comando inicia uma tarefa acompanhada por progresso real. A sincronização preserva referências válidas, executa as funções atuais e recalcula o estado. Ela não aprova uma divergência automaticamente."],
          },
          {
            titulo: "Resumo e filtros",
            itens: [
              "Categoria separa Estatística, Geometria e Padrão.",
              "Função, Grupo e Subgrupo restringem o critério consultado.",
              "Situação separa aprovada (S), reprovada (N) e pendente.",
              "Aplicar consulta a combinação escolhida; Limpar restaura os filtros.",
            ],
          },
          {
            titulo: "Como ler a grade",
            paragrafos: ["Cada linha relaciona concurso e dezenas da amostra, função ou filtro, referência esperada, valor calculado e decisão S/N. Pendente indica referência ausente, função não executada ou conferência incompleta."],
          },
          {
            titulo: "Relatório e divergências",
            paragrafos: ["O relatório agrupa exigidas, executadas, aprovadas, reprovadas e pendentes por função. Divergências detalham o desacordo para diagnóstico; uma sugestão de causa não altera a referência nem a aprovação."],
          },
          {
            titulo: "Efeito nos dados",
            paragrafos: ["A execução grava calculados, assinaturas executadas, decisões e estado de cobertura. Ela não altera os resultados sorteados nem corrige funções automaticamente."],
          },
        ],
        relacionados: ["conceito-validacao", "pagina-preparacao-screener", "referencia-bloqueios"],
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
            titulo: "Analisar e salvar",
            paragrafos: ["Analisar configuração calcula os dados analíticos usando o último concurso cadastrado, mas não grava configuração, seleção ou Backtest. Salvar configuração abre uma conferência; somente Confirmar e salvar cria o registro. Configurações salvas ficam protegidas contra alteração."],
          },
          {
            titulo: "Registros do screener de dezenas",
            paragrafos: ["Registrar previsão do próximo concurso prepara a lista para o alvo imediatamente seguinte e abre confirmação. Somente uma configuração salva pode originar o registro. Confirmar e registrar seleção preserva dezenas, faixas, ranking, corte e configuração antes do sorteio."],
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
            paragrafos: ["Formar jogos em uma seleção registrada carrega concurso, configuração e dezenas preservadas. Número máximo de jogos é um teto; Valor de um jogo é o preço unitário. Conferir configuração calcula o valor máximo e apenas revisa os dados."],
          },
          {
            titulo: "Limitação atual",
            paragrafos: ["Confirmar e iniciar Screener permanece desabilitado até a integração do Screener de combinações. Nesta fase, a conferência não gera combinações, não aplica filtros e não grava jogos."],
          },
          {
            titulo: "Sequência recomendada",
            paragrafos: ["Atualize os resultados, analise uma configuração, salve-a, compare-a no Backtest e só então registre a seleção do próximo concurso. Depois do sorteio, importe o resultado para conferir o registro original."],
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
