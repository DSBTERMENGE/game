# Evidência de teste — subetapa 18.2

Data: 28/10/2026

## Escopo

Fotografia canônica da configuração do novo screener, sem conexão com filtros
reais, sem persistência e sem alteração no screener operacional existente.

## Verificações específicas

- ordenação efetiva de famílias e filtros;
- parâmetros aninhados, datas, decimais, versões, modo, semente e limite;
- intervalo e frequências históricas dos grupos de padrões;
- cálculo da lista excludente com operadores `<` e `<=`;
- classe sem correspondência fora da lista excludente;
- igualdade de JSON/checksum para o mesmo conteúdo lógico;
- mudança do checksum quando a configuração muda;
- independência posterior em relação aos mapas de origem;
- detecção de conteúdo adulterado;
- recusa de tipos ambíguos, parâmetros incompletos e frequências divergentes.

## Comandos

```powershell
$env:PYTHONPATH='src;.'
python -m unittest tests.test_fotografia_configuracao -v
python -m unittest discover -s tests -v
python -c "import ast,pathlib; arquivos=[pathlib.Path('src/msen/screener/fotografia.py'),pathlib.Path('src/msen/screener/__init__.py'),pathlib.Path('tests/test_fotografia_configuracao.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in arquivos]"
```

## Resultado

- Testes específicos: **8 aprovados**.
- Regressão completa: **461 testes aprovados**.
- Validação sintática em memória: **3 arquivos aprovados**.
- `compileall` não foi usado como evidência porque o servidor local mantém
  arquivos do `__pycache__` bloqueados para substituição no Windows.
- Os `ResourceWarning` já existentes em testes de leitura do frontend não
  causaram falha e não pertencem ao código desta subetapa.
