# Evidência da etapa 31.4 — Conclusão do cálculo do Polígono 2

Data: 12/11/2026

## Regra concluída

A tentativa experimental da etapa 31.3 não pode ser usada como regra final
apenas removendo arestas excedentes. Em 180 dos 3.069 concursos, as arestas que
ela conservou já não continham nenhum circuito capaz de passar uma única vez
pelas seis dezenas. Nesses casos, alguma aresta necessária havia sido retirada
na primeira fase.

O cálculo definitivo, portanto, aplica diretamente os requisitos aprovados:

- usa as seis dezenas como seis vértices;
- forma um único circuito fechado com seis arestas;
- dá grau dois a cada vértice;
- rejeita qualquer circuito com cruzamento;
- mede todos os circuitos simples possíveis;
- escolhe, de forma determinística, o circuito de maior área;
- calcula a área exata e o centro de gravidade CG2.

A menor dezena é fixada como início e circuitos percorridos em sentidos opostos
são tratados como equivalentes. Assim, são avaliados no máximo 60 circuitos por
concurso, sem aproximações numéricas.

## Conferência histórica

Os 3.069 concursos do banco atual foram consultados sem gravação. Todos
produziram um Polígono 2 válido, com seis vértices distintos e área positiva;
não houve resultado ausente ou estruturalmente inválido.

## Validação automatizada

- cinco testes específicos do cálculo definitivo;
- quatro testes do diagnóstico experimental;
- 33 testes geométricos existentes;
- total de 42 testes aprovados;
- entrada em qualquer ordem produz o mesmo resultado;
- desempates e orientação são determinísticos;
- pontos colineares, que não formam área, são recusados;
- nenhuma API, interface, tabela ou linha do banco foi alterada.

O cálculo está pronto para a integração visual e histórica prevista nas etapas
seguintes. Nesta etapa ele ainda não foi desenhado no Painel.
