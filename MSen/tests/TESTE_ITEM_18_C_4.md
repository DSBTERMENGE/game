# Teste da subetapa 18-C.4 — remoção do modelo indevido

Data: 29/10/2026.

## Banco de dados

A migração `010_remover_sem_correspondencia.sql` foi validada sobre o backup
real anterior ao recálculo e depois aplicada ao banco local `games`.

Estado anterior no teste:

- ocorrências reais: 1.289;
- linhas indevidas: 1.780;
- total: 3.069.

Estado atual:

- `resultado_classificacao_padrao`: 1.289 linhas;
- todas as 1.289 linhas possuem `id_padrao`;
- `id_padrao` é `NOT NULL`;
- a coluna `estado_classificacao` não existe mais;
- as 1.780 linhas indevidas foram removidas;
- nenhuma ocorrência real foi perdida.

## Código

- removida a enumeração de estados do domínio;
- o repositório aceita somente padrão real obrigatório;
- o recálculo grava somente resultados que atendem a `PD_001`, `PD_002` ou
  `PD_003` e remove apenas ocorrências antigas que deixaram de corresponder;
- recálculos repetidos preservam os identificadores das 1.289 ocorrências;
- o perfil mantém 3.069 como denominador, mas apresenta somente os três padrões;
- API, fotografia e frontend não criam nem exibem classe complementar;
- quando nenhum padrão estudado é identificado na combinação, nada é
  persistido e o funil continua.

## Validações

- migração testada em restauração temporária e database removido;
- perfil real: PD_001=1.192, PD_002=92 e PD_003=5;
- API real respondeu HTTP 200 com somente `PD_001`, `PD_002` e `PD_003`;
- 493 testes Python aprovados;
- 35 testes JavaScript aprovados;
- 11 testes de fluxo no Google Chrome aprovados.

Migrações históricas e relatórios antigos continuam documentando o estado que
existia antes da correção. Os contratos funcionais vigentes foram marcados como
corrigidos e o código de produção não contém mais o modelo removido.
