# Evidência do Item 12.6 — reinício e integração visual

Data: 2026-10-27.

## Servidor e API

- processo anterior PID 8556 encerrado;
- servidor atualizado iniciado no PID 12888;
- endereço: `http://127.0.0.1:5050/`;
- `/api/saude`: saudável;
- `/api/padroes`: nove registros e nove detectores implementados.

Valores confirmados pela API:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_007` | 2.053 | 1,495127 | 0,852399 |
| `PD_008` | 863 | 3,554524 | 2,902303 |
| `PD_009` | 93 | 33,141304 | 35,099728 |

## Google Chrome

O validador de leitura real foi ampliado para nove linhas. No Google Chrome,
ele confirmou `PD_004`–`PD_009`, seus nomes, valores calculados e o estado
“Implementada”. Nenhum cadastro ou dado foi modificado durante a validação.

PythonAnywhere não foi alterado.
