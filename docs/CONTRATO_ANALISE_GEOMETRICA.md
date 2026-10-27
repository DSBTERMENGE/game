# Contrato da análise geométrica dos resultados

Data da decisão: 2026-10-27. Este documento define o comportamento esperado
antes da implementação. Nesta fase as medidas servem somente para análise do
histórico; nenhuma delas exclui combinações.

## 1. Coordenadas e ordem dos vértices

A matriz contém dez colunas e seis linhas. O centro da dezena `n` tem a
coordenada lógica:

```text
x = (n - 1) % 10
y = (n - 1) // 10
```

Assim, `01=(0,0)`, `10=(9,0)`, `51=(0,5)` e `60=(9,5)`. Distâncias, áreas e
centros são calculados em unidades lógicas e não em pixels ou milímetros. A
conversão para a tela será apenas visual.

As seis dezenas devem ser diferentes, estar entre 01 e 60 e serão sempre
ordenadas crescentemente antes da construção. A ordem original do sorteio
permanece armazenada, mas não participa desta análise. Portanto, qualquer
permutação das mesmas seis dezenas produz exatamente as mesmas medidas.

## 2. Linha aberta e fechamento

Os centros das seis dezenas ordenadas formam os vértices `V1` a `V6`.

- a linha aberta contém `V1–V2–V3–V4–V5–V6`;
- sua extensão é a soma euclidiana dos cinco segmentos;
- o fechamento acrescenta `V6–V1`;
- o perímetro do percurso é a extensão aberta mais o segmento de fechamento.

Os seis centros serão desenhados com pequenos círculos. A espessura, as cores,
a transparência e a visibilidade serão preferências visuais e não alterarão os
cálculos.

## 3. Cruzamentos, regiões e área total

O percurso fechado será tratado como uma rede planar:

1. localizar todos os cruzamentos entre segmentos não adjacentes;
2. dividir os segmentos nos pontos de cruzamento;
3. identificar cada região fechada e limitada formada pela rede;
4. calcular cada região uma única vez;
5. somar as áreas positivas das regiões.

Logo, um percurso que formar duas ou três regiões continuará produzindo apenas
uma `area_total`. Cruzamentos não causam cancelamento entre áreas. Segmentos
repetidos ou parcialmente sobrepostos contam uma única vez para delimitar as
regiões e não criam área por si mesmos. Encontros somente em extremidades não
são considerados cruzamentos internos.

Para evitar decisões instáveis por arredondamento, coordenadas de interseção e
relações topológicas deverão ser calculadas exatamente, preferencialmente com
`fractions.Fraction`. Arredondamento será feito apenas na apresentação ou na
persistência, com precisão ainda a ser definida na migração.

## 4. Centro de gravidade único

Cada região fechada possui área `Ai` e centroide `(Cxi, Cyi)`. O resultado
possui um único centro de gravidade, ponderado pelas áreas:

```text
CGx = soma(Ai * Cxi) / area_total
CGy = soma(Ai * Cyi) / area_total
```

Se `area_total` for zero, `CGx` e `CGy` serão nulos. O centro de gravidade é
diferente do ponto da média espacial já existente; ambos serão preservados e
representados separadamente.

## 5. Casos degenerados

- seis pontos colineares: área zero e centro de gravidade nulo;
- trechos colineares consecutivos: permanecem no percurso e contribuem para a
  extensão, mas não criam área;
- três ou mais segmentos no mesmo cruzamento: existe um único nó na rede;
- contato de um segmento com um vértice não adjacente: o segmento é dividido
  naquele nó, sem duplicá-lo;
- sobreposição parcial: os limites coincidentes são normalizados antes da
  identificação das regiões.

## 6. Exemplos numéricos de referência

As expressões exatas abaixo devem ser usadas nos testes. Aproximações servem
somente para facilitar a conferência visual.

### Exemplo A — figura sem cruzamento

```text
Dezenas: 01, 20, 30, 40, 50, 51
Pontos:  (0,0), (9,1), (9,2), (9,3), (9,4), (0,5)
Extensão aberta: 3 + 2*sqrt(82) ≈ 21,110770
Perímetro:        8 + 2*sqrt(82) ≈ 26,110770
Área total:       36
CG:               (4,125; 2,5)
Regiões:          1
```

### Exemplo B — percurso com cruzamento e duas regiões

```text
Dezenas: 01, 02, 03, 10, 11, 20
Pontos:  (0,0), (1,0), (2,0), (9,0), (0,1), (9,1)
Cruzamento interno: (4,5; 0,5)
Extensão aberta:    18 + sqrt(82) ≈ 27,055385
Perímetro:          18 + 2*sqrt(82) ≈ 36,110770
Áreas componentes:  2,25 e 2,25
Área total:          4,5
CG global:           (4,5; 0,5)
Regiões:             2
```

### Exemplo C — área nula

```text
Dezenas: 01, 02, 03, 04, 05, 06
Pontos:  (0,0), (1,0), (2,0), (3,0), (4,0), (5,0)
Extensão aberta: 5
Perímetro:       10
Área total:      0
CG:              nulo
Regiões:         0
```

### Exemplo D — invariância da ordem de entrada

As entradas `(20, 01, 51, 40, 30, 50)` e `(01, 20, 30, 40, 50, 51)` devem
produzir integralmente os valores do Exemplo A.

## 7. Critérios de aceite da futura implementação

- validar seis dezenas distintas entre 01 e 60;
- produzir os mesmos valores para qualquer ordem de entrada;
- reproduzir os quatro exemplos deste contrato;
- não depender de dimensões ou estilos do navegador;
- manter funções públicas com docstrings em português;
- separar cálculo, persistência e desenho;
- não criar nem aplicar critérios de exclusão nesta etapa.
