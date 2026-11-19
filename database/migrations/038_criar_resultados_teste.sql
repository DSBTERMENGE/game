-- Migração 038: coleção fixa de combinações para validação de detectores.

BEGIN;

CREATE TABLE resultados_teste (
    id_resultado_teste BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    res_01 SMALLINT NOT NULL,
    res_02 SMALLINT NOT NULL,
    res_03 SMALLINT NOT NULL,
    res_04 SMALLINT NOT NULL,
    res_05 SMALLINT NOT NULL,
    res_06 SMALLINT NOT NULL,

    CONSTRAINT ck_resultados_teste_intervalos CHECK (
        res_01 BETWEEN 1 AND 60
        AND res_02 BETWEEN 1 AND 60
        AND res_03 BETWEEN 1 AND 60
        AND res_04 BETWEEN 1 AND 60
        AND res_05 BETWEEN 1 AND 60
        AND res_06 BETWEEN 1 AND 60
    ),
    CONSTRAINT ck_resultados_teste_distintos CHECK (
        res_01 <> res_02
        AND res_01 <> res_03
        AND res_01 <> res_04
        AND res_01 <> res_05
        AND res_01 <> res_06
        AND res_02 <> res_03
        AND res_02 <> res_04
        AND res_02 <> res_05
        AND res_02 <> res_06
        AND res_03 <> res_04
        AND res_03 <> res_05
        AND res_03 <> res_06
        AND res_04 <> res_05
        AND res_04 <> res_06
        AND res_05 <> res_06
    )
);

COMMENT ON TABLE resultados_teste IS
    'Coleção fixa de combinações aleatórias usada para validar detectores.';
COMMENT ON COLUMN resultados_teste.id_resultado_teste IS
    'Identificador interno automático, sem significado para o teste.';
COMMENT ON COLUMN resultados_teste.res_01 IS 'Primeira dezena na ordem gerada.';
COMMENT ON COLUMN resultados_teste.res_02 IS 'Segunda dezena na ordem gerada.';
COMMENT ON COLUMN resultados_teste.res_03 IS 'Terceira dezena na ordem gerada.';
COMMENT ON COLUMN resultados_teste.res_04 IS 'Quarta dezena na ordem gerada.';
COMMENT ON COLUMN resultados_teste.res_05 IS 'Quinta dezena na ordem gerada.';
COMMENT ON COLUMN resultados_teste.res_06 IS 'Sexta dezena na ordem gerada.';

COMMIT;
