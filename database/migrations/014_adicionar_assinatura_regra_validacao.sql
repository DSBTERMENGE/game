-- Migração 014: distingue a regra matemática da implementação Python.

BEGIN;

ALTER TABLE criterios_validacao
    ADD COLUMN assinatura_regra CHAR(64) NOT NULL;

ALTER TABLE criterios_validacao
    ADD CONSTRAINT ck_criterios_validacao_assinatura_regra
    CHECK (assinatura_regra ~ '^[0-9a-f]{64}$');

COMMENT ON COLUMN criterios_validacao.assinatura_regra IS
    'SHA-256 automático da definição matemática e semântica do critério.';

COMMIT;
