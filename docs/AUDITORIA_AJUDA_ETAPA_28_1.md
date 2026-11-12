# Auditoria das fontes da Ajuda — Etapa 28.1

Data da auditoria: 11/11/2026.

## 1. Escopo

Esta auditoria identifica as fontes que deverão sustentar a futura Ajuda central
do Game. Ela não altera telas, cálculos, banco de dados nem os textos de Ajuda
já exibidos pelo sistema.

## 2. Decisão de navegação já aprovada

Quando a página central for implementada em etapa posterior, `Ajuda` será o
último item do menu principal, alinhado à esquerda e situado depois de
`Gestão do desenvolvimento`. A Etapa 28.1 apenas registra essa decisão; ainda
não cria nem reposiciona itens do menu.

## 3. Ordem de confiança das fontes

Em caso de divergência, a conferência deverá seguir esta ordem:

1. código em execução, esquema atual do PostgreSQL e testes automatizados;
2. decisões recentes registradas em `PLANO_ETAPAS_E_TESTES.md` e
   `notas/decisoes.md`;
3. contrato específico vigente do módulo em `docs/`;
4. `docs/funcionamento.md`;
5. documentos identificados como históricos e evidências de etapas antigas.

Os modais de Ajuda atuais são material editorial aproveitável, mas não são
prova isolada da regra funcional. Antes da migração, cada afirmação deverá ser
comparada com as fontes dos itens 1 a 4.

## 4. Inventário por página

| Página | Ajuda local atual | Principais fontes técnicas para conferência |
| --- | --- | --- |
| Painel (`index.html`) | Não | `frontend/js/main.js`, `api/resultados.py`, testes de resultados |
| Cadastros (`cadastros.html`) | Não | páginas de Grupos e Padrões e suas APIs específicas |
| Grupos e subgrupos (`grupos-padroes.html`) | Não | `api/grupos_padroes.py`, repositórios e testes de grupos |
| Padrões (`padroes.html`) | Não | `api/padroes.py`, `api/perfis_padroes.py` e testes correspondentes |
| Distribuições (`distribuicoes.html`) | Não | `api/distribuicoes.py`, serviços de distribuição e seus testes |
| Screener (`screener.html`) | Não | `api/screener.py`, `api/screener_extensivel_service.py`, contratos e testes do Screener |
| Validação e auditoria (`auditoria.html`) | Não | `api/validacao.py`, `api/execucoes_validacao.py`, `docs/API_VALIDACAO.md` e testes de homologação |
| Frequência das dezenas (`frequencias.html`) | Sim, modal próprio | `api/frequencias.py`, serviços e repositórios de frequência, `docs/CONTRATO_FREQUENCIA_DEZENAS.md` e testes da Etapa 22 |
| Gráficos de frequência (`graficos-frequencias.html`) | Sim, ajuda geral e contextual | `frontend/js/graficos-frequencias.js`, API e contrato de frequência |
| Seleção de dezenas (`selecao-dezenas.html`) | Sim, modal próprio | `api/selecao_dezenas.py`, serviços/repositórios do módulo, `docs/CONTRATO_SELECAO_DEZENAS.md`, `docs/CONTRATO_BACKTEST_SELECAO_DEZENAS.md` e testes da Etapa 23 |
| Gestão do desenvolvimento (`gestao-desenvolvimento.html`) | Sim, modal próprio | `api/gestao_desenvolvimento.py`, serviço/repositório, migração 028 e testes da Etapa 27 |

Resultado: quatro das onze páginas possuem algum conteúdo local de Ajuda e
sete não possuem. O conteúdo existente está distribuído entre HTML e
JavaScript, sem página central, busca geral ou links diretos por assunto.

## 5. Fontes documentais classificadas

### Vigentes, sujeitas à conferência técnica

- `docs/INDICE_DOCUMENTACAO.md`: define a precedência documental.
- `docs/funcionamento.md`: visão funcional consolidada.
- contratos específicos, principalmente os de Frequência, Seleção de dezenas,
  Backtest e homologação do Screener;
