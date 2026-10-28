# Teste do Item 16.7 — perfil, percentuais e raridade experimental

Data: 28/10/2026

## Regras implementadas

- denominador oficial: todos os resultados válidos;
- percentual alternativo: somente resultados classificados em algum padrão;
- `SEM_CORRESPONDENCIA` completa o total oficial, mas não é padrão raro;
- operador de raridade: estritamente menor (`<`);
- amostra vazia não produz padrões raros;
- o perfil exige classificação completa antes do cálculo;
- as contagens são reconciliadas com os detectores históricos;
- `num_oco`, intervalo médio e desvio-padrão de `PD_001`–`PD_003` são
  sincronizados em conjunto, preservando a consistência do catálogo;
- nenhuma regra do screener é ativada.

## Teste controlado

Com quatro resultados e uma ocorrência em cada classe, todos apresentaram 25%
do total. Com limite igual a 25%, nenhum padrão foi marcado como raro. Com
limite igual a 25,000001%, `PD_001`, `PD_002` e `PD_003` foram indicados como
raros. Isso comprova o operador estrito `<`.

O perfil rejeitou corretamente a tentativa anterior ao recálculo das
classificações. O catálogo foi sincronizado com uma ocorrência em cada padrão.

## Perfil do histórico clonado

Com limite experimental de 10%:

| Classe | Quantidade | % dos 3.069 | % dos 1.289 classificados | Raro |
|---|---:|---:|---:|---|
| PD_001 | 1.192 | 38,840013% | 92,474787% | Não |
| PD_002 | 92 | 2,997719% | 7,137316% | Sim |
| PD_003 | 5 | 0,162920% | 0,387898% | Sim |
| SEM_CORRESPONDENCIA | 1.780 | 57,999348% | não aplicável | Não |

As quantidades e os percentuais oficiais fecharam em 3.069 e 100%. A soma dos
percentuais alternativos exibidos pode apresentar diferença de 0,000001 ponto
percentual exclusivamente pelo arredondamento individual em seis casas; as
contagens exatas fecham em 1.289.

`PD_002` e `PD_003` foram apenas indicados como raros. Nenhum deles foi ativado
como filtro.

## Testes e proteção

- cinco testes unitários direcionados: aprovados;
- dois fluxos PostgreSQL temporários: aprovados;
- 403 testes da regressão Python: aprovados;
- databases temporários removidos; auditoria final `[]`;
- database `games` e PythonAnywhere não alterados.
