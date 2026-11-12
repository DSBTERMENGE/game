# Contrato editorial da Ajuda central

Versão editorial: 1.0
Definida na subetapa 28.2 em 11/11/2026.

## 1. Finalidade

A Ajuda central deverá explicar o Game em linguagem operacional e servir como
fonte rápida de consulta para o usuário, o desenvolvimento e a IA. Ela não
substitui código, testes ou contratos técnicos como prova do comportamento;
transforma o funcionamento comprovado nessas fontes em explicação humana.

Este contrato define a organização, o vocabulário e o formato do conteúdo. A
página, a busca e os links serão implementados somente em subetapa posterior.

## 2. Princípios editoriais

1. Começar pela finalidade e pela ação possível, não pela implementação.
2. Definir um termo antes de usá-lo como parte de outra explicação.
3. Separar assuntos extensos em subtópicos curtos e diretamente acessíveis.
4. Informar claramente quando uma ação grava, altera ou apenas consulta dados.
5. Explicar bloqueios pela causa e pela próxima ação possível.
6. Não apresentar hipótese, lembrança ou recurso planejado como funcionamento
   atual.
7. Usar exemplos numéricos pequenos quando eles reduzirem a ambiguidade.
8. Usar fórmulas, gráficos e desenhos somente quando ajudarem materialmente a
   entender uma relação.
9. Não expor nomes de classes, funções, tabelas ou códigos internos ao usuário,
   salvo em uma referência técnica explicitamente identificada.
10. Manter uma única explicação principal por conceito e usar links internos
    nas demais páginas, evitando cópias divergentes.

## 3. Árvore da Ajuda

### 3.1 Começar aqui

- **O que é o Game**
- **Caminho normal de utilização**
- **O que o sistema calcula e o que ele não promete**
- **Como verificar se os resultados estão atualizados**
- **Como localizar um assunto nesta Ajuda**

### 3.2 Conceitos gerais

- **Concursos e resultados**
  - concurso cadastrado;
  - último concurso cadastrado;
  - concurso-alvo;
  - corte histórico.
- **Dezenas, intervalos e distribuições**
  - ocorrência e intervalo;
  - média e desvio-padrão;
  - limites históricos e faixa ajustada;
  - fatores `k` e `j`.
- **Configurações e estudos**
  - configuração;
  - assinatura;
  - imutabilidade;
  - análise, estudo e Backtest.
- **Screener e combinações**
  - preparação do Screener;
  - teste com amostra;
  - aplicação do Screener;
  - universo de combinações;
  - combinações das dezenas selecionadas.
- **Validação do sistema**
  - validação;
  - homologação;
  - cobertura;
  - bloqueio de segurança.
- **Dados e atualização**
  - informação momentânea;
  - informação gravada;
  - cálculo integral;
  - atualização incremental.

### 3.3 Ajuda por página

Os tópicos seguirão a ordem funcional do menu:

1. **Painel**
2. **Cadastros**
   - Grupos e subgrupos;
   - Padrões.
3. **Distribuições**
4. **Preparação do Screener**
5. **Validação e auditoria**
6. **Frequência das dezenas**
   - página principal;
   - gráficos de frequência.
7. **Seleção de dezenas**
8. **Gestão do desenvolvimento**
9. **Ajuda**

`Preparação do Screener` é o título editorial adotado para o assunto. Enquanto
a interface ainda exibir apenas `Screener`, os dois nomes deverão localizar o
mesmo tópico. A eventual alteração do texto do menu é funcional e depende de
autorização própria.

`Seleção de dezenas` permanece como título vigente. Se o módulo for dividido
ou renomeado quando a formação de jogos estiver completa, a árvore e os links
antigos deverão ser preservados por aliases.

### 3.4 Referência funcional

- **Linha do tempo dos cálculos**
- **O que é gravado e o que é apenas consultado**
- **Estados e situações exibidos pelo sistema**
- **Mensagens, bloqueios e providências**
- **Fórmulas utilizadas**
- **Limites e quantidades importantes**
- **Glossário**
- **Funcionalidades em desenvolvimento**

