-- Migração 017: quantidade, mínimo e máximo dos intervalos simples.

BEGIN;

ALTER TABLE frequencia_de_resultado
    ADD COLUMN qtd_intervalos INTEGER,
    ADD COLUMN intervalo_minimo INTEGER,
    ADD COLUMN intervalo_maximo INTEGER;

WITH ocorrencias AS (
    SELECT r.numero_ap, d.dezena
    FROM resultados AS r
    CROSS JOIN LATERAL UNNEST(ARRAY[
        r.res_01, r.res_02, r.res_03, r.res_04, r.res_05, r.res_06
    ]) AS d(dezena)
), intervalos AS (
    SELECT dezena,
           numero_ap - LAG(numero_ap) OVER (
               PARTITION BY dezena ORDER BY numero_ap
           ) AS intervalo
    FROM ocorrencias
), resumo AS (
    SELECT dezena,
           COUNT(intervalo)::INTEGER AS qtd_intervalos,
           MIN(intervalo)::INTEGER AS intervalo_minimo,
           MAX(intervalo)::INTEGER AS intervalo_maximo
    FROM intervalos
    GROUP BY dezena
)
UPDATE frequencia_de_resultado AS f
SET qtd_intervalos = COALESCE(r.qtd_intervalos, 0),
    intervalo_minimo = r.intervalo_minimo,
    intervalo_maximo = r.intervalo_maximo
FROM resumo AS r
WHERE r.dezena = f.dezena;

UPDATE frequencia_de_resultado
SET qtd_intervalos = 0
WHERE qtd_intervalos IS NULL;

ALTER TABLE frequencia_de_resultado
    ALTER COLUMN qtd_intervalos SET DEFAULT 0,
    ALTER COLUMN qtd_intervalos SET NOT NULL,
    ADD CONSTRAINT ck_frequencia_de_resultado_intervalos CHECK (
        (num_oco < 2 AND qtd_intervalos = 0
            AND intervalo_minimo IS NULL AND intervalo_maximo IS NULL)
        OR
        (num_oco >= 2 AND qtd_intervalos = num_oco - 1
            AND intervalo_minimo > 0
            AND intervalo_maximo >= intervalo_minimo)
    );

COMMENT ON COLUMN frequencia_de_resultado.qtd_intervalos IS
    'Quantidade de intervalos entre ocorrências simples consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.intervalo_minimo IS
    'Menor intervalo observado entre ocorrências simples consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.intervalo_maximo IS
    'Maior intervalo observado entre ocorrências simples consecutivas.';

COMMIT;
