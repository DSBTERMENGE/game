# Teste da subetapa 33.4 — Integração e validação

Data: 14/11/2026

## Alteração verificada

- preservação dos resumos de Média espacial, CG1, CG2 e Quadrantes;
- inclusão simultânea da tabela das 60 ocorrências quando Dezenas está ativa;
- largura lateral fixa;
- altura limitada à altura da grade das dezenas;
- rolagem interna para combinações com conteúdo extenso.

## Conferência no servidor real

Todas as cinco camadas foram ativadas em `http://127.0.0.1:5050/`. O navegador
confirmou:

- 60 frequências exibidas;
- resumos de Quadrantes, Média espacial, CG1 e CG2 preservados;
- altura lateral: 359,046875 px;
- altura do mapa: 358,953125 px;
- largura lateral: 208 px;
- conteúdo horizontal cortado: 0;
- rolagem vertical interna ativa para o conteúdo de 859 px.

## Resultado

Aprovado. A combinação das camadas não aumenta nem desloca o Painel.
