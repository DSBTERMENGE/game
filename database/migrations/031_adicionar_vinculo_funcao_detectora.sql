-- Migração 031: prepara a associação direta entre padrões e funções detectoras.
--
-- Esta migração é exclusivamente aditiva. O preenchimento das novas colunas
-- será realizado e conferido em uma etapa posterior.

BEGIN;

ALTER TABLE padroes_subgrupo
    ADD COLUMN funcao_detectora VARCHAR(500),
    ADD CONSTRAINT ck_padroes_funcao_detectora_preenchida CHECK (
        funcao_detectora IS NULL OR BTRIM(funcao_detectora) <> ''
    );

ALTER TABLE criterios_validacao
    ADD COLUMN id_padrao BIGINT,
    ADD CONSTRAINT fk_criterios_validacao_padrao_grupo FOREIGN KEY (
        id_grupo, id_padrao
    ) REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    ADD CONSTRAINT uk_criterios_validacao_id_padrao UNIQUE (id_padrao),
    ADD CONSTRAINT ck_criterios_validacao_id_padrao_categoria CHECK (
        id_padrao IS NULL OR categoria = 'PADRAO'
    );

COMMIT;
