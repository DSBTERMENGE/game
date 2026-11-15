# Evidência da etapa 31.8 — Manchas e gradientes

Data: 12/11/2026

## Camadas das manchas

O quadro Manchas recebeu seleções independentes para Média espacial, CG1, CG2
e Quadrantes. Uma, várias ou todas podem ser combinadas antes de usar `Desenhar
mancha`.

Os pontos próximos são agrupados em células lógicas de um quarto de unidade. A
quantidade acumulada determina o tamanho, a opacidade e a cor: concentrações
menores começam em azul e as maiores avançam até o vermelho. As camadas possuem
classes distintas para permitir sua identificação e evolução posterior.

Quando Quadrantes está marcado, quatro áreas transparentes são desenhadas sobre
o mapa. A intensidade de cada uma corresponde à quantidade histórica de dezenas
naquele quadrante.

## Dados históricos

Foi criado um contrato compacto em `/api/resultados/manchas`. Ele devolve apenas
o número do concurso, CG1 e CG2. A Média espacial e os quadrantes são obtidos dos
resultados já presentes no navegador. A consulta é somente leitura e reutiliza
o cache geométrico; nenhuma linha é gravada.

Enquanto a persistência incremental não for ligada, a primeira preparação de
CG2 pode ser mais demorada porque calcula os concursos ainda ausentes do cache.
As consultas seguintes na mesma execução reutilizam os valores calculados.

## Validação

- contrato compacto coberto por teste da API;
- seleção individual e sobreposição das quatro camadas cobertas por teste;
- gradiente agrupado validado com aproximadamente 3.000 resultados;
- 12 testes da API e 128 testes unitários do frontend aprovados;
- fluxo Chromium de importação, mancha e limpeza aprovado;
- nenhuma tabela ou linha do banco foi alterada.
