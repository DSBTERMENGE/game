# Evidência do Item 11.6 — linhas subjacentes e integração visual

Data: 2026-10-27.

## Regra esclarecida

O usuário confirmou que o padrão é o equivalente vertical das sequências
horizontais: as dezenas devem estar na mesma coluna e em linhas imediatamente
subjacentes. Assim, `25` e `35` formam um par vertical; `25` e `45`, sem `35`,
não formam.

Contrato, detectores, testes e documentação foram corrigidos. A classificação
continua exclusiva pela maior sequência vertical: exatamente duas, exatamente
três ou mais de três dezenas.

## Validação e banco

- 44 testes direcionados aprovados;
- persistência correta confirmada em PostgreSQL temporário e database removido;
- 205 testes Python aprovados;
- 22 testes de frontend aprovados;
- 8 fluxos Chrome aprovados;
- backup adicional antes da correção local:
  `games_pre_recalculo_colunas_20261027_090949.dump`;
- tamanho do backup: 117.935 bytes;
- SHA-256: `688DC50925E583007A205566F29D2038992A8E34CD7E372D1FE423286D636D4F`.

O `games` preservou 3.069 resultados e passou a conter:

| Código | Ocorrências | Intervalo médio | Desvio-padrão |
|---|---:|---:|---:|
| `PD_004` | 1.037 | 2,960425 | 2,387099 |
| `PD_005` | 66 | 45,969231 | 42,006948 |
| `PD_006` | 4 | 696,666667 | 373,443734 |

Os nomes e as descrições foram alinhados à expressão “linhas subjacentes”. O
servidor local foi reiniciado no PID 8556. A API marcou os seis detectores como
implementados e a leitura real no Google Chrome confirmou seis linhas, textos e
estatísticas corretos. PythonAnywhere não foi alterado.
