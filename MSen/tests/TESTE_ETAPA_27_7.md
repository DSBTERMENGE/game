# Evidência da etapa 27.7

Data: 11/11/2026.

## Cadastro migrado

O primeiro reaproveitamento fora da Gestão do desenvolvimento foi aplicado à
inclusão de configurações da Seleção de dezenas.

A auditoria confirmou que esse cadastro é imutável e possui a ação própria
`Analisar configuração`. Por isso, não recebeu edição nem arquivamento. Foram
reutilizadas somente as regras compatíveis: validação, conferência anterior ao
POST, cancelamento sem gravação, bloqueio de repetição enquanto salva e
preservação da conferência quando o servidor falha.

O fluxo comum está em `frontend/js/fluxo-cadastro-confirmado.js`. Grupos,
subgrupos e padrões não foram modificados nesta etapa.

## Validação

- 3 testes unitários específicos do fluxo comum aprovados;
- 113 testes unitários do frontend aprovados no total;
- 8 fluxos Playwright da Seleção de dezenas aprovados no Chrome;
- 723 testes Python aprovados;
- o teste de navegador confirmou zero POST antes da confirmação e somente um
  POST depois dela;
- nenhuma migração ou alteração de dados foi necessária.

O teste do navegador usou a porta alternativa 4174 porque a porta 4173 estava
ocupada pelo servidor local do usuário. O processo existente não foi encerrado.

## Limites respeitados

- nenhuma publicação foi executada;
- nenhum commit ou push foi executado;
- grupos, subgrupos e padrões permanecem com seus fluxos atuais;
- cada futura migração continua dependendo de nova análise e autorização.
