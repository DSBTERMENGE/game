-- Migração 016: referências independentes e valores numéricos ausentes.

BEGIN;

ALTER TABLE avaliacoes_validacao
    ADD COLUMN estado_valor_esperado VARCHAR(30),
    ADD COLUMN estado_valor_calculado VARCHAR(30),
    ADD COLUMN referencia_origem VARCHAR(30),
    ADD COLUMN referencia_revisor VARCHAR(200),
    ADD COLUMN referencia_observacao TEXT,
    ADD COLUMN referencia_conferida_em TIMESTAMPTZ;

ALTER TABLE avaliacoes_validacao
    DROP CONSTRAINT ck_avaliacoes_validacao_modo,
    DROP CONSTRAINT ck_avaliacoes_validacao_referencia_numerica,
    DROP CONSTRAINT ck_avaliacoes_validacao_execucao_numerica,
    ADD CONSTRAINT ck_avaliacoes_validacao_modo CHECK (
        (id_grupo IS NULL
            AND estado_padrao_esperado IS NULL AND id_padrao_esperado IS NULL
            AND estado_padrao_calculado IS NULL AND id_padrao_calculado IS NULL)
        OR
        (id_grupo IS NOT NULL
            AND estado_valor_esperado IS NULL AND valor_esperado IS NULL
            AND estado_valor_calculado IS NULL AND valor_calculado IS NULL
            AND diferenca IS NULL)
    ),
    ADD CONSTRAINT ck_avaliacoes_validacao_referencia_numerica CHECK (
        id_grupo IS NOT NULL
        OR
        (referencia_conferida
            AND estado_valor_esperado IN ('VALOR_IDENTIFICADO', 'SEM_VALOR')
            AND ((estado_valor_esperado = 'VALOR_IDENTIFICADO' AND valor_esperado IS NOT NULL)
                OR (estado_valor_esperado = 'SEM_VALOR' AND valor_esperado IS NULL)))
        OR
        (NOT referencia_conferida
            AND estado_valor_esperado IS NULL AND valor_esperado IS NULL)
    ),
    ADD CONSTRAINT ck_avaliacoes_validacao_execucao_numerica CHECK (
        id_grupo IS NOT NULL
        OR
        (executado
            AND estado_valor_calculado IN ('VALOR_IDENTIFICADO', 'SEM_VALOR')
            AND ((estado_valor_calculado = 'VALOR_IDENTIFICADO' AND valor_calculado IS NOT NULL)
                OR (estado_valor_calculado = 'SEM_VALOR' AND valor_calculado IS NULL)))
        OR
        (NOT executado
            AND estado_valor_calculado IS NULL AND valor_calculado IS NULL)
    ),
    ADD CONSTRAINT ck_avaliacoes_validacao_revisor CHECK (
        (referencia_conferida
            AND referencia_origem IN ('HUMANO', 'IA', 'TESTE_AUTOMATIZADO')
            AND BTRIM(referencia_revisor) <> ''
            AND referencia_conferida_em IS NOT NULL)
        OR
        (NOT referencia_conferida
            AND referencia_origem IS NULL AND referencia_revisor IS NULL
            AND referencia_observacao IS NULL AND referencia_conferida_em IS NULL)
    );

COMMENT ON COLUMN avaliacoes_validacao.estado_valor_esperado IS
    'VALOR_IDENTIFICADO ou SEM_VALOR para referência numérica conferida.';
COMMENT ON COLUMN avaliacoes_validacao.referencia_origem IS
    'Origem independente que produziu e conferiu o esperado.';

COMMIT;
