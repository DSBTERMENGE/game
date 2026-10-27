# Funcionamento planejado do programa

## Objetivo analítico

O sistema tratará cada resultado como uma observação composta por seis valores.
Para raciocinar sobre os padrões, esses valores podem ser imaginados como
temperaturas medidas em seis pontos de um corpo. O interesse do projeto está na
identificação e representação de padrões, e não apenas na listagem dos dados.

## Formas de entrada

Os dados poderão entrar de duas maneiras:

1. importação de várias linhas de uma planilha Excel;
2. inclusão ou edição individual pela interface.

As duas formas deverão chamar exatamente as mesmas funções de validação e
cálculo. Não haverá uma fórmula exclusiva da planilha e outra para o formulário.

A API de inclusão e edição individual já usa esse fluxo comum nas rotas
`POST /api/resultados` e `PUT /api/resultados/<numero_ap>`. Os campos derivados
nunca são aceitos como fonte: são recalculados pelo servidor antes da gravação.

## Processamento de uma linha

Para cada linha, o programa deverá:

1. receber data, número da apresentação e seis resultados;
2. validar os campos de entrada;
3. calcular soma, média aritmética, mediana e desvio-padrão em relação à média;
4. gravar valores originais e calculados na mesma transação;
5. se a linha estiver sendo editada, substituir os cálculos anteriores pelos
   valores recalculados;
6. confirmar a operação somente se todas as etapas terminarem corretamente.

Na importação do Excel, esse fluxo será executado em laço para cada linha. No
formulário, será executado quando o usuário clicar em Salvar.

Uma planilha atualizada poderá substituir a anterior. O importador usará o
número da apresentação/concurso para inserir somente linhas novas, ignorar as
idênticas e separar divergências para conferência, sem criar duplicações.

A leitura e a comparação em memória já foram implementadas e testadas. A fonte
inicial contém 3.069 concursos válidos, de 1 a 3069, sem linhas inválidas. A
gravação desses dados depende das etapas de persistência PostgreSQL e ainda não
deve ser considerada concluída.

## Painel de comandos

A interface possui controles para:

- selecionar uma planilha Excel;
- solicitar importação, cálculos e armazenamento pela API Python;
- selecionar diretamente um resultado carregado;
- navegar para o resultado anterior ou seguinte;
- configurar o tempo de apresentação;
- iniciar ou pausar o voo dos pássaros;
- desenhar a mancha acumulada;
- limpar o gráfico.

A navegação individual é circular quando existem dois ou mais resultados.
Com apenas um, os botões Anterior, Próximo e Voo permanecem desabilitados; com
zero, também ficam desabilitados o seletor e a mancha. O painel informa de forma
explícita quando nenhum resultado foi carregado e a quantidade carregada nos
demais casos.

O frontend usa `POST /api/resultados/importar` para enviar o Excel e
`GET /api/resultados` para carregar a série. As duas rotas estão implementadas.
A importação aceita somente `.xlsx`, limita o envio a 10 MiB, usa arquivo
temporário descartável e devolve o relatório incremental em JSON.
Depois de recarregar os resultados, a interface preserva o resumo com as
quantidades inseridas, iguais, alteradas e inválidas. O fluxo completo foi
validado num database PostgreSQL efêmero: uma segunda importação da mesma fonte
não criou duplicidades.

## Funções de cálculo por linha

- soma dos seis resultados;
- média aritmética dos seis resultados;
- mediana dos seis resultados;
- desvio-padrão dos seis resultados em relação à média.

A definição exata do desvio-padrão, populacional ou amostral, ainda precisa ser
confirmada. Até essa decisão, nenhuma fórmula definitiva deverá ser codificada.

## Estatísticas de ocorrência

Para cada número inteiro de 01 a 60, o programa deverá obter:

- frequência: quantidade total de ocorrências;
- sequência dos intervalos entre ocorrências;
- intervalo médio entre ocorrências;
- desvio-padrão dos intervalos.

Essas funções deverão aceitar, quando a funcionalidade exigir, todo o histórico
ou um período selecionado. A ordem temporal deverá ser definida por data e pelo
número da apresentação, com regra explícita para eventual empate.

## Cálculos da linha e cálculos históricos

Soma, média, mediana e desvio-padrão pertencem a uma única linha e serão
armazenados com ela.

Frequências, intervalos, médias móveis e outros cálculos históricos dependem de
várias linhas. Inicialmente, serão produzidos quando a consulta ou o gráfico for
solicitado. Se futuramente forem armazenados, qualquer inclusão ou alteração
antiga deverá recalcular todas as posições históricas afetadas.

