# Teste do DDL — Item 1.4

## Data e isolamento

- Data: 2026-10-26.
- PostgreSQL usado: 16.11.
- Ambiente: cluster temporário criado exclusivamente para o teste.
- Porta temporária: 55439.
- Autenticação do cluster descartável: `trust`.
- Banco temporário: `msen_test`.
- PostgreSQL local persistente: não alterado; a conexão normal exigiu senha e
  foi abandonada sem tentativa de usar credenciais de outros projetos.
- PythonAnywhere: não acessado.
- Finalização: servidor temporário parado, diretório removido e porta sem
  resposta.

## Arquivos testados

- `database/schema_postgresql.sql`;
- `database/migrations/001_criar_estrutura_inicial.sql`.

Os dois arquivos tinham conteúdo idêntico durante o teste:

```text
SHA-256: DFA29D6966B260B719E30BCB63AE58B0A98D744D44CDFCFD648EAFD0F1A9BD87
```

## Resultados

### Primeira execução

- transação concluída;
- `schema_migrations` criada;
- `resultados` criada;
- `frequencia_de_resultado` criada;
- índice por `data_resultado` criado;
- 60 dezenas inseridas.

### Segunda execução controlada

- transação concluída;
- objetos existentes foram preservados;
- nenhuma tabela foi duplicada;
- nenhuma dezena foi duplicada;
- o segundo `INSERT` de sementes inseriu zero linhas.

### Conferência de estrutura e sementes

```text
tabelas=3
dezenas=60
dezenas_distintas=60
```

### Inserção válida

Foi inserido o exemplo aprovado da apresentação 3069 e atualizada a linha de
frequência da dezena 05:

```text
resultado_valido=1
```

### Restrição de resultados repetidos

Uma linha contendo a dezena 05 duas vezes foi rejeitada pela restrição
`ck_resultados_distintos`. A linha não permaneceu na tabela.

### Reversão provocada

Uma inserção válida foi seguida de divisão por zero dentro de uma subtransação
de teste. O PostgreSQL reverteu a inserção e o bloco confirmou sua ausência.

```text
invalidos_ausentes=0
```

## Conclusão

Os critérios do Item 1.4 foram atendidos no ambiente isolado. Isso valida o DDL,
mas não autoriza sua execução no PostgreSQL local persistente nem no
PythonAnywhere.
