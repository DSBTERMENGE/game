# Evidência do Item 15.2 — contrato de detecção e exclusão

Data: 2026-10-27.

O contrato foi registrado em `docs/CONTRATO_DETECCAO_EXCLUSAO.md` e definiu:

- separação entre detector, política e modo de execução;
- denominador como todos os resultados válidos avaliados pela mesma versão;
- comparação exata e exibição com seis casas/`ROUND_HALF_UP`;
- operador inclusivo `percentual <= tolerância`, ainda sem valor aprovado;
- modos inativo, sombra e ativo, sem transição automática;
- falha conservadora: dado ausente ou inconsistente nunca exclui;
- justificativa auditável obrigatória para cada decisão;
- intervalos e desvios fora da política percentual até contrato próprio.

Nenhum padrão piloto, tolerância ou exclusão foi aprovado. Não houve alteração
de código, configuração ou banco de dados.