## 4. Vocabulário oficial inicial

| Termo | Uso editorial |
| --- | --- |
| Concurso | Identificador sequencial de um sorteio. Não usar como sinônimo de resultado. |
| Resultado | Conjunto de dezenas efetivamente sorteadas em um concurso. |
| Último concurso cadastrado | Maior concurso existente no banco consultado. Pode estar atrasado em relação à operadora. |
| Concurso-alvo | Concurso que está sendo analisado. Na análise do próximo concurso, é o imediatamente posterior ao último cadastrado. |
| Corte histórico | Último concurso cujos dados podem participar de determinado cálculo. Para avaliar o alvo `C`, o corte é, em regra documentada no módulo, `C - 1`. |
| Fotografia | Estado calculado e preservado para um concurso de corte específico. Não é imagem gráfica. Na primeira ocorrência, escrever “fotografia dos cálculos”. |
| Configuração | Conjunto identificado de parâmetros usados por um cálculo ou estudo. |
| Assinatura | Identificador técnico que permite verificar se uma configuração preservada continua íntegra. Não a apresentar como dado que o usuário precise inventar. |
| Backtest | Estudo que reaplica uma configuração em concursos já conhecidos, usando em cada alvo apenas a base histórica permitida para aquele momento. |
| Screener | Conjunto encadeado de filtros; uma combinação só é aprovada se passar pelos filtros exigidos. |
| Preparação do Screener | Área onde critérios, referências e funcionamento do Screener são estudados e validados. |
| Teste do Screener | Aplicação voltada à verificação dos filtros em uma amostra controlada, atualmente associada às 5.000 primeiras combinações quando esse fluxo estiver operacional. |
| Aplicação do Screener | Aplicação dos filtros ao conjunto completo definido para a operação. Não confundir com o teste em amostra. |
| Validação | Conferência de um resultado calculado contra regras ou referências esperadas. |
| Homologação | Aprovação formal de que uma função ou critério produz o comportamento esperado na versão conferida. |
| Cobertura | Comprovação de que os casos exigidos foram exercitados e conferidos. |
| Persistido ou gravado | Dado armazenado no PostgreSQL e disponível após encerrar a consulta. |
| Momentâneo | Resultado calculado para exibição e não preservado como registro funcional. Evitar “temporário” quando não houver outro processo persistente a distinguir. |
| Atualização incremental | Processamento apenas da parte nova, apoiado em estado anterior válido. Não usar esse termo sem confirmação específica do módulo. |

Sinônimos, abreviações e nomes antigos deverão constar como palavras de busca,
mas o texto principal usará o termo oficial. Exemplos: `CA` para
concurso-alvo, `DP` para desvio-padrão e `Screener` para Preparação do Screener.

## 5. Modelo obrigatório de um tópico de página

Cada página será descrita, quando aplicável, nesta ordem:

1. **Finalidade** — para que serve e quando usar.
2. **Antes de começar** — dados ou configurações necessários.
3. **Campos** — significado, origem, valor padrão, limites e obrigatoriedade.
4. **Comandos** — efeito de cada botão e se exige confirmação.
5. **Resultados apresentados** — como ler tabelas, resumos e gráficos.
6. **Efeito nos dados** — o que apenas consulta, o que grava e o que pode ser
   alterado depois.
7. **Mensagens e bloqueios** — causa em linguagem comum e providência possível.
8. **Sequência de uso** — passos curtos do fluxo normal.
9. **Exemplo** — somente quando esclarecer o comportamento.
10. **Assuntos relacionados** — links para conceitos e outras páginas.

Uma seção inaplicável deverá ser omitida; não serão criados títulos vazios.

## 6. Modelo dos demais tópicos

Um conceito geral deverá conter:

- definição curta;
- importância no sistema;
- exemplo ou relação com outros conceitos, quando necessário;
- páginas em que aparece;
- fonte funcional conferida, registrada nos metadados editoriais e não
  necessariamente exibida ao usuário.

