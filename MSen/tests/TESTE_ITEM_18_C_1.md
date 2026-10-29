# Teste da subetapa 18-C.1 — contrato e inventário

Data da conferência: 29/10/2026.

## Escopo

Levantamento somente de leitura do modelo atual de padrões. Nenhuma tabela,
restrição, linha ou valor do PostgreSQL foi alterado.

## Contrato aprovado

Cada padrão cadastrado possui uma única linha de estado estatístico atual:

```text
percentual_ocorrencia = quantidade_ocorrencias / total_sorteios * 100
```

- `quantidade_ocorrencias`: número de resultados históricos que atendem ao
  padrão;
- `total_sorteios`: denominador histórico usado no cálculo;
- `percentual_ocorrencia`: incidência do padrão sobre todo o espaço amostral;
- um padrão com nenhuma ocorrência guarda quantidade `0` e percentual `0%`;
- cada recálculo atualiza a linha existente, sem criar histórico;
- o screener seleciona somente padrões com função Python aprovada e
  `percentual_ocorrencia < limite_configurado`;
- o complemento até 100% não é padrão, classe nem registro.

Há duas responsabilidades Python diferentes:

1. a análise histórica executa o detector sobre todos os sorteios e calcula o
   percentual do padrão;
2. o detector do screener recebe uma combinação e informa se ela atende ao
   padrão raro previamente selecionado.

## Estado atual do banco `games`

- Resultados históricos: **3.069**.
- Padrões cadastrados com detector: **9** (`PD_001` a `PD_009`).
- A tabela `padroes_subgrupo` possui atualmente `num_oco`, `intervalo_medio` e
  `desv_padrao`; ainda não possui denominador nem percentual armazenado.
- A tabela `resultado_classificacao_padrao` possui **3.069** linhas somente para
  `PG_001`:
  - `PADRAO_IDENTIFICADO`: **1.289**;
  - `SEM_CORRESPONDENCIA`: **1.780**.
- As 1.289 classificações válidas correspondem a `PD_001=1.192`, `PD_002=92`
  e `PD_003=5`.
- `id_padrao` é anulável e duas restrições CHECK admitem explicitamente
  `SEM_CORRESPONDENCIA`; isso precisará de migração, não apenas de DELETE.

## Impacto localizado

A expressão indevida aparece em **34 arquivos**:

| Área | Arquivos |
|---|---:|
| Banco e migração | 2 |
| Python de produção | 5 |
| Testes e relatórios de teste | 19 |
| Frontend e teste Chrome | 2 |
| Documentação funcional | 4 |
| Planejamento e continuidade | 2 |

Principais pontos de produção afetados:

- `database/migrations/008_criar_classificacao_resultado_padrao.sql`;
- `database/schema_postgresql.sql`;
- `MSen/src/msen/modelos/classificacao_padrao.py`;
- `MSen/src/msen/padroes/classificacao.py`;
- `MSen/src/msen/services/classificacao_padroes.py`;
- `MSen/src/msen/api/perfis_padroes.py`;
- `MSen/src/msen/screener/familia_padroes.py`;
- `MSen/src/msen/screener/fotografia.py`, que aceita `padrao_cod=None`;
- `MSen/src/msen/database/classificacoes_padrao_repository.py`, cujo contrato
  atual permite padrão nulo;
- `frontend/js/padroes.js`.

## Ordem segura das correções futuras

1. criar a migração dos campos estatísticos sem remover dados;
2. recalcular e conferir os percentuais dos nove padrões;
3. criar migração específica para apagar somente as 1.780 linhas indevidas e
   tornar `id_padrao` obrigatório nas classificações persistidas;
4. ajustar domínio, repositório, serviço, API, fotografia e frontend;
5. substituir os testes antigos por testes do contrato correto;
6. selecionar por consulta somente os padrões abaixo do limite configurado.

## Resultado

Inventário concluído. O banco permaneceu inalterado. A subetapa 18-C.2 pode
usar este documento como lista de impacto e critério de segurança.
