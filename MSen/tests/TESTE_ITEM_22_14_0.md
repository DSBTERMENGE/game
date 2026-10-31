# Evidência da subetapa 22.14.0 — Contrato da prévia modal

Data: 2026-10-31

## Escopo autorizado

Somente definição e documentação do contrato. HTML, CSS, JavaScript, API e
banco de dados permaneceram inalterados.

## Fontes reconciliadas

- `GET /api/frequencias/estado` já fornece resultados, período, geração ativa,
  último concurso processado, linhas históricas, criação e conclusão;
- `POST /api/frequencias/previa` já distingue modo, motivo, período, concursos
  novos, divergências, gravação e substituição;
- a estimativa de concursos e linhas deverá ser acrescentada à API na 22.14.1,
  evitando cálculo funcional duplicado no frontend.

## Contrato aprovado

1. `Calcular prévia` não executa nem grava.
2. O modal apresenta situação atual, ação prevista, período, totais e gravação.
3. `Cancelar` não cria tarefa.
4. `Prosseguir` é a confirmação explícita e abre o acompanhamento existente.
5. O botão `Executar` separado deixa de existir.
6. Ausência de alteração bloqueia prosseguimento.
7. Mudanças invalidam a prévia e a execução revalida o estado no servidor.

A implementação depende de autorização específica da subetapa 22.14.1.
