-- Migração 035: permite referências categóricas no sistema de validação.
--
-- Exclusivamente estrutural: não cadastra critérios, não cria referências e
-- não altera avaliações existentes.

BEGIN;

ALTER TABLE criterios_validacao
    DROP CONSTRAINT ck_criterios_validacao_tipo,
    DROP CONSTRAINT ck_criterios_validacao_categoria_tipo_grupo,
    DROP CONSTRAINT ck_criterios_validacao_precisao,
    ADD CONSTRAINT ck_criterios_validacao_tipo CHECK (
        tipo_resultado IN ('INTEIRO', 'DECIMAL', 'PADRAO', 'CATEGORICO')
    ),
    ADD CONSTRAINT ck_criterios_validacao_categoria_tipo_grupo CHECK (
        (categoria = 'PADRAO'
            AND tipo_resultado IN ('PADRAO', 'CATEGORICO')
            AND id_grupo IS NOT NULL)
        OR
        (categoria IN ('ESTATISTICA', 'GEOMETRIA')
            AND tipo_resultado IN ('INTEIRO', 'DECIMAL')
            AND id_grupo IS NULL)
    ),
    ADD CONSTRAINT ck_criterios_validacao_precisao CHECK (
        (tipo_resultado = 'DECIMAL' AND precisao_decimal BETWEEN 0 AND 18)
        OR
        (tipo_resultado IN ('INTEIRO', 'PADRAO', 'CATEGORICO')
            AND precisao_decimal IS NULL)
    ),
    ADD CONSTRAINT ck_criterios_validacao_vinculo_categorico CHECK (
        tipo_resultado <> 'CATEGORICO' OR id_padrao IS NULL
    );

ALTER TABLE avaliacoes_validacao
    ADD COLUMN categoria_esperada VARCHAR(200),
    ADD COLUMN categoria_calculada VARCHAR(200),
    DROP CONSTRAINT ck_avaliacoes_validacao_modo,
    DROP CONSTRAINT ck_avaliacoes_validacao_referencia_padrao,
    DROP CONSTRAINT ck_avaliacoes_validacao_execucao_padrao,
    ADD CONSTRAINT ck_avaliacoes_validacao_modo CHECK (
        (id_grupo IS NULL
            AND estado_padrao_esperado IS NULL
            AND id_padrao_esperado IS NULL
            AND estado_padrao_calculado IS NULL
            AND id_padrao_calculado IS NULL
            AND categoria_esperada IS NULL
            AND categoria_calculada IS NULL)
        OR
        (id_grupo IS NOT NULL
            AND estado_valor_esperado IS NULL
            AND valor_esperado IS NULL
            AND estado_valor_calculado IS NULL
            AND valor_calculado IS NULL
            AND diferenca IS NULL
            AND NOT (
                categoria_esperada IS NOT NULL
                AND (estado_padrao_esperado IS NOT NULL
                    OR id_padrao_esperado IS NOT NULL)
            )
            AND NOT (
                categoria_calculada IS NOT NULL
                AND (estado_padrao_calculado IS NOT NULL
                    OR id_padrao_calculado IS NOT NULL)
            ))
    ),
    ADD CONSTRAINT ck_avaliacoes_validacao_referencia_padrao CHECK (
        id_grupo IS NULL
        OR
        (NOT referencia_conferida
            AND estado_padrao_esperado IS NULL
            AND id_padrao_esperado IS NULL
            AND categoria_esperada IS NULL)
        OR
        (referencia_conferida
            AND (
                (categoria_esperada IS NOT NULL
                    AND BTRIM(categoria_esperada) <> ''
                    AND estado_padrao_esperado IS NULL
                    AND id_padrao_esperado IS NULL)
                OR
                (categoria_esperada IS NULL
                    AND estado_padrao_esperado IN (
                        'PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA'
                    )
                    AND (
                        (estado_padrao_esperado = 'PADRAO_IDENTIFICADO'
                            AND id_padrao_esperado IS NOT NULL)
                        OR
                        (estado_padrao_esperado = 'SEM_CORRESPONDENCIA'
                            AND id_padrao_esperado IS NULL)
                    ))
            ))
    ),
    ADD CONSTRAINT ck_avaliacoes_validacao_execucao_padrao CHECK (
        id_grupo IS NULL
        OR
        (NOT executado
            AND estado_padrao_calculado IS NULL
            AND id_padrao_calculado IS NULL
            AND categoria_calculada IS NULL)
        OR
        (executado
            AND (
                (categoria_calculada IS NOT NULL
                    AND BTRIM(categoria_calculada) <> ''
                    AND estado_padrao_calculado IS NULL
                    AND id_padrao_calculado IS NULL)
                OR
                (categoria_calculada IS NULL
                    AND estado_padrao_calculado IN (
                        'PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA'
                    )
                    AND (
                        (estado_padrao_calculado = 'PADRAO_IDENTIFICADO'
                            AND id_padrao_calculado IS NOT NULL)
                        OR
                        (estado_padrao_calculado = 'SEM_CORRESPONDENCIA'
                            AND id_padrao_calculado IS NULL)
                    ))
            ))
    );

COMMENT ON COLUMN avaliacoes_validacao.categoria_esperada IS
    'Resposta categórica independente, conferida antes da execução.';
COMMENT ON COLUMN avaliacoes_validacao.categoria_calculada IS
    'Resposta categórica produzida pela função executada.';

COMMIT;
