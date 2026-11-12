# Preparação de publicação da Gestão do desenvolvimento

Este roteiro não autoriza nem executa publicação no PythonAnywhere.

## Antes de publicar

1. Confirmar commit local aprovado e cópia de segurança do banco remoto.
2. Verificar variáveis `GAME_DB_*` do ambiente sem exibir credenciais.
3. Confirmar que o database de destino é o previsto para o Game.
4. Enviar código, migração 028 e arquivos estáticos da nova página.
5. Aplicar a migração pelo executor oficial e conferir a versão em
   `schema_migrations`.
6. Recarregar a aplicação web e invalidar arquivos estáticos antigos.

## Conferência funcional

1. Abrir a Gestão do desenvolvimento e consultar a lista vazia ou existente.
2. Abrir e cancelar o registro rápido, confirmando ausência de nova linha.
3. Criar um registro de homologação previamente autorizado.
4. Editar, consultar histórico, arquivar e desarquivar esse registro.
5. Confirmar pesquisa, filtros, paginação e mensagens em tela estreita.
6. Registrar data e resultado da publicação no campo próprio.

Qualquer falha interrompe a publicação. Não se deve alterar manualmente o
histórico ou contornar a versão de concorrência.
