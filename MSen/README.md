# MSen

Projeto Python para organizar e desenvolver funcionalidades relacionadas à
análise de resultados da Mega-Sena.

## Estrutura

- `src/msen`: código-fonte da aplicação;
- `tests`: testes automatizados;
- `tests/fixtures`: planilhas pequenas e controladas para testes de importação;
- `dados/fontes`: planilhas originais usadas como fonte de resultados;
- `dados`: demais recursos visuais e arquivos de apoio;
- `pyproject.toml`: configuração, dependências e metadados do projeto.

Os documentos gerais ficam em `../docs` e as anotações de planejamento em
`../notas`.

## Preparação do ambiente

No diretório `MSen`, crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Antes de acessar o PostgreSQL, defina as variáveis `GAME_DB_*` descritas em
`.env.example`. O projeto não lê esse arquivo automaticamente e nunca deve
receber senhas versionadas.

## Execução

```powershell
msen
```

Também é possível executar diretamente pelo módulo:

```powershell
python -m msen.main
```

Para iniciar o servidor local com a interface e a API no mesmo endereço:

```powershell
flask --app "msen.api:criar_app()" run
```

Se o pacote ainda não tiver sido instalado em modo editável, use nesta sessão
do PowerShell:

```powershell
$env:PYTHONPATH="src"
flask --app "msen.api:criar_app()" run
```

Esse servidor é apenas para desenvolvimento. Em produção, inclusive no
PythonAnywhere, deve ser usada a entrada WSGI disponível em `wsgi.py`.

Depois de iniciar, abra `http://127.0.0.1:5000/` no Google Chrome.

## Testes

```powershell
pytest
```

Na raiz `Game`, os testes de frontend usam:

```powershell
npm run test:frontend
npm run test:browser
npm run test:integration:browser
```

O último comando exige o PostgreSQL local configurado em `MSen/.env` e executa
somente leituras do banco durante o fluxo PostgreSQL até os gráficos.
