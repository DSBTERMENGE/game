# Evidência da subetapa 22.14.2 — Fechamento da prévia modal

Data: 2026-10-31

## Documentação reconciliada

- ajuda da página atualizada para o fluxo modal;
- API documentada com período, quantidade de concursos e linhas estimadas;
- funcionamento atualizado para o caminho único de confirmação;
- funcionalidades e decisões atualizadas.

## Cobertura específica no Chrome

- primeira carga e simulação;
- atualização incremental;
- reconstrução por configuração;
- reconstrução por alteração da origem;
- ausência de alteração com `Prosseguir` desabilitado;
- erro apresentado no diálogo sem criar execução;
- cancelamento sem criar tarefa;
- fechamento por `Esc` e foco contido no diálogo;
- gravação com uma única confirmação explícita;
- layout em 1.280 px e 520 px.

## Regressão final

```powershell
python -m unittest discover -s MSen\tests -p "test_*.py"
npm run test:frontend
npm run test:browser
```

Resultados:

- 629 testes Python aprovados;
- 51 testes JavaScript aprovados;
- 32 fluxos Chrome aprovados.

Os avisos preexistentes de arquivos do Screener não fechados e de módulos Node
sem `type: module` não causaram falha. Nenhuma carga histórica foi iniciada e
nenhum dado de frequência foi gravado no banco `games`.
