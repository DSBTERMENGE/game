# Configuração da conexão PostgreSQL

## Variáveis

A aplicação recebe a conexão exclusivamente por variáveis de ambiente:

- `GAME_DB_HOST`: servidor PostgreSQL;
- `GAME_DB_PORT`: porta, com padrão `5432`;
- `GAME_DB_NAME`: database, planejado como `games`;
- `GAME_DB_USER`: usuário exclusivo da aplicação;
- `GAME_DB_PASSWORD`: senha obrigatória;
- `GAME_DB_SSLMODE`: padrão `prefer`; em hospedagem, usar o modo exigido pelo
  provedor;
- `GAME_DB_CONNECT_TIMEOUT`: padrão de 5 segundos, aceitando de 1 a 60.

`MSen/.env.example` é apenas um modelo. A aplicação não carrega `.env`
automaticamente. No desenvolvimento, as variáveis devem ser definidas no
terminal ou no processo que inicia o programa. No PythonAnywhere, devem ser
fornecidas pela configuração segura do ambiente/WSGI, sem colocá-las no Git.

## Segurança

- a senha é obrigatória mesmo quando um ambiente descartável permite conexão
  sem autenticação;
- a configuração oculta a senha em sua representação textual;
- o driver recebe parâmetros separados, sem criar URL contendo credenciais;
- falhas retornam código e orientação genérica, sem copiar a mensagem bruta do
  servidor;
- não existe valor padrão para host, database, usuário ou senha.

## Responsabilidades

`msen.config.carregar_configuracao_banco` valida o ambiente.
`msen.database.abrir_conexao` abre uma conexão, e
`msen.database.verificar_conexao` executa uma consulta sem alteração para
confirmar database, usuário e versão do servidor.

Esta etapa não cria database, tabelas ou dados. Migrações pertencem ao Item 4.2.

## Ordem dos ambientes

O ambiente local é o único destino durante o desenvolvimento. A configuração
do PythonAnywhere será preparada somente quando todas as funcionalidades locais
estiverem concluídas, testadas e aprovadas. As credenciais e os parâmetros dos
dois ambientes não devem ser misturados.
