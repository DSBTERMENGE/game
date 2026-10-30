# Teste da subetapa 22.6 — confirmação, simulação e cancelamento

Data: 2026-10-30.

## Contratos implementados

- `Salvar dados` possui estado inicial `true` no controle reutilizável do
  frontend; esse estado não é lido nem gravado no armazenamento do navegador.
- Toda chamada de gravação exige `confirmacao_gravacao=True` no servidor.
- A mensagem aprovada é:

```text
O tick para salvar está ativo. Você realmente deseja salvar os dados?
```

- A prévia informa primeira carga, ausência de alteração, concursos novos,
  reconstrução por origem ou reconstrução por configuração.
- Configuração divergente devolve campo, valor gravado e valor calculado.
- Tick desmarcado executa simulação completa ou incremental sem criar geração,
  substituir configuração ou inserir fotografia.
- O progresso usa concursos realmente processados, incluindo a recomposição do
  estado acumulado antes dos novos cortes.
- O cancelamento é cooperativo entre concursos e reverte integralmente a
  transação, mesmo quando um novo corte já foi inserido.
- O coordenador do servidor e o controle do frontend recusam execução dupla.

O modal reutilizável passou a aceitar uma função opcional de cancelamento. O
botão solicita cancelamento seguro, permanece no modal e não fecha a operação
enquanto o servidor ainda estiver executando.

## PostgreSQL efêmero

```text
python -m tests.validar_operacao_historico_frequencia
```

Foram confirmados:

- prévia inicial e mensagem obrigatória;
- simulação de 540 linhas sem qualquer gravação;
- recusa de gravação sem confirmação;
- progresso chegando ao total real;
- prévia incremental listando concursos 6 e 7;
- simulação incremental de 360 linhas sem alterar as 540 existentes;
- cancelamento depois da inserção do concurso 6, com rollback completo;
- gravação posterior bem-sucedida;
- comparação lado a lado do `tamanho_inicial` divergente.

O database efêmero foi removido e o `games` não foi alterado.

## Regressão

- Python: **615 testes aprovados**.
- JavaScript: **42 testes aprovados**.

Permaneceram somente avisos preexistentes de arquivos abertos em testes do
Screener e de módulos JavaScript sem `type: module` no `package.json`.

A API pública e a página que consumirão esses contratos permanecem nas
subetapas 22.7 e 22.8.
