# Evidência da etapa 29

Data: 11/11/2026.

## Alterações

- `prioridade` removida do domínio, API, repositório, formulário e registro
  rápido;
- `origem_registro` removida do registro e `origem_evento` removida do modelo
  do histórico;
- novo campo obrigatório `data_registro`, do tipo `DATE`, escolhido pelo
  usuário em um calendário;
- Situação do trabalho preservada;
- seletor `Ordenar por` removido;
- consulta fixada em `criado_em, id_manutencao`, na ordem de criação;
- migração 029 criada, mas ainda não aplicada ao banco local.

## Validação

- 19 testes específicos do domínio, API e migrações aprovados;
- 725 testes Python aprovados no total;
- 114 testes unitários do frontend aprovados;
- fluxos Playwright da página completa e do registro rápido aprovados;
- nenhuma gravação funcional foi realizada durante os testes de navegador.

## Pendente de autorização própria

Executar `029_data_registro_remover_prioridade_origem.sql` no banco local
`games`. Até essa aplicação, o banco continua no modelo da migração 028.
