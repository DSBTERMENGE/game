# Teste de soma, média e mediana — Item 2.2

## Data e escopo

- Data: 2026-10-26.
- Python: 3.13.5.
- Código: `src/msen/calculos/estatisticas_linha.py`.
- Testes: `tests/test_estatisticas_linha.py`.
- Banco, Excel, API e interface: não acessados.

## Teste específico

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_estatisticas_linha.py' -v
```

Resultado:

```text
Ran 6 tests
OK
```

## Teste acumulado dos Itens 2.1 e 2.2

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
```

Resultado:

```text
Ran 21 tests
OK
```

## Casos conferidos

- exemplo da apresentação 3069;
- menor conjunto válido: 01 a 06;
- maior conjunto válido: 55 a 60;
- mediana independente da ordem de entrada;
- ordem original preservada;
- média calculada com `Decimal`;
- seis casas na média e uma casa na mediana;
- arredondamento aprovado para média periódica;
- funções sem alteração do modelo de entrada;
- nenhuma regressão nas validações do Item 2.1.

## Valores de referência

Para `47, 5, 22, 44, 57, 19`:

```text
soma    = 194
média   = 32.333333
mediana = 33.0
```

## Conclusão

Os critérios do Item 2.2 foram atendidos. Isso não autoriza implementar o
desvio-padrão do Item 2.3.
