-- Migração 009: fotografia estatística atual de cada padrão.

BEGIN;

ALTER TABLE padroes_subgrupo
    ADD COLUMN total_sorteios INTEGER,
    ADD COLUMN percentual_ocorrencia NUMERIC(9,6),
    ADD CONSTRAINT ck_padroes_total_sorteios
        CHECK (total_sorteios IS NULL OR total_sorteios > 0),
    ADD CONSTRAINT ck_padroes_percentual_ocorrencia
        CHECK (
            percentual_ocorrencia IS NULL
            OR percentual_ocorrencia BETWEEN 0 AND 100
        ),
    ADD CONSTRAINT ck_padroes_fotografia_ocorrencia CHECK (
        (
            total_sorteios IS NULL
            AND percentual_ocorrencia IS NULL
        )
        OR
        (
            total_sorteios IS NOT NULL
            AND num_oco IS NOT NULL
            AND num_oco <= total_sorteios
            AND percentual_ocorrencia IS NOT NULL
            AND percentual_ocorrencia = ROUND(
                num_oco::NUMERIC * 100 / total_sorteios,
                6
            )
        )
    );

COMMENT ON COLUMN padroes_subgrupo.total_sorteios IS
    'Total de sorteios da fotografia histórica atual; nulo antes do cálculo.';
COMMENT ON COLUMN padroes_subgrupo.percentual_ocorrencia IS
    'Incidência atual do padrão: num_oco / total_sorteios * 100, com seis casas.';

COMMIT;
