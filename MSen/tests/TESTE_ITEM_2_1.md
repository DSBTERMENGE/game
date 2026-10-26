# Teste do modelo de entrada — Item 2.1

## Data e escopo

- Data: 2026-10-26.
- Python: 3.13.5.
- Módulo: `src/msen/modelos/resultado.py`.
- Testes: `tests/test_resultado.py`.
- Banco, Excel, API e interface: não acessados.

## Comando executado

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_resultado.py' -v
```

Foi usado `unittest`, disponível na biblioteca padrão, porque `pytest` ainda não
está instalado no ambiente. Os testes são compatíveis com descoberta futura
pelo `pytest`.

## Resultado

```text
Ran 15 tests
OK
```

Foram conferidos:

- criação de uma linha válida;
- normalização de `DD/MM/AAAA` para `date`;
- preservação da ordem dos seis resultados;
- imutabilidade do modelo;
- data ausente, inexistente, com formato incorreto ou horário;
- apresentação ausente, não inteira ou não positiva;
- quantidade de resultados ausente, inválida ou não sequencial;
- posição individual ausente;
- resultado não inteiro, inclusive booleano;
- limites 1 e 60 aceitos;
- valores 0 e 61 rejeitados;
- resultado repetido rejeitado e identificado.

Uma tentativa adicional de `py_compile` encontrou acesso negado ao criar
`__pycache__`. Isso não impediu a importação e execução integral dos módulos. Uma
importação posterior com gravação de bytecode desativada também foi aprovada.

## Conclusão

Os critérios do Item 2.1 foram atendidos. Isso não autoriza implementar os
cálculos do Item 2.2.
