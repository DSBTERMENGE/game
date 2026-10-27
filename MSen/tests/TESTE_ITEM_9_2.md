# Evidência de teste — Item 9.2

Data: 2026-10-26

## Alteração

- criada a migração `002_criar_tabela_padroes.sql`;
- atualizado o esquema completo `database/schema_postgresql.sql`;
- nenhuma tabela anterior foi alterada ou recriada;
- a tabela foi criada inicialmente sem registros.

## Validação em database temporário vazio

O executor aplicou as migrações `001` e `002` em ordem. Foram confirmadas as
sete colunas contratadas e três estados válidos:

- detector/estatística pendente, com os três campos estatísticos nulos;
- histórico analisado sem ocorrência, com `num_oco = 0`;
- duas ocorrências, com intervalo médio 15 e desvio-padrão zero.

O PostgreSQL rejeitou corretamente:

- código fora do formato;
- nome vazio;
- contagem negativa;
- duas ocorrências sem as estatísticas obrigatórias;
- código duplicado.

O database temporário foi removido e a listagem final retornou vazia.

## Aplicação no database local preenchido

- backup local anterior já havia sido restaurado e validado no Item 7.3;
- migração aplicada: `002`;
- migração já existente e preservada: `001`;
- resultados antes/depois: 3.069;
- frequências antes/depois: 60;
- padrões após a criação: 0;
- migrações registradas: `001`, `002`.

## Regressão

- 140 testes Python aprovados;
- 2 fluxos integrados Google Chrome/PostgreSQL aprovados em 9,1 segundos;
- nenhuma alteração ou publicação no PythonAnywhere.

## Conclusão

A migração é aditiva, preservou o banco preenchido e satisfez as restrições do
contrato. O Item 9.2 está concluído.
