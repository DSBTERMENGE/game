# Índice da documentação vigente

Este índice identifica onde procurar cada tipo de informação. Ele evita tratar
rascunhos, protótipos e relatórios antigos como descrição atual do sistema.

## Documentos canônicos

| Assunto | Documento |
|---|---|
| Execução autorizada, etapas e testes | `PLANO_ETAPAS_E_TESTES.md` |
| Visão geral e arquitetura do projeto | `PLANO_DO_PROJETO.md` |
| Funcionamento atual explicado de ponta a ponta | `docs/funcionamento.md` |
| Decisões aprovadas e suas datas | `notas/decisoes.md` |
| Funcionalidades existentes e pendentes | `notas/funcionalidades.md` |
| Ponto exato de retomada entre sessões | `CONTINUIDADE_IA.md` |
| Estrutura consolidada do PostgreSQL | `database/schema_postgresql.sql` |
| Histórico incremental do PostgreSQL | `database/migrations/` |
| Contrato da homologação das funções | `docs/CONTRATO_HOMOLOGACAO_FUNCOES.md` |
| API da Validação e auditoria | `docs/API_VALIDACAO.md` |
| API da Frequência das dezenas | `docs/API_FREQUENCIAS.md` |
| Contrato da Frequência das dezenas | `docs/CONTRATO_FREQUENCIA_DEZENAS.md` |

## Documentos técnicos especializados

- `docs/API_*.md`: contratos das APIs existentes;
- `docs/CONTRATO_*.md`: decisões técnicas de uma funcionalidade específica;
- `docs/DICIONARIO_DADOS_RESULTADOS.md`: significado dos campos de resultados;
- `docs/MODELO_POSTGRESQL.md` e `docs/banco-de-dados.md`: explicação humana do
  modelo, subordinada ao esquema e às migrações vigentes;
- `docs/codigo-python.md`: organização e responsabilidades do backend;
- `MSen/tests/TESTE_ITEM_*.md`: evidência do que foi testado em cada subetapa.

## Documentos históricos ou substituídos

- `docs/PLANO_DO_PROJETO_HISTORICO.md`: checklist do planejamento inicial,
  substituído pela visão vigente da raiz;
- `docs/funcionamento_historico_ate_etapa_19.md`: narrativa planejada anterior,
  substituída pelo funcionamento vigente;
- `docs/CONTRATO_CLASSIFICACAO_GRUPOS.md`: contrato histórico da classificação
  com `SEM_CORRESPONDENCIA`; a migração 010 removeu esse registro da
  classificação persistida;
- `docs/PROTOTIPO_SCREENER_TRES_NIVEIS.md` e
  `docs/INTERFACE_SCREENER_EXTENSIVEL.md`: projeto/evidência da construção do
  Screener, subordinados ao código e ao funcionamento vigente;
- `docs/criterios_selecao_combinaçoes.txt`: consolidação histórica de decisões;
- `docs/PLANO_FUNCIONALIDADES.txt`: levantamento inicial em texto simples,
  substituído pelo plano operacional da raiz;
- `docs/banco-de-dados.md`: plano inicial do banco, substituído pelo esquema e
  pelas migrações vigentes;
- `docs/CONTRATO_SCREENER.md`: contrato da fase experimental anterior ao
  Screener oficial e à trava de homologação;
- `MSen/tests/TESTE_ITEM_*.md`: evidências imutáveis de cada momento, não
  descrição necessariamente vigente.

O estado `SEM_CORRESPONDENCIA` permanece válido somente dentro de
`avaliacoes_validacao` como resultado de classificador sem subgrupo; ele não
voltou a ser uma linha da classificação histórica.

## Precedência em caso de divergência

1. comportamento confirmado pelo código e pelos testes atuais;
2. `PLANO_ETAPAS_E_TESTES.md` e decisões aprovadas mais recentes;
3. contrato específico vigente;
4. `docs/funcionamento.md`;
5. documentos históricos, protótipos e relatórios antigos.

Uma divergência não deve ser aceita silenciosamente. A etapa em andamento deve
reconciliar os documentos canônicos e registrar a correção.

## Regra de manutenção

Cada subetapa continua atualizando plano, evidência e continuidade. Ao fechar
uma etapa funcional, é obrigatório revisar também:

- `docs/funcionamento.md`;
- `notas/decisoes.md`;
- `notas/funcionalidades.md`;
- documentos de banco e API afetados;
- este índice, caso surja ou deixe de existir um documento canônico.

Na Etapa 20, essa reconciliação integral pertence à subetapa 20.17.
