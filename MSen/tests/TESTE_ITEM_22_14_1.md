# Evidência da subetapa 22.14.1 — Prévia modal

Data: 2026-10-31

## Implementação

- API de prévia ampliada com `quantidade_concursos` e `linhas_estimadas`;
- estimativa calculada pelo servidor conforme modo e tipos de evento;
- diálogo com situação atual, ação, motivo, período, totais e gravação;
- fluxo único `Calcular prévia` → `Cancelar` ou `Prosseguir`;
- remoção do botão separado `Executar` e da segunda confirmação genérica;
- bloqueio de `Prosseguir` para `SEM_ALTERACAO`;
- erro da prévia apresentado no próprio diálogo;
- prosseguimento integrado ao modal de andamento existente.

## Verificação

- 629 testes Python aprovados;
- 51 testes JavaScript aprovados;
- 5 fluxos Chrome específicos aprovados em largura normal e estreita;
- validador PostgreSQL confirmou estimativas de carga inicial e incremental;
- API real do banco `games` devolveu primeira carga dos concursos 500 a 3.069,
  com 2.570 concursos e 462.600 linhas estimadas;
- a consulta real de prévia não criou tarefa e não gravou histórico;
- somente a porta 5050 permaneceu ativa para o Game.

Os avisos Python sobre três arquivos antigos do Screener abertos pelos testes
permanecem preexistentes e não causaram falha.
