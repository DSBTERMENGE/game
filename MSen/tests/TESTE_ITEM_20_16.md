# Evidência — subetapa 20.16

Data: 2026-10-30.

## Trava do Screener

O ponto de entrada do Screener agora exige, antes do plano executável:

- estado global atualizado;
- catálogo ativo idêntico ao registro Python de produção;
- assinatura de função e regra atuais;
- todas as amostras ativas conferidas, executadas e `S`;
- zero pendências, divergências ou assinaturas executadas antigas;
- dez perfis operacionais com a quantidade atual de resultados;
- cobertura de todos os critérios estatísticos e geométricos;
- cobertura exata dos padrões homologados selecionados pelo limite vigente.

Testes independentes confirmaram bloqueio para função nova, alterada,
pendente, reprovada, filtro ausente/extra, perfil antigo e estado global falso.
O cenário integralmente aprovado foi aceito.

## Funções de produção

`execucao_validacao` resolve cada critério exclusivamente por
`criar_registro_criterios_producao()`. A regressão conferiu as três categorias,
as assinaturas calculadas do código-fonte e a recusa de catálogo divergente.

## PostgreSQL temporário

Dois bancos efêmeros, criados e removidos pelos validadores seguros, confirmaram:

- 200 amostras e 3.800 avaliações, sem duplicar dezenas;
- carga idempotente e amostra adicional preservada;
- novo resultado incorporado aos dez perfis atuais;
- padrões e classificações recalculados com o denominador novo;
- assinatura do conjunto de resultados alterada;
- valores esperados, calculados e aprovação da homologação preservados.

## Estado real de `games`

- Critérios ativos: 19.
- Perfis operacionais: 10.
- Resultados no estado e na tabela: 3.069.
- Estado: desatualizado.
- Motivo: `HOMOLOGACAO_CONCLUIDA_AGUARDANDO_COBERTURA`.
- Resultado da trava: `ALGORITMO_DESATUALIZADO`.

Nenhum flag foi forçado e nenhum dado de produção foi alterado.

## Suítes

- Python: 567 testes aprovados.
- Node: 37 testes aprovados.
- Chromium: 20 fluxos aprovados.
- Nada foi publicado externamente.

Próxima subetapa: 20.17, somente após autorização específica.
