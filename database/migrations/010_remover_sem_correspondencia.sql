-- Migração 010: persistir somente ocorrências reais de padrões.

BEGIN;

DELETE FROM resultado_classificacao_padrao
WHERE estado_classificacao = 'SEM_CORRESPONDENCIA';

ALTER TABLE resultado_classificacao_padrao
    DROP CONSTRAINT ck_resultado_classificacao_estado_padrao,
    DROP CONSTRAINT ck_resultado_classificacao_estado,
    ALTER COLUMN id_padrao SET NOT NULL,
    DROP COLUMN estado_classificacao;

COMMENT ON TABLE resultado_classificacao_padrao IS
    'Ocorrências reais de padrões identificadas nos resultados históricos.';
COMMENT ON COLUMN resultado_classificacao_padrao.id_padrao IS
    'Padrão efetivamente identificado no resultado e no grupo.';

COMMIT;
