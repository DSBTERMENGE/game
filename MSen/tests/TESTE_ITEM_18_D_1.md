# Inventário da subetapa 18-D.1 — consolidação do screener

Data: 2026-10-29

## Objetivo

Identificar todos os componentes dos screeners antigo, protótipo e atual antes
de remover qualquer elemento. Esta subetapa foi somente de leitura e
documentação: páginas, APIs, banco e comportamento não foram alterados.

## Diagnóstico confirmado

Existem três apresentações diferentes no repositório:

1. `screener.html`: funil antigo de oito filtros, quadro simples e validação
   humana apenas local;
2. `screener-prototipo.html`: protótipo visual fictício do futuro funil;
3. `screener-extensivel.html`: funil real em três níveis, com estatística,
   geometria e padrões históricos.

Os dois screeners executáveis possuem APIs e JavaScript independentes:

- antigo: `GET /api/screener/quadro`, `screener.js` e `quadro_ativo.py`;
- atual: `POST /api/screener/quadro-extensivel`,
  `screener-extensivel.js` e `screener_extensivel_service.py`.

## Destino definido por componente

| Componente | Destino | Motivo |
| --- | --- | --- |
| Conteúdo de `screener-extensivel.html` | migrar para `screener.html` | será a única página oficial |
| `screener-extensivel.js` | migrar/renomear para o script oficial | contém a interface validada do funil atual |
| `screener-extensivel-contrato.js` | manter, com nome genérico avaliado na migração | valida o fechamento dos três níveis |
| `POST /api/screener/quadro-extensivel` | migrar para a rota oficial do screener | evitar nome transitório na API |
| `screener.html` antigo | substituir | não continuará acessível ao usuário |
| `screener.js` antigo | remover após a migração | atende somente o quadro e a validação antigos |
| `GET /api/screener/quadro` antigo | substituir pela API oficial atual | atende somente a interface antiga |
| `quadro_ativo.py` | remover após retirar API e testes antigos | monta o quadro antigo e casos provisórios |
| tabela e seletores de validação humana | remover | pertencem a um experimento local, não à auditoria futura |
| `screener-prototipo.html`, seu JS e dados fictícios | remover da produção | o funil real já substituiu o protótipo |
| testes do funil atual | migrar para os nomes e URLs oficiais | preservam o contrato validado |
| testes do funil antigo e do protótipo | retirar ou converter | não devem perpetuar interfaces removidas |
| documentos históricos e relatórios antigos | preservar como histórico | registram a evolução já executada |
| documentos operacionais atuais | atualizar | devem usar apenas o nome `Screener` |

## Núcleo antigo que ainda é necessário

O serviço atual executa o funil anterior sobre a mesma amostra para preencher a
comparação `anterior x novo`. Para isso usa diretamente:

- `criar_adaptadores_ativos(configuracao)`;
- `executar_funil(amostra, adaptadores)`;
- políticas e adaptadores do primeiro funil.

Esse núcleo de cálculo não pode ser apagado junto com a tela antiga enquanto a
comparação permanecer no relatório. Ele será mantido como **referência interna
de comparação**, sem página, menu ou API pública própria.

O funil atual não depende de `quadro_ativo.py`, dos casos de validação humana,
de `screener.js` antigo nem do protótipo fictício.

## Referências que exigem atualização

- configuração da aplicação em `api/app.py`, que injeta os dois executores;
- blueprint `api/screener.py`, atualmente com duas rotas;
- testes Python da API e de `gerar_quadro_screener`;
- testes JavaScript e Chrome das três apresentações;
- testes integrados que acessam `/screener-extensivel.html`;
- barras de navegação das páginas principais;
- documentos com os termos `novo funil`, `Screener atual` e
  `Screener extensível`.

## Página futura de auditoria

A página `/auditoria.html` será criada separadamente na 18-D.4. Ela não herdará
os seletores nem os dados provisórios do screener antigo. Nesta etapa terá
somente navegação, título e aviso de construção; a funcionalidade pertence à
Etapa 20.

## Resultado

Não existe função de produção necessária ao screener atual somente na tela ou
na validação humana antigas. A única dependência relevante é o núcleo do funil
anterior usado internamente para comparação, que deverá ser preservado.

Inventário aprovado tecnicamente, sem alteração de banco ou comportamento.
