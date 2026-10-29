# Teste da subetapa 18-C.3 — recálculo histórico dos padrões

Data: 29/10/2026.

## Procedimento

As funções oficiais de `PD_001` a `PD_009` percorreram os 3.069 resultados. O
repositório atualizou a linha existente de cada padrão com quantidade, total de
sorteios, percentual, intervalo médio e desvio-padrão.

Antes do banco local, o processo foi executado sobre uma restauração temporária
do backup. O database temporário foi removido ao final.

## Resultado persistido

| Padrão | Ocorrências | Total | Percentual |
|---|---:|---:|---:|
| PD_001 | 1.192 | 3.069 | 38,840013% |
| PD_002 | 92 | 3.069 | 2,997719% |
| PD_003 | 5 | 3.069 | 0,162920% |
| PD_004 | 1.037 | 3.069 | 33,789508% |
| PD_005 | 66 | 3.069 | 2,150538% |
| PD_006 | 4 | 3.069 | 0,130336% |
| PD_007 | 2.053 | 3.069 | 66,894754% |
| PD_008 | 863 | 3.069 | 28,119909% |
| PD_009 | 93 | 3.069 | 3,030303% |

## Segurança e verificações

- Backup anterior ao recálculo:
  `MSen/dados/backups/games_pre_recalculo_padroes_20261029_072519.dump`;
- tamanho: 252.759 bytes;
- SHA-256:
  `F5E783B3EEC37A0E772E3452E0533F57E537501B8387EBA6D35E15D2673B824C`;
- continuam existindo exatamente nove linhas e nove códigos de padrão;
- nenhuma das nove linhas diverge da fórmula percentual;
- o total de resultados permaneceu 3.069;
- intervalos e desvios anteriores foram reconciliados pelas mesmas funções;
- as 1.780 classificações indevidas não foram removidas nesta subetapa;
- regressão: 492 testes Python aprovados.

Padrões com zero ocorrência são suportados e gravam 0%, conforme teste da
18-C.2. Nenhum dos nove padrões atuais resultou em zero no histórico disponível.