- documentos `API_*.md`, arquitetura, esquema do banco e plano de testes;
- `PLANO_ETAPAS_E_TESTES.md`, `CONTINUIDADE_IA.md` e
  `notas/decisoes.md` para decisões recentes.

### Históricas

- `docs/funcionamento_historico_ate_etapa_19.md`;
- `docs/PLANO_DO_PROJETO_HISTORICO.md`;
- protótipos, contratos revogados e arquivos `TESTE_ITEM_*` usados como
  evidência de uma etapa já encerrada.

Essas fontes ajudam a explicar a evolução, mas não devem definir sozinhas o
funcionamento atual.

### Incompletas ou que exigem reconciliação

- os modais locais não abrangem todo o sistema e duplicam conceitos;
- `docs/funcionamento.md` informa no cabeçalho atualização em 30/10/2026,
  embora contenha módulos e decisões posteriores; seu conteúdo é útil, mas o
  metadado de atualização está defasado;
- não há glossário oficial único para concurso-alvo, corte, fotografia,
  geração, homologação, cobertura, teste e aplicação do Screener;
- não há matriz central indicando, para cada operação, o que é gravado no
  PostgreSQL e o que existe apenas durante a consulta.

## 6. Pontos históricos confirmados

A leitura do código, dos contratos e do banco `games` confirmou:

- existem 3.069 resultados, numerados continuamente de 1 a 3.069;
- a configuração vigente de frequência começa no concurso 1 e usa tamanho
  inicial 500;
- a primeira fotografia acumulada da frequência corresponde ao concurso 500;
- as fotografias vigentes abrangem os concursos 500 a 3.069, totalizando
  2.570 cortes;
- o histórico de frequência possui 462.600 avaliações, coerente com
  2.570 concursos, 60 dezenas e três tipos de evento;
- o backtest da Seleção de dezenas aceita concurso inicial a partir de 500;
- no alvo 500, o cálculo da Seleção usa apenas os resultados conhecidos até o
  corte 499, isto é, os concursos 1 a 499.

Portanto, são três referências diferentes que a Ajuda deverá nomear sem
misturar:

1. **início dos resultados:** concurso 1;
2. **primeira fotografia acumulada da frequência:** concurso 500, calculada a
   partir da base iniciada no concurso 1;
3. **primeiro alvo permitido no backtest da Seleção:** concurso 500, usando o
   corte histórico 499.

Fontes principais: `configuracao_frequencia.py`,
`backtest_selecao_dezenas.py`, `fonte_backtest_repository.py`, API da Seleção,
contratos de Frequência e Backtest e consultas somente de leitura ao banco.

## 7. Lacunas e contradições a resolver nas próximas subetapas

1. Definir nomenclatura oficial para `Screener` ou `Preparação do Screener` e
   separar claramente teste com 5.000 combinações de aplicação integral.
2. Explicar a diferença entre a amostra de 5.000, o universo
   `C(60,6) = 50.063.860` e as combinações produzidas pelas dezenas selecionadas.
3. Documentar o motivo técnico de cada bloqueio do Screener e traduzir as
   mensagens para orientação operacional ao usuário.
4. Confirmar, módulo por módulo, quais atualizações são incrementais, quais
   recalculam dados e quais preservam fotografias anteriores.
5. Uniformizar os termos usados na Seleção de dezenas, especialmente previsão,
   registro do screener, concurso-alvo, corte e formação de jogos.
6. Definir se `Seleção de dezenas` continuará como nome da página quando o
   fluxo de combinações estiver completo.
7. Criar um mapa explícito de persistência, confirmação, alteração,
   imutabilidade e exclusão para cada cadastro e estudo.
8. Atualizar a data e reconciliar o conteúdo de `docs/funcionamento.md` antes
   de promovê-lo como base editorial da Ajuda central.

## 8. Encaminhamento

A Etapa 28.1 fornece o inventário e as evidências. A próxima subetapa prevista
é a 28.2, que deverá propor a árvore dos assuntos, o vocabulário oficial e o
modelo editorial. Ela depende de nova autorização e não está incluída neste
trabalho.
