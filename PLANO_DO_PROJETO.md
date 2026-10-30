# Projeto Game / MSen — visão vigente

Atualizado em 2026-10-30.

O roteiro operacional, com autorização por subetapa, está em
`PLANO_ETAPAS_E_TESTES.md`. O funcionamento implementado está em
`docs/funcionamento.md` e o mapa documental em `docs/INDICE_DOCUMENTACAO.md`.

## Finalidade

Importar, armazenar e analisar resultados da Mega-Sena; construir perfis
estatísticos, geométricos e de padrões; homologar independentemente todas as
funções usadas; e selecionar combinações somente quando o conjunto estiver
integralmente aprovado e reconciliado.

## Arquitetura atual

- frontend HTML/CSS/JavaScript em `frontend/`;
- API Flask e regras Python em `MSen/src/msen/`;
- PostgreSQL versionado por `database/schema_postgresql.sql` e migrações;
- configuração por variáveis de ambiente, sem credenciais no repositório;
- testes Python, Node, Chromium e PostgreSQL temporário.

## Capacidades concluídas

- importação incremental de `.xlsx`, inclusão, edição e consulta;
- cálculos estatísticos por resultado e análise geométrica;
- painel gráfico, voo, mancha e configuração visual;
- CRUD de grupos e padrões;
- classificação e incidência histórica de nove padrões em três grupos;
- perfis estatísticos e geométricos atuais;
- Screener oficial em três famílias com amostra protegida de 5.000;
- Validação e auditoria com 200 amostras e 19 critérios;
- referências independentes, comparação `S/N`, relatório e exportação;
- trava do Screener por homologação, perfis, assinaturas e cobertura.
- módulo de frequência das dezenas com histórico concurso a concurso, eventos
  simples/2VS/3VS, gráficos, simulação e avaliação de assertividade.

## Estado operacional

No banco local `games`, existem 3.069 resultados, 19 critérios, 3.800
avaliações aprovadas e dez perfis atuais. O estado global continua bloqueado
por `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`; o Screener real deve recusar a
execução enquanto o flag não for liberado por procedimento controlado.

## Limites e próximos ciclos

- processamento integral de 50.063.860 combinações permanece bloqueado;
- o backtest geral do Screener ainda será construído; o estudo de frequência já
  preserva cortes sem informação futura e avalia retornos posteriores;
- publicação no PythonAnywhere continua adiada;
- modal de andamento no Screener é etapa posterior;
- commit e push somente mediante autorização específica.

## Regras permanentes

1. O arquivo de entrada não é alterado.
2. O frontend nunca acessa diretamente o banco.
3. Campos derivados são calculados pelo Python de produção.
4. Toda alteração de banco recebe migração nova.
5. Função nova ou alterada não entra no Screener sem 200 aprovações.
6. Perfis correntes usam todos os resultados; corte temporal pertence ao
   backtest.
7. Nenhuma credencial, backup ou dado temporário deve entrar no Git.
8. Cada subetapa exige autorização, teste, evidência e continuidade.
