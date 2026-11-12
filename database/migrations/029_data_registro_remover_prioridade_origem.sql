BEGIN;

ALTER TABLE manutencao_sistema
    ADD COLUMN data_registro DATE;

UPDATE manutencao_sistema
SET data_registro = criado_em::date
WHERE data_registro IS NULL;

DROP INDEX ix_manutencao_filtros;

ALTER TABLE manutencao_sistema
    ALTER COLUMN data_registro SET NOT NULL,
    DROP CONSTRAINT ck_manutencao_prioridade,
    DROP CONSTRAINT ck_manutencao_origem,
    DROP COLUMN prioridade,
    DROP COLUMN origem_registro;

CREATE INDEX ix_manutencao_filtros
    ON manutencao_sistema (tipo, status_trabalho, status_publicacao);

ALTER TABLE manutencao_sistema_historico
    DROP CONSTRAINT ck_manutencao_historico,
    DROP COLUMN origem_evento;

ALTER TABLE manutencao_sistema_historico
    ADD CONSTRAINT ck_manutencao_historico CHECK (
        tipo_evento IN (
            'CRIADO', 'ATUALIZADO', 'ARQUIVADO', 'DESARQUIVADO',
            'REABERTO', 'STATUS_ALTERADO', 'PUBLICACAO_ALTERADA'
        )
        AND versao_registro > 0
        AND jsonb_typeof(dados_json) = 'object'
    );

COMMIT;
