# Plano do projeto Game / MSen

> A execução detalhada, com autorização item a item e testes obrigatórios, está
> em `PLANO_ETAPAS_E_TESTES.md`. Esse documento é o roteiro operacional vigente.

## Finalidade

O MSen será uma aplicação para importar, armazenar, consultar e analisar o
histórico de concursos da Mega-Sena. O sistema deverá funcionar no ambiente
local e, posteriormente, no PythonAnywhere usando PostgreSQL.

Este documento é o roteiro principal do projeto. Detalhes estáveis ficam em
`docs`, ideias ainda não aprovadas ficam em `notas/ideias.md` e o ponto de
continuidade entre sessões fica em `CONTINUIDADE_IA.md`.

## Regras de trabalho

1. O FinCtl é somente uma referência externa. Nenhum arquivo, dado, histórico
   Git ou credencial dele deve ser incorporado ao Game.
2. Nenhuma senha deve ser gravada no repositório. A configuração deve vir de
   variáveis de ambiente.
3. O arquivo original de resultados é uma entrada e não deve ser alterado.
4. Alterações no banco devem ser versionadas por migrações SQL.
5. Cada etapa só será considerada concluída depois de testes e registro em
   `CONTINUIDADE_IA.md`.
6. Ideias não aprovadas não são requisitos e não devem ser implementadas
   automaticamente.

## Arquitetura planejada

```text
Interface HTML/JavaScript
          |
          v
API Python
          |
          +-- serviços e regras de negócio
          +-- importação e validação da planilha
          +-- consultas e análises
          |
          v
PostgreSQL (banco games)
```

O pacote Python continuará em `MSen/src/msen`. A interface fica separada em
`frontend`, com CSS em `frontend/css` e JavaScript em `frontend/js`. Ela não
acessará o banco diretamente: toda leitura ou gravação passará pela API e pelas
regras Python.

## Etapas

### Etapa 1 — Documentação e decisões

- [x] Definir a finalidade inicial do produto.
- [x] Criar o plano geral, o catálogo de funcionalidades, o arquivo de ideias e
  o documento de continuidade.
- [ ] Confirmar com o usuário o primeiro conjunto de funcionalidades.
- [ ] Registrar decisões pendentes em `notas/decisoes.md`.

### Etapa 2 — Banco de dados PostgreSQL

- [x] Aprovar o modelo inicial da tabela `resultados` descrito em
  `docs/banco-de-dados.md`.
- [x] Criar a pasta `database` e o DDL inicial.
- [ ] Criar tabela de controle de migrações.
- [x] Criar as restrições e o índice inicialmente aprovados.
- [ ] Preparar configuração por variáveis de ambiente.
- [ ] Testar criação em um banco local vazio.
- [ ] Testar uma segunda execução sem perda ou duplicação de dados.
- [ ] Documentar a preparação do banco no PythonAnywhere.

### Etapa 3 — Código Python de infraestrutura

- [ ] Adicionar o driver PostgreSQL às dependências.
- [ ] Criar módulo de configuração e conexão.
- [ ] Criar executor de migrações pendentes.
- [ ] Criar repositórios de persistência sem SQL espalhado pela interface.
- [ ] Criar tratamento de transações, rollback e erros.
- [ ] Criar testes unitários e de integração.

### Etapa 4 — Importação dos resultados

- [ ] Ler a planilha sem modificá-la.
- [ ] Localizar e validar o cabeçalho real.
- [ ] Converter número do concurso, data e seis dezenas.
- [ ] Recusar concursos inválidos e dezenas repetidas ou fora de 1 a 60.
- [ ] Importar de forma idempotente, sem duplicar concursos existentes.
- [ ] Gerar relatório com registros importados, ignorados e rejeitados.

### Etapa 5 — Consultas e análises

- [ ] Consultar um concurso pelo número.
- [ ] Consultar concursos por período.
- [ ] Calcular frequência histórica das dezenas.
- [ ] Calcular intervalos, intervalo médio e desvio-padrão dos intervalos para
  cada número de 01 a 60.
- [ ] Calcular médias móveis quando solicitadas.
- [ ] Comparar combinações informadas com resultados anteriores.
- [ ] Definir consultas ou views adicionais somente conforme necessidade real.

### Etapa 6 — API e interface

- [ ] Escolher e registrar o framework web Python.
- [ ] Definir contratos de entrada e saída da API.
- [ ] Integrar os arquivos HTML, CSS e JavaScript existentes.
- [ ] Plotar um resultado e sua média na grade de 01 a 60.
- [ ] Plotar o histórico como manchas formadas por pequenos círculos.
- [ ] Exibir erros de validação de maneira clara.
- [ ] Testar os principais fluxos da interface até o PostgreSQL.

### Etapa 7 — PythonAnywhere

- [ ] Criar ou identificar o banco PostgreSQL `games` no serviço.
- [ ] Configurar variáveis de ambiente no WSGI sem expor segredos.
- [ ] Aplicar as migrações antes de liberar a nova versão.
- [ ] Não executar todo o DDL destrutivamente a cada carregamento do WSGI.
- [ ] Fazer validação pós-migração e teste funcional.
- [ ] Definir backup e procedimento de reversão.

## Critérios de conclusão

Uma funcionalidade estará pronta quando tiver comportamento definido,
implementação, teste correspondente, documentação atualizada e nenhuma
credencial ou dado temporário incluído no Git.
