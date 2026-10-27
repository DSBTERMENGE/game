-- Migração 007: medidas geométricas individuais de cada resultado.

BEGIN;

CREATE TABLE analise_geometrica_resultado (
    id_resultado BIGINT PRIMARY KEY,
    extensao_aberta NUMERIC(20,12) NOT NULL,
    perimetro_fechado NUMERIC(20,12) NOT NULL,
    quantidade_regioes SMALLINT NOT NULL,
    area_total NUMERIC(20,12) NOT NULL,
    centro_gravidade_x NUMERIC(20,12),
    centro_gravidade_y NUMERIC(20,12),
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_analise_geometrica_resultado
        FOREIGN KEY (id_resultado) REFERENCES resultados (id_resultado)
        ON DELETE CASCADE,
    CONSTRAINT ck_analise_geometrica_extensao_positiva
        CHECK (extensao_aberta > 0),
    CONSTRAINT ck_analise_geometrica_perimetro
        CHECK (perimetro_fechado >= extensao_aberta),
    CONSTRAINT ck_analise_geometrica_quantidade_regioes
        CHECK (quantidade_regioes >= 0),
    CONSTRAINT ck_analise_geometrica_area
        CHECK (area_total >= 0),
    CONSTRAINT ck_analise_geometrica_estado_area CHECK (
        (quantidade_regioes = 0 AND area_total = 0)
        OR (quantidade_regioes > 0 AND area_total > 0)
    ),
    CONSTRAINT ck_analise_geometrica_centro_completo CHECK (
        (centro_gravidade_x IS NULL) = (centro_gravidade_y IS NULL)
    ),
    CONSTRAINT ck_analise_geometrica_estado_centro CHECK (
        (area_total = 0 AND centro_gravidade_x IS NULL)
        OR (area_total > 0 AND centro_gravidade_x IS NOT NULL)
    ),
    CONSTRAINT ck_analise_geometrica_centro_x CHECK (
        centro_gravidade_x IS NULL OR centro_gravidade_x BETWEEN 0 AND 9
    ),
    CONSTRAINT ck_analise_geometrica_centro_y CHECK (
        centro_gravidade_y IS NULL OR centro_gravidade_y BETWEEN 0 AND 5
    ),
    CONSTRAINT ck_analise_geometrica_versao_calculo
        CHECK (versao_calculo > 0)
);

COMMENT ON TABLE analise_geometrica_resultado IS
    'Medidas derivadas da figura formada pelas dezenas em ordem crescente.';
COMMENT ON COLUMN analise_geometrica_resultado.extensao_aberta IS
    'Soma dos cinco segmentos consecutivos em unidades lógicas.';
COMMENT ON COLUMN analise_geometrica_resultado.perimetro_fechado IS
    'Extensão aberta acrescida do segmento entre a maior e a menor dezena.';
COMMENT ON COLUMN analise_geometrica_resultado.quantidade_regioes IS
    'Quantidade de regiões fechadas e limitadas identificadas na rede planar.';
COMMENT ON COLUMN analise_geometrica_resultado.area_total IS
    'Soma positiva das áreas de todas as regiões fechadas.';
COMMENT ON COLUMN analise_geometrica_resultado.centro_gravidade_x IS
    'Coordenada horizontal do centro de gravidade ponderado pelas áreas.';
COMMENT ON COLUMN analise_geometrica_resultado.centro_gravidade_y IS
    'Coordenada vertical do centro de gravidade ponderado pelas áreas.';

COMMIT;
