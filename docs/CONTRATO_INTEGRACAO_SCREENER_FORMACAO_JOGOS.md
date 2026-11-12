# Integração da formação de jogos com o Screener

O motor entrega cada combinação diretamente ao Screener, em fluxo. Não é
criada uma lista intermediária com todas as combinações e esta etapa não grava
jogos no banco de dados.

Antes da primeira combinação, o plano do funil é validado e sua configuração é
fotografada em JSON canônico com assinatura SHA-256. Uma fotografia alterada é
recusada. Cada combinação percorre os filtros na ordem fotografada e sai do
funil na primeira reprovação.

O relatório registra examinadas, reprovações por filtro, aprovadas e filtros
inativos. A igualdade `examinadas = reprovadas + aprovadas` é obrigatória.

## Estado atual

No banco real, a homologação está marcada como desatualizada pelo motivo
`HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`. A integração respeita essa trava.
Enquanto ela permanecer, o sistema não deve apresentar a estrutura existente
como Screener integral nem liberar a formação final de jogos.

A classificação das combinações aprovadas permanece reservada à etapa 26.6.
