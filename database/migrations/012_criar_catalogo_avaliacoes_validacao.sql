-- Migração 012: catálogo de funções e avaliações por amostra.

BEGIN;

CREATE TABLE criterios_validacao (
    id_criterio BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(80) NOT NULL,
    nome VARCHAR(200) NOT NULL,
    categoria VARCHAR(20) NOT NULL,
    funcao_python VARCHAR(300) NOT NULL,
    tipo_resultado VARCHAR(20) NOT NULL,
    precisao_decimal SMALLINT,
    id_grupo BIGINT,
    assinatura_funcao CHAR(64) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_criterios_validacao_codigo UNIQUE (codigo),
    CONSTRAINT uk_criterios_validacao_id_grupo UNIQUE (id_criterio, id_grupo),
    CONSTRAINT ck_criterios_validacao_codigo_preenchido CHECK (BTRIM(codigo) <> ''),
    CONSTRAINT ck_criterios_validacao_nome_preenchido CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_criterios_validacao_funcao_preenchida
        CHECK (BTRIM(funcao_python) <> ''),
    CONSTRAINT ck_criterios_validacao_categoria
        CHECK (categoria IN ('ESTATISTICA', 'GEOMETRIA', 'PADRAO')),
    CONSTRAINT ck_criterios_validacao_tipo
        CHECK (tipo_resultado IN ('INTEIRO', 'DECIMAL', 'PADRAO')),
    CONSTRAINT ck_criterios_validacao_categoria_tipo_grupo CHECK (
        (categoria = 'PADRAO' AND tipo_resultado = 'PADRAO' AND id_grupo IS NOT NULL)
        OR
        (categoria IN ('ESTATISTICA', 'GEOMETRIA')
            AND tipo_resultado IN ('INTEIRO', 'DECIMAL') AND id_grupo IS NULL)
    ),
    CONSTRAINT ck_criterios_validacao_precisao CHECK (
        (tipo_resultado = 'DECIMAL' AND precisao_decimal BETWEEN 0 AND 18)
        OR
        (tipo_resultado IN ('INTEIRO', 'PADRAO') AND precisao_decimal IS NULL)
    ),
    CONSTRAINT ck_criterios_validacao_assinatura
        CHECK (assinatura_funcao ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_criterios_validacao_estado
        CHECK (estado IN ('PENDENTE', 'APROVADO', 'REPROVADO')),
    CONSTRAINT fk_criterios_validacao_grupo
        FOREIGN KEY (id_grupo) REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT ON DELETE CASCADE
);

CREATE TABLE avaliacoes_validacao (
    id_resultado BIGINT NOT NULL,
    id_criterio BIGINT NOT NULL,
    id_grupo BIGINT,
    referencia_conferida BOOLEAN NOT NULL DEFAULT FALSE,
    valor_esperado NUMERIC,
    valor_calculado NUMERIC,
    estado_padrao_esperado VARCHAR(30),
    id_padrao_esperado BIGINT,
    estado_padrao_calculado VARCHAR(30),
    id_padrao_calculado BIGINT,
    executado BOOLEAN NOT NULL DEFAULT FALSE,
    assinatura_executada CHAR(64),
    aprovado CHAR(1),
    diferenca NUMERIC,
    calculado_em TIMESTAMPTZ,

    CONSTRAINT pk_avaliacoes_validacao PRIMARY KEY (id_resultado, id_criterio),
    CONSTRAINT ck_avaliacoes_validacao_modo CHECK (
        (id_grupo IS NULL
            AND estado_padrao_esperado IS NULL AND id_padrao_esperado IS NULL
            AND estado_padrao_calculado IS NULL AND id_padrao_calculado IS NULL)
        OR
        (id_grupo IS NOT NULL
            AND valor_esperado IS NULL AND valor_calculado IS NULL
            AND diferenca IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_referencia_numerica CHECK (
        id_grupo IS NOT NULL
        OR
        (referencia_conferida AND valor_esperado IS NOT NULL)
        OR
        (NOT referencia_conferida AND valor_esperado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_referencia_padrao CHECK (
        id_grupo IS NULL
        OR
        (
            referencia_conferida
            AND estado_padrao_esperado IN ('PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA')
            AND (
                (estado_padrao_esperado = 'PADRAO_IDENTIFICADO'
                    AND id_padrao_esperado IS NOT NULL)
                OR
                (estado_padrao_esperado = 'SEM_CORRESPONDENCIA'
                    AND id_padrao_esperado IS NULL)
            )
        )
        OR
        (NOT referencia_conferida
            AND estado_padrao_esperado IS NULL AND id_padrao_esperado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_execucao_numerica CHECK (
        id_grupo IS NOT NULL
        OR
        (executado AND valor_calculado IS NOT NULL)
        OR
        (NOT executado AND valor_calculado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_execucao_padrao CHECK (
        id_grupo IS NULL
        OR
        (
            executado
            AND estado_padrao_calculado IN ('PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA')
            AND (
                (estado_padrao_calculado = 'PADRAO_IDENTIFICADO'
                    AND id_padrao_calculado IS NOT NULL)
                OR
                (estado_padrao_calculado = 'SEM_CORRESPONDENCIA'
                    AND id_padrao_calculado IS NULL)
            )
        )
        OR
        (NOT executado
            AND estado_padrao_calculado IS NULL AND id_padrao_calculado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_execucao CHECK (
        (executado
            AND assinatura_executada ~ '^[0-9a-f]{64}$'
            AND calculado_em IS NOT NULL)
        OR
        (NOT executado
            AND assinatura_executada IS NULL
            AND calculado_em IS NULL
            AND diferenca IS NULL
            AND aprovado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_aprovado CHECK (
        aprovado IS NULL OR aprovado IN ('S', 'N')
    ),
    CONSTRAINT ck_avaliacoes_validacao_comparacao CHECK (
        (referencia_conferida AND executado AND aprovado IN ('S', 'N'))
        OR
        ((NOT referencia_conferida OR NOT executado) AND aprovado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_diferenca CHECK (
        id_grupo IS NOT NULL
        OR
        (referencia_conferida AND executado AND diferenca IS NOT NULL)
        OR
        ((NOT referencia_conferida OR NOT executado) AND diferenca IS NULL)
    ),
    CONSTRAINT fk_avaliacoes_validacao_amostra
        FOREIGN KEY (id_resultado) REFERENCES amostras_validacao (id_resultado)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_validacao_criterio
        FOREIGN KEY (id_criterio) REFERENCES criterios_validacao (id_criterio)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_validacao_criterio_grupo
        FOREIGN KEY (id_criterio, id_grupo)
        REFERENCES criterios_validacao (id_criterio, id_grupo)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_validacao_padrao_esperado
        FOREIGN KEY (id_grupo, id_padrao_esperado)
        REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_avaliacoes_validacao_padrao_calculado
        FOREIGN KEY (id_grupo, id_padrao_calculado)
        REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX ix_avaliacoes_validacao_criterio_aprovado
    ON avaliacoes_validacao (id_criterio, aprovado);

COMMENT ON TABLE criterios_validacao IS
    'Catálogo das funções cuja assinatura precisa ser homologada.';
COMMENT ON TABLE avaliacoes_validacao IS
    'Comparação entre o resultado esperado e o calculado por amostra e função.';
COMMENT ON COLUMN avaliacoes_validacao.aprovado IS
    'NULL enquanto pendente, S quando coincide e N quando diverge.';
COMMENT ON COLUMN avaliacoes_validacao.estado_padrao_esperado IS
    'PADRAO_IDENTIFICADO ou SEM_CORRESPONDENCIA; NULL significa pendente.';

COMMIT;