Uma referência funcional deverá privilegiar tabelas pequenas, mapas de estado
ou linhas do tempo quando essas formas forem mais claras que parágrafos.

## 7. Estados editoriais

O conteúdo poderá usar somente estas classificações:

- **Funcionamento confirmado:** comportamento conferido no sistema atual. É o
  estado normal e não precisa aparecer como aviso em todos os parágrafos.
- **Limitação conhecida:** função existente com restrição que afeta o uso. O
  texto deverá dizer a consequência e a alternativa disponível.
- **Em desenvolvimento:** recurso ainda não disponível para operação completa.
  O texto deverá separar o que já funciona do que falta.

Contradições não serão publicadas como duas alternativas. Elas deverão ser
registradas na Gestão do desenvolvimento e resolvidas ou explicitamente
classificadas antes da publicação do tópico.

## 8. Títulos, leitura e linguagem

- Títulos de primeiro nível: no máximo seis palavras sempre que possível.
- Subtítulos: uma pergunta ou ação objetiva, sem repetir o título principal.
- Parágrafos: uma ideia principal e linguagem direta.
- Botões e campos: reproduzir exatamente o texto vigente na interface.
- Números: usar o padrão visual em português, como `5.000` e `50.063.860`.
- Fórmulas: definir cada símbolo imediatamente antes ou depois da expressão.
- Siglas: escrever o nome completo na primeira ocorrência de cada tópico.
- Evitar “simplesmente”, “obviamente”, “normalmente” e mensagens que atribuam
  erro ao usuário sem explicar a causa.
- Não usar “previsão” para um registro ou estudo quando o termo puder sugerir
  garantia de resultado; explicar o sentido estatístico quando seu uso for
  indispensável.

## 9. Identificadores e links internos

Cada tópico e subtópico terá um identificador estável, sem acentos, baseado no
assunto e não na posição visual. Padrões reservados:

- `inicio-*` para Começar aqui;
- `conceito-*` para Conceitos gerais;
- `pagina-*` para Ajuda por página;
- `referencia-*` para Referência funcional.

Exemplos: `conceito-corte-historico`, `pagina-preparacao-screener` e
`pagina-selecao-dezenas-backtest`.

Uma alteração de título não deverá quebrar o identificador existente. Nomes
antigos poderão permanecer como aliases de busca e de link. O mecanismo de URL
será definido e testado na implementação da página, preservando esses IDs.

## 10. Relação entre alteração funcional e Ajuda

Toda etapa que alterar comportamento visível deverá declarar no plano:

- tópicos da Ajuda afetados;
- termos, campos, comandos, mensagens ou efeitos nos dados que mudaram;
- fontes técnicas usadas para conferir o novo texto;
- teste que garante a correspondência entre interface e Ajuda.

A alteração funcional não será considerada encerrada enquanto esses tópicos
não estiverem atualizados. Mudança ainda não implantada ficará apenas em
`Funcionalidades em desenvolvimento` e não será descrita como disponível.

## 11. Metadados editoriais internos

O conteúdo deverá permitir registrar, sem poluir a leitura do usuário:

- identificador estável;
- título e aliases;
- seção e ordem;
- páginas relacionadas;
- estado editorial;
- data da última conferência;
- fontes técnicas conferidas;
- versão funcional ou etapa responsável.

O formato técnico desses metadados será escolhido na Etapa 28.3. O conteúdo
deverá ficar separado da marcação visual para evitar duplicação em HTML e
JavaScript.

## 12. Situação após a Etapa 28

A página central, o item final do menu, a pesquisa, os links diretos e os
acessos contextuais foram implantados e validados. Os antigos conteúdos locais
duplicados foram removidos. `frontend/js/ajuda-conteudo.js` é a fonte editorial
oficial do Game.

Uma etapa futura que alterar interface, fluxo, cálculo, persistência, mensagem
ou limitação visível somente poderá ser encerrada depois de atualizar os
tópicos afetados e validar a correspondência entre sistema e Ajuda.
