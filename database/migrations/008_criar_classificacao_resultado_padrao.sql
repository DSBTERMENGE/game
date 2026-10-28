-- Migração 008: classificação de cada resultado em cada grupo de padrões.

BEGIN;

ALTER TABLE padroes_subgrupo
    ADD CONSTRAINT uk_padroes_subgrupo_grupo_padrao
    UNIQUE (id_grupo, id_padrao);

CREATE TABLE resultado_classificacao_padrao (
    id_classificacao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_resultado BIGINT NOT NULL,
    id_grupo BIGINT NOT NULL,
    id_padrao BIGINT,
    estado_classificacao VARCHAR(30) NOT NULL,
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    calculado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_resultado_classificacao_resultado_grupo
        UNIQUE (id_resultado, id_grupo),
    CONSTRAINT fk_resultado_classificacao_resultado
        FOREIGN KEY (id_resultado) REFERENCES resultados (id_resultado)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_resultado_classificacao_grupo
        FOREIGN KEY (id_grupo) REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_resultado_classificacao_padrao_do_grupo
        FOREIGN KEY (id_grupo, id_padrao)
        REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_resultado_classificacao_estado
        CHECK (estado_classificacao IN (
            'PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA'
        )),
    CONSTRAINT ck_resultado_classificacao_estado_padrao CHECK (
        (estado_classificacao = 'PADRAO_IDENTIFICADO' AND id_padrao IS NOT NULL)
        OR
        (estado_classificacao = 'SEM_CORRESPONDENCIA' AND id_padrao IS NULL)
    ),
    CONSTRAINT ck_resultado_classificacao_versao
        CHECK (versao_calculo > 0)
);

CREATE INDEX ix_resultado_classificacao_grupo_padrao
    ON resultado_classificacao_padrao (id_grupo, id_padrao);

COMMENT ON TABLE resultado_classificacao_padrao IS
    'Classificação histórica de cada resultado em cada grupo de padrões.';
COMMENT ON COLUMN resultado_classificacao_padrao.id_padrao IS
    'Padrão identificado no grupo; nulo somente no estado SEM_CORRESPONDENCIA.';
COMMENT ON COLUMN resultado_classificacao_padrao.estado_classificacao IS
    'PADRAO_IDENTIFICADO ou SEM_CORRESPONDENCIA, conforme o classificador.';
COMMENT ON COLUMN resultado_classificacao_padrao.versao_calculo IS
    'Versão da função classificadora usada para produzir o registro.';
COMMENT ON COLUMN resultado_classificacao_padrao.calculado_em IS
    'Data e hora em que a classificação foi calculada.';

COMMIT;
