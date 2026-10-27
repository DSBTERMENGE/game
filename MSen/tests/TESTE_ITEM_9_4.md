# Evidência de teste — Item 9.4

Data: 2026-10-26

## Regra aprovada

Cada resultado é classificado pelo maior bloco consecutivo:

- `PD_001`: maior bloco exatamente igual a dois;
- `PD_002`: maior bloco exatamente igual a três;
- `PD_003`: maior bloco superior a três.

As categorias são exclusivas. O exemplo aprovado
`10, 25, 26, 27, 50, 58` pertence somente a `PD_002`, pelo bloco
`25, 26, 27`.

## Implementação

- detectores puros em `msen/padroes/sequenciais.py`;
- estatística reutilizável em `msen/padroes/estatisticas.py`;
- registro dos três códigos em `msen/padroes/iniciais.py`;
- todas as funções públicas documentadas em português;
- nenhuma gravação no banco nesta subetapa.

## Casos testados

- ausência de sequência;
- dois, três, quatro, cinco e seis números consecutivos;
- grupos concorrentes e classificação pelo maior;
- dois grupos de duas dentro do mesmo resultado contando apenas uma ocorrência;
- limites 01 e 60;
- entrada fora do contrato;
- histórico vazio e com somente uma ocorrência;
- ordenação sem modificar a entrada;
- intervalos, média e desvio-padrão populacional;
- concurso duplicado, datas incompatíveis e detector inválido.

## Resultados dos testes

- 19 testes específicos de padrões aprovados;
- 159 testes Python acumulados aprovados.

## Leitura do histórico local

Análise somente leitura dos 3.069 resultados:

| Código | Resultados correspondentes | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_001` | 1.192 | 2,575147 | 1,995592 |
| `PD_002` | 92 | 33,527473 | 33,637806 |
| `PD_003` | 5 | 680,500000 | 545,478460 |

`PD_003` ocorreu nos concursos 186, 509, 2052, 2789 e 2908, com intervalos
323, 1543, 737 e 119. Os valores ainda não foram persistidos; isso pertence ao
Item 9.5.

## Conclusão

Os detectores e cálculos iniciais estão implementados e testados. O banco local
e o PythonAnywhere não foram alterados nesta subetapa.
