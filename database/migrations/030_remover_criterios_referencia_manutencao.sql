-- Migração 030: remove campos dispensados da Gestão do desenvolvimento.

BEGIN;

ALTER TABLE manutencao_sistema
    DROP CONSTRAINT ck_manutencao_conclusao,
    DROP COLUMN criterios_conclusao,
    DROP COLUMN referencia;

ALTER TABLE manutencao_sistema
    ADD CONSTRAINT ck_manutencao_conclusao CHECK (
        status_trabalho <> 'CONCLUIDO' OR concluido_em IS NOT NULL
    );

COMMIT;
