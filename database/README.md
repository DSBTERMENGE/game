# Banco de dados do Game / MSen

Esta pasta contém a estrutura PostgreSQL versionada do projeto. O banco
planejado chama-se `games`, mas os arquivos SQL não criam o database nem fazem
troca automática de conexão. Eles devem ser executados somente depois de
confirmar o ambiente e o banco de destino.

## Arquivos

- `schema_postgresql.sql`: estrutura completa atual para uma instalação nova;
- `migrations/001_criar_estrutura_inicial.sql`: primeira alteração incremental,
  com as três tabelas aprovadas;
- `migrations/002_criar_tabela_padroes.sql`: cadastro e resumo estatístico dos
  padrões;
- `migrations/003_inicializar_catalogo_padroes.sql`: três registros iniciais e
  sequência de códigos que não reutiliza exclusões;
- `migrations/004` a `008`: grupos adicionais, geometria e classificações;
- `migrations/009_adicionar_percentual_ocorrencia_padroes.sql`: denominador e
  percentual da fotografia estatística atual de cada padrão;
- `migrations/010_remover_sem_correspondencia.sql`: mantém somente ocorrências
  reais de padrões na classificação histórica;
- `migrations/011_criar_amostras_validacao.sql`: relaciona resultados escolhidos
  como entradas para homologação das funções, sem duplicar as dezenas;
- `migrations/012_criar_catalogo_avaliacoes_validacao.sql`: cria o catálogo das
  funções e as comparações por amostra, incluindo grupos e subgrupos;
- `migrations/013_criar_estado_algoritmo_selecao.sql`: cria a linha única que
  bloqueia ou libera o algoritmo conforme homologação, perfis e cobertura;
- `migrations/014_adicionar_assinatura_regra_validacao.sql`: separa a assinatura
  da regra matemática da assinatura da implementação Python;
- `migrations/015_criar_perfis_operacionais_atuais.sql`: guarda somente o resumo
  estatístico e geométrico vigente, recalculado sobre todos os resultados;
- `migrations/016_referencias_independentes_validacao.sql`: registra origem e
  revisor das referências e representa valor numérico legitimamente ausente;
- `migrations/017_ampliar_frequencia_resultado.sql`: acrescenta quantidade,
  mínimo e máximo dos intervalos entre ocorrências simples e preenche os dados
  atuais diretamente dos resultados;
- `migrations/018_criar_configuracao_frequencia_dezenas.sql`: cria a configuração
  ativa, tipada e assinada do estudo de frequência das dezenas;
- `migrations/019_criar_historico_frequencia_dezenas.sql`: cria gerações
  isoladas e fotografias por concurso, dezena e tipo de evento;
- `migrations/020_identificar_origem_historico_frequencia.sql`: associa cada
  geração à assinatura e à quantidade dos resultados que a originaram;
- `migrations/018_criar_configuracao_frequencia_dezenas.sql`: cria a configuração
  ativa, tipada e assinada do estudo de frequência das dezenas;
- `seeds/README.md`: regras para dados iniciais e importados.

## Regras

1. Não colocar senhas ou endereços privados nos arquivos SQL.
2. Não incluir dados da planilha no DDL.
3. Toda alteração futura deve receber uma nova migração numerada.
4. Nunca editar uma migração já aplicada em algum ambiente; criar a próxima.
5. Antes de executar, confirmar servidor, database, usuário e existência de
   backup quando houver dados importantes.

## Execução

O executor Python aplica, em ordem, somente as migrações ainda não registradas e
confere o checksum das já executadas. `schema_postgresql.sql` representa a
estrutura completa para uma instalação nova.

O banco local persistente só pode receber uma migração depois dos testes e da
autorização correspondente. O PythonAnywhere permanece fora do escopo até a
conclusão de todo o desenvolvimento local.
