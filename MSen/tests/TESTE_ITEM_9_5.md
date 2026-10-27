# Evidência de teste — Item 9.5

Data: 2026-10-26

## Implementação

- `database/padroes_repository.py`: listagem, cadastro inicial idempotente e
  atualização exclusiva dos campos estatísticos;
- `services/padroes.py`: cadastro e recálculo atômico dos três padrões;
- importação, inclusão e edição de resultados passaram a recalcular padrões na
  mesma transação das frequências;
- nome e descrição existentes são preservados durante o recálculo.

## Validação temporária

Um database efêmero recebeu seis resultados controlados. Foram confirmados:

- `PD_001`: 2 resultados, intervalo médio 15 e desvio zero;
- `PD_002`: 1 resultado, sem intervalo ou desvio;
- `PD_003`: 2 resultados, intervalo médio 20 e desvio zero;
- segundo recálculo sem duplicação de registros;
- preservação de um nome editado pelo usuário;
- remoção do database temporário ao final.

## PostgreSQL local

O serviço analisou 3.069 resultados e persistiu:

| Código | Nome | `num_oco` | `intervalo_medio` | `desv_padrao` |
|---|---|---:|---:|---:|
| `PD_001` | Duas dezenas sequenciais | 1.192 | 2,575147 | 1,995592 |
| `PD_002` | Três dezenas sequenciais | 92 | 33,527473 | 33,637806 |
| `PD_003` | Mais de três dezenas sequenciais | 5 | 680,500000 | 545,478460 |

Um segundo recálculo manteve exatamente três linhas e os mesmos valores.

## Regressão

- 5 testes unitários novos de persistência;
- 164 testes Python acumulados aprovados;
- 2 fluxos Chrome/PostgreSQL aprovados em 8,0 segundos;
- o fluxo de importação integrado confirmou três padrões recalculados
  automaticamente;
- nenhum database ou servidor temporário permaneceu;
- PythonAnywhere não foi acessado.

## Conclusão

Cadastro, persistência e recálculo automático estão funcionais e preservam os
campos editáveis. O Item 9.5 está concluído.
