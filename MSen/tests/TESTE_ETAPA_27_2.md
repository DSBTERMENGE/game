# Evidência da etapa 27.2

Data: 11/11/2026.

## Entregas

- migração `028_criar_gestao_desenvolvimento.sql`;
- tabela principal e histórico protegido contra atualização e exclusão;
- domínio com catálogos e validações;
- repositório com pesquisa, filtros, ordenação e paginação no servidor;
- criação idempotente, concorrência otimista e arquivamento reversível;
- endpoints explícitos, sem API genérica de tabelas ou SQL;
- consulta ao histórico imutável;
- testes de domínio, DDL e contrato HTTP.

A migração foi aplicada ao banco local `games` após autorização específica em
11/11/2026. A versão 028 foi registrada em `schema_migrations`; as tabelas
`manutencao_sistema` e `manutencao_sistema_historico`, a restrição de
idempotência e o gatilho de histórico imutável foram confirmados diretamente no
catálogo do PostgreSQL. As duas tabelas permanecem vazias. A interface visual
permanece fora desta etapa.

## Validação

Os testes específicos são executados com:

```powershell
$env:PYTHONPATH='MSen/src'
python -m unittest discover -s MSen/tests -p 'test_*gestao_desenvolvimento*.py'
```

Validação final: os 16 testes específicos e a suíte completa de 722 testes
Python foram aprovados. Os avisos de arquivos não fechados pertencem aos testes
preexistentes da página Screener e não causaram falha.