## Gráfico de um resultado

A interface possui uma grade de números de 01 a 60. Para apresentar um único
resultado:

- cada número ocorrido receberá um círculo sobreposto;
- a cor inicial será verde-claro;
- a marca deverá permitir que o número continue legível;
- tamanho, opacidade, borda e cor deverão ficar configuráveis no código visual;
- a média espacial também será marcada na escala, sem arredondamento para o
  centro de uma dezena.

### Coordenadas da matriz

O centro da dezena `01` é a origem `(0; 0)`. Cada avanço até o centro da célula
seguinte acrescenta uma unidade no eixo correspondente. O eixo horizontal
cresce para a direita e o vertical cresce para baixo.

```text
01 = (0; 0)     10 = (9; 0)
11 = (0; 1)     20 = (9; 1)
21 = (0; 2)     30 = (9; 2)
31 = (0; 3)     40 = (9; 3)
41 = (0; 4)     50 = (9; 4)
51 = (0; 5)     60 = (9; 5)
```

Para uma dezena inteira `n` entre 1 e 60:

```text
x = (n - 1) módulo 10
y = parte inteira de ((n - 1) / 10)
```

Para um resultado com seis dezenas, a coordenada média será o centro geométrico
dos seis pontos:

```text
media_x = (x1 + x2 + x3 + x4 + x5 + x6) / 6
media_y = (y1 + y2 + y3 + y4 + y5 + y6) / 6
```

As coordenadas normalmente serão decimais. Um ponto como `(2; 4,33)` deverá ser
desenhado exatamente entre os centros das células, e não arredondado para uma
dezena. No banco e nos cálculos será utilizado ponto decimal; a interface poderá
apresentar vírgula conforme o idioma.

Para converter a coordenada lógica em posição na tela, o JavaScript medirá o
centro real de `01`, a distância horizontal entre centros consecutivos e a
distância vertical entre linhas:

```text
pixel_x = centro_01_x + media_x * passo_horizontal
pixel_y = centro_01_y + media_y * passo_vertical
```

Assim, a posição continuará correta se o tamanho das células ou o espaço entre
elas mudar no CSS.

Essa geometria foi validada automaticamente para os quatro cantos da matriz,
uma média inteira e o ponto decimal `(2; 4,33)`. Ao redimensionar a janela, a
camada SVG e todas as marcas do resultado selecionado são recalculadas a partir
dos novos centros. A marca verde usa transparência e não captura eventos do
mouse, mantendo os números legíveis e os controles acessíveis.

### Modos de apresentação

- `animação`: mostrar as seis dezenas e a média espacial de um resultado,
  aguardar 0,5 segundo, limpar as marcas e avançar para o próximo;
- `mancha`: avançar pelos resultados sem apagar as marcas anteriores, formando
  uma composição acumulada.

No voo, o intervalo pode variar entre 0,1 e 30 segundos e uma alteração passa a
valer no passo seguinte. A pausa cancela o único temporizador ativo. O avanço é
circular e, se a janela for redimensionada durante a animação, o resultado atual
é redesenhado imediatamente sem interromper nem duplicar o temporizador.

## Gráfico acumulado de todos os resultados

Para representar o histórico completo:

- cada ocorrência adicionará um pequeno círculo dentro do retângulo do número;
- o diâmetro inicial sugerido é de aproximadamente 3 mm;
- os círculos serão posicionados lado a lado;
- quando a largura disponível terminar, o preenchimento continuará na linha
  seguinte, voltando ao início do retângulo;
- o conjunto deverá formar uma mancha visual cuja densidade indique frequência;
- a mesma abordagem será aplicada às médias.

Quando a quantidade de círculos ultrapassa a capacidade da célula, o
preenchimento retorna ao primeiro ponto e continua sobrepondo novos ciclos. A
opacidade faz a sobreposição aumentar a densidade visual sem alterar o tamanho
da grade. Cada resultado também produz uma pequena marca em sua coordenada média.
O fluxo foi validado com 3.000 resultados, 18.000 marcas de dezenas e 3.000
marcas de média.

## Organização das funções Python

As responsabilidades serão separadas, conceitualmente, em:

```text
ler_planilha
validar_resultado
calcular_estatisticas_da_linha
salvar_resultado
calcular_frequencias
calcular_intervalos
calcular_media_movel
preparar_dados_do_grafico
```

Os nomes definitivos poderão mudar, mas importação, cálculos, persistência e
representação visual não deverão ser misturados numa única função.
