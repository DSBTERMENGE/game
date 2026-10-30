# Teste da subetapa 20.7 — referências independentes

Data: 30/10/2026

## Estado

**Concluída.** Foram produzidas e conferidas as 3.800 referências independentes:
800 estatísticas, 1.200 geométricas e 1.800 de padrões.

## Proteção implementada

A migração 016 acrescentou:

- estado numérico `VALOR_IDENTIFICADO` ou `SEM_VALOR`;
- origem `HUMANO`, `IA` ou `TESTE_AUTOMATIZADO`;
- identificação do revisor;
- observação opcional;
- data da conferência.

O serviço de aprovação:

- não calcula o esperado usando a função aferida;
- grava referência e conferência atomicamente;
- protege referência já conferida contra sobrescrita;
- diferencia valor numérico ausente de referência pendente;
- valida se um padrão positivo pertence ao detector específico do critério;
- mantém o algoritmo desatualizado.

## PostgreSQL temporário

Foram aprovados:

- referência numérica comum;
- referência numérica legitimamente ausente;
- padrão identificado;
- padrão não identificado;
- origem, revisor e data obrigatórios;
- rejeição de sobrescrita;
- rejeição de padrão incompatível com o detector.

O database efêmero foi removido ao final.

## Aplicação da estrutura local

Backup anterior à migração:

- arquivo: `MSen/dados/backups/games_pre_referencias_20_7_20261030_041037.dump`;
- tamanho: 282.763 bytes;
- SHA-256: `60E520113CD5962C4FC026B6566B1530A3F1022D20AF63AA7389CDAB4DC653B2`;
- catálogo: 165 itens.

Somente a migração 016 foi aplicada. As 3.800 avaliações foram preservadas, sem
preenchimento ou aprovação automática.

## Oráculos independentes

Foi criado um oráculo separado para as quatro estatísticas e os nove detectores
de padrões. O arquivo não importa `msen.calculos`, `msen.geometria` nem
`msen.padroes`. Casos manuais conhecidos foram usados para verificar soma,
média, mediana, desvio e os nove padrões exclusivos.

Backup anterior à carga parcial:

- arquivo:
  `MSen/dados/backups/games_pre_gabarito_parcial_20_7_20261030_041205.dump`;
- tamanho: 284.926 bytes;
- SHA-256: `3865F98AD3E240DF38250F72FD55B8E00974AEDB52EDCA0F3E0001AE9A188666`;
- catálogo: 167 itens.

Resultado no `games`:

- estatística: 800 referências conferidas;
- padrões: 1.800 referências conferidas;
- geometria: 1.200 referências conferidas;
- total conferido: 3.800;
- total pendente: zero;
- referências sem valor: zero;
- metadados inválidos: zero.

## Oráculo geométrico

Com autorização do usuário, foi instalado o Shapely 2.2.0, apoiado pelo GEOS,
como dependência exclusiva de desenvolvimento/teste. O oráculo constrói as
coordenadas diretamente das dezenas e calcula extensão, perímetro, regiões,
área e centroide sem importar `msen.geometria` nem reutilizar seus resultados.
Casos manuais simples, cruzado e colinear verificaram o oráculo antes da carga.

O Shapely não participa do cálculo de produção nem do Screener. Sua finalidade
nesta etapa é somente produzir uma segunda resposta independente para aferir as
funções reais nas subetapas posteriores.

Backup anterior à carga geométrica:

- arquivo:
  `MSen/dados/backups/games_pre_gabarito_geometrico_20_7_20261030_042817.dump`;
- tamanho: 289.896 bytes;
- SHA-256: `BCECF35A18771BD07D20C3DDE860895C46A7741940A40F18D176F391798FCC43`;
- catálogo: 167 itens.

## Regressão

Resultado: **541 testes Python aprovados**. Foram emitidos somente três
`ResourceWarning` preexistentes sobre arquivos de frontend abertos por testes;
não houve falha.

## Resultado

A infraestrutura e as 3.800 referências estão aprovadas. A subetapa 20.7 está
encerrada. O algoritmo permanece desatualizado porque esta etapa gravou somente
os esperados; as funções reais ainda serão executadas e comparadas nas
subetapas 20.8 a 20.10, cada qual mediante autorização própria.
