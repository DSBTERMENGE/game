-- Migração 015: perfis numéricos atuais usados pelo algoritmo de seleção.

BEGIN;

CREATE TABLE perfis_operacionais_atuais (
    codigo VARCHAR(80) PRIMARY KEY,
    categoria VARCHAR(20) NOT NULL,
    quantidade_resultados BIGINT NOT NULL,
    quantidade_com_valor BIGINT NOT NULL,
    quantidade_ausente BIGINT NOT NULL,
    media NUMERIC,
    desvio_padrao_populacional NUMERIC,
    minimo NUMERIC,
    maximo NUMERIC,
    calculado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_perfis_operacionais_codigo CHECK (BTRIM(codigo) <> ''),
    CONSTRAINT ck_perfis_operacionais_categoria
        CHECK (categoria IN ('ESTATISTICA', 'GEOMETRIA')),
    CONSTRAINT ck_perfis_operacionais_quantidades CHECK (
        quantidade_resultados >= 0
        AND quantidade_com_valor >= 0
        AND quantidade_ausente >= 0
        AND quantidade_com_valor + quantidade_ausente = quantidade_resultados
    ),
    CONSTRAINT ck_perfis_operacionais_valores CHECK (
        (quantidade_com_valor = 0 AND media IS NULL
            AND desvio_padrao_populacional IS NULL
            AND minimo IS NULL AND maximo IS NULL)
        OR
        (quantidade_com_valor > 0 AND media IS NOT NULL
            AND desvio_padrao_populacional IS NOT NULL
            AND minimo IS NOT NULL AND maximo IS NOT NULL AND minimo <= maximo)
    )
);

COMMENT ON TABLE perfis_operacionais_atuais IS
    'Resumo substituível dos perfis numéricos calculados sobre todos os resultados atuais.';
COMMENT ON COLUMN perfis_operacionais_atuais.quantidade_ausente IS
    'Valores nulos legítimos, como centro de gravidade ausente quando não há área.';

COMMIT;
