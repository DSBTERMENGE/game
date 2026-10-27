-- Migração 001: estrutura inicial do Game / MSen.
-- Compatível com PostgreSQL 12 ou superior.
-- Pressupõe conexão prévia ao database correto.

BEGIN;

CREATE TABLE IF NOT EXISTS schema_migrations (
    versao VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL,
    aplicada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_schema_migrations_versao_preenchida
        CHECK (BTRIM(versao) <> ''),
    CONSTRAINT ck_schema_migrations_nome_preenchido
        CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_schema_migrations_checksum_sha256
        CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$')
);

COMMENT ON TABLE schema_migrations IS
    'Controle das migrações PostgreSQL aplicadas pelo projeto.';
COMMENT ON COLUMN schema_migrations.checksum_sha256 IS
    'SHA-256 em hexadecimal minúsculo do arquivo de migração aplicado.';

CREATE TABLE IF NOT EXISTS resultados (
    id_resultado BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_resultado DATE NOT NULL,
    numero_ap INTEGER NOT NULL,
    res_01 SMALLINT NOT NULL,
    res_02 SMALLINT NOT NULL,
    res_03 SMALLINT NOT NULL,
    res_04 SMALLINT NOT NULL,
    res_05 SMALLINT NOT NULL,
    res_06 SMALLINT NOT NULL,
    soma_res SMALLINT NOT NULL,
    media_aritmetica_res NUMERIC(10,6) NOT NULL,
    mediana_res NUMERIC(4,1) NOT NULL,
    desvio_padrao_media NUMERIC(10,6) NOT NULL,
    media_coordenada_x NUMERIC(7,6) NOT NULL,
    media_coordenada_y NUMERIC(7,6) NOT NULL,
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_resultados_numero_ap UNIQUE (numero_ap),
    CONSTRAINT ck_resultados_numero_ap_positivo CHECK (numero_ap > 0),
    CONSTRAINT ck_resultados_res_01_intervalo CHECK (res_01 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_02_intervalo CHECK (res_02 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_03_intervalo CHECK (res_03 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_04_intervalo CHECK (res_04 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_05_intervalo CHECK (res_05 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_06_intervalo CHECK (res_06 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_distintos CHECK (
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
    ),
    CONSTRAINT ck_resultados_soma_res CHECK (soma_res BETWEEN 21 AND 345),
    CONSTRAINT ck_resultados_media_aritmetica_res
        CHECK (media_aritmetica_res BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_mediana_res CHECK (mediana_res BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_desvio_padrao_media
        CHECK (desvio_padrao_media >= 0),
    CONSTRAINT ck_resultados_media_coordenada_x
        CHECK (media_coordenada_x BETWEEN 0 AND 9),
    CONSTRAINT ck_resultados_media_coordenada_y
        CHECK (media_coordenada_y BETWEEN 0 AND 5),
    CONSTRAINT ck_resultados_versao_calculo CHECK (versao_calculo > 0)
);

CREATE INDEX IF NOT EXISTS idx_resultados_data_resultado
    ON resultados (data_resultado);

COMMENT ON TABLE resultados IS
    'Resultados históricos e cálculos próprios de cada apresentação.';
COMMENT ON COLUMN resultados.id_resultado IS
    'Identificador interno automático, sem significado histórico.';
COMMENT ON COLUMN resultados.numero_ap IS
    'Número oficial e único da apresentação/concurso.';
COMMENT ON COLUMN resultados.res_01 IS 'Primeiro resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_02 IS 'Segundo resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_03 IS 'Terceiro resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_04 IS 'Quarto resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_05 IS 'Quinto resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_06 IS 'Sexto resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.desvio_padrao_media IS
    'Desvio-padrão populacional dos seis resultados.';
COMMENT ON COLUMN resultados.media_coordenada_x IS
    'Média horizontal no sistema lógico de coordenadas da matriz.';
COMMENT ON COLUMN resultados.media_coordenada_y IS
    'Média vertical no sistema lógico de coordenadas da matriz.';

CREATE TABLE IF NOT EXISTS analise_geometrica_resultado (
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
    CONSTRAINT ck_analise_geometrica_area CHECK (area_total >= 0),
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
    CONSTRAINT ck_analise_geometrica_versao_calculo CHECK (versao_calculo > 0)
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

CREATE TABLE IF NOT EXISTS frequencia_de_resultado (
    id_dezena SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dezena SMALLINT NOT NULL,
    prim_oco INTEGER,
    ult_oco INTEGER,
    num_oco INTEGER NOT NULL DEFAULT 0,
    media_oco NUMERIC(12,6),
    mediana_oco NUMERIC(12,6),
    desv_padrao_oco NUMERIC(12,6),
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_frequencia_de_resultado_dezena UNIQUE (dezena),
    CONSTRAINT ck_frequencia_de_resultado_dezena
        CHECK (dezena BETWEEN 1 AND 60),
    CONSTRAINT ck_frequencia_de_resultado_num_oco CHECK (num_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_ordem_ocorrencias
        CHECK (prim_oco IS NULL OR ult_oco IS NULL OR prim_oco <= ult_oco),
    CONSTRAINT ck_frequencia_de_resultado_estado CHECK (
        (
            num_oco = 0
            AND prim_oco IS NULL
            AND ult_oco IS NULL
            AND media_oco IS NULL
            AND mediana_oco IS NULL
            AND desv_padrao_oco IS NULL
        )
        OR
        (
            num_oco = 1
            AND prim_oco IS NOT NULL
            AND ult_oco = prim_oco
            AND media_oco IS NULL
            AND mediana_oco IS NULL
            AND desv_padrao_oco IS NULL
        )
        OR
        (
            num_oco >= 2
            AND prim_oco IS NOT NULL
            AND ult_oco IS NOT NULL
            AND media_oco IS NOT NULL
            AND mediana_oco IS NOT NULL
            AND desv_padrao_oco IS NOT NULL
        )
    ),
    CONSTRAINT ck_frequencia_de_resultado_media_oco
        CHECK (media_oco IS NULL OR media_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_mediana_oco
        CHECK (mediana_oco IS NULL OR mediana_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_desv_padrao_oco
        CHECK (desv_padrao_oco IS NULL OR desv_padrao_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_versao_calculo
        CHECK (versao_calculo > 0),
    CONSTRAINT fk_frequencia_de_resultado_prim_oco
        FOREIGN KEY (prim_oco)
        REFERENCES resultados (numero_ap)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_frequencia_de_resultado_ult_oco
        FOREIGN KEY (ult_oco)
        REFERENCES resultados (numero_ap)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE frequencia_de_resultado IS
    'Resumo derivado de ocorrências e intervalos para cada dezena de 01 a 60.';
COMMENT ON COLUMN frequencia_de_resultado.prim_oco IS
    'Número da primeira apresentação em que a dezena ocorreu.';
COMMENT ON COLUMN frequencia_de_resultado.ult_oco IS
    'Número da última apresentação em que a dezena ocorreu.';
COMMENT ON COLUMN frequencia_de_resultado.num_oco IS
    'Quantidade total de ocorrências da dezena.';
COMMENT ON COLUMN frequencia_de_resultado.media_oco IS
    'Média dos intervalos entre ocorrências consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.mediana_oco IS
    'Mediana dos intervalos entre ocorrências consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.desv_padrao_oco IS
    'Desvio-padrão populacional dos intervalos entre ocorrências.';

INSERT INTO frequencia_de_resultado (dezena)
SELECT dezena
FROM GENERATE_SERIES(1, 60) AS dezenas(dezena)
ON CONFLICT (dezena) DO NOTHING;

CREATE TABLE IF NOT EXISTS padroes_grupo (
    id_grupo BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    grupo_cod VARCHAR(20) NOT NULL,
    grupo_nome VARCHAR(200) NOT NULL,
    grupo_descr TEXT NOT NULL,

    CONSTRAINT uk_padroes_grupo_grupo_cod UNIQUE (grupo_cod),
    CONSTRAINT ck_padroes_grupo_grupo_cod_formato
        CHECK (grupo_cod ~ '^PG_[0-9]{3,}$'),
    CONSTRAINT ck_padroes_grupo_grupo_nome_preenchido
        CHECK (BTRIM(grupo_nome) <> ''),
    CONSTRAINT ck_padroes_grupo_grupo_descr_preenchida
        CHECK (BTRIM(grupo_descr) <> '')
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_padroes_grupo_nome_normalizado
    ON padroes_grupo (LOWER(BTRIM(grupo_nome)));

COMMENT ON TABLE padroes_grupo IS
    'Grupos conceituais usados para organizar padrões relacionados.';
COMMENT ON COLUMN padroes_grupo.id_grupo IS
    'Identificador interno automático do grupo.';
COMMENT ON COLUMN padroes_grupo.grupo_cod IS
    'Código estável e único do grupo, gerado pelo sistema.';
COMMENT ON COLUMN padroes_grupo.grupo_nome IS
    'Nome curto e editável do conceito agrupador.';
COMMENT ON COLUMN padroes_grupo.grupo_descr IS
    'Descrição detalhada e editável do conceito agrupador.';

INSERT INTO padroes_grupo (grupo_cod, grupo_nome, grupo_descr)
VALUES
(
    'PG_001',
    'Dezenas sequenciais',
    'Padrões baseados em grupos de dezenas consecutivas no resultado.'
),
(
    'PG_002',
    'Dezenas na mesma coluna',
    'Padrões baseados em dezenas posicionadas na mesma coluna da matriz.'
),
(
    'PG_003',
    'Dezenas na mesma linha',
    'Padrões baseados na quantidade de dezenas posicionadas na mesma linha da matriz.'
)
ON CONFLICT (grupo_cod) DO NOTHING;

CREATE SEQUENCE IF NOT EXISTS padroes_grupo_codigo_seq
    AS BIGINT MINVALUE 1 START WITH 4;

SELECT SETVAL(
    'padroes_grupo_codigo_seq',
    GREATEST(
        3,
        COALESCE(MAX(SUBSTRING(grupo_cod FROM 4)::BIGINT), 3)
    ),
    TRUE
)
FROM padroes_grupo;

COMMENT ON SEQUENCE padroes_grupo_codigo_seq IS
    'Gera a parte numérica de grupo_cod sem reutilizar códigos excluídos.';

CREATE TABLE IF NOT EXISTS padroes_subgrupo (
    id_padrao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_grupo BIGINT NOT NULL,
    padrao_cod VARCHAR(20) NOT NULL,
    padrao_nome VARCHAR(200) NOT NULL,
    padrao_descr TEXT NOT NULL,
    num_oco INTEGER,
    intervalo_medio NUMERIC(12,6),
    desv_padrao NUMERIC(12,6),

    CONSTRAINT uk_padroes_padrao_cod UNIQUE (padrao_cod),
    CONSTRAINT ck_padroes_padrao_cod_formato
        CHECK (padrao_cod ~ '^PD_[0-9]{3,}$'),
    CONSTRAINT ck_padroes_padrao_nome_preenchido
        CHECK (BTRIM(padrao_nome) <> ''),
    CONSTRAINT ck_padroes_padrao_descr_preenchida
        CHECK (BTRIM(padrao_descr) <> ''),
    CONSTRAINT ck_padroes_num_oco
        CHECK (num_oco IS NULL OR num_oco >= 0),
    CONSTRAINT ck_padroes_intervalo_medio
        CHECK (intervalo_medio IS NULL OR intervalo_medio >= 0),
    CONSTRAINT ck_padroes_desv_padrao
        CHECK (desv_padrao IS NULL OR desv_padrao >= 0),
    CONSTRAINT ck_padroes_estado_estatistico CHECK (
        (
            num_oco IS NULL
            AND intervalo_medio IS NULL
            AND desv_padrao IS NULL
        )
        OR
        (
            num_oco BETWEEN 0 AND 1
            AND intervalo_medio IS NULL
            AND desv_padrao IS NULL
        )
        OR
        (
            num_oco >= 2
            AND intervalo_medio IS NOT NULL
            AND desv_padrao IS NOT NULL
        )
    ),
    CONSTRAINT fk_padroes_subgrupo_grupo
        FOREIGN KEY (id_grupo)
        REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_padroes_subgrupo_nome_no_grupo
    ON padroes_subgrupo (id_grupo, LOWER(BTRIM(padrao_nome)));

COMMENT ON TABLE padroes_subgrupo IS
    'Padrões específicos vinculados a grupos e suas estatísticas históricas.';
COMMENT ON COLUMN padroes_subgrupo.id_padrao IS
    'Identificador interno automático, sem significado funcional.';
COMMENT ON COLUMN padroes_subgrupo.id_grupo IS
    'Grupo conceitual obrigatório ao qual o padrão pertence.';
COMMENT ON COLUMN padroes_subgrupo.padrao_cod IS
    'Código estável e único usado para vincular o cadastro ao detector Python.';
COMMENT ON COLUMN padroes_subgrupo.padrao_nome IS
    'Nome curto e editável apresentado ao usuário.';
COMMENT ON COLUMN padroes_subgrupo.padrao_descr IS
    'Descrição detalhada e editável da regra reconhecida pelo detector.';
COMMENT ON COLUMN padroes_subgrupo.num_oco IS
    'Quantidade de resultados históricos que correspondem ao padrão; nulo antes do cálculo.';
COMMENT ON COLUMN padroes_subgrupo.intervalo_medio IS
    'Média dos intervalos entre ocorrências; nula quando existem menos de duas ocorrências.';
COMMENT ON COLUMN padroes_subgrupo.desv_padrao IS
    'Desvio-padrão populacional dos intervalos; nulo quando existem menos de duas ocorrências.';

INSERT INTO padroes_subgrupo (id_grupo, padrao_cod, padrao_nome, padrao_descr)
SELECT grupo.id_grupo, dados.padrao_cod, dados.padrao_nome, dados.padrao_descr
FROM padroes_grupo AS grupo
CROSS JOIN (
    VALUES
    (
        'PD_001',
        'Duas dezenas sequenciais',
        'O maior grupo consecutivo do resultado possui exatamente duas dezenas.'
    ),
    (
        'PD_002',
        'Três dezenas sequenciais',
        'O maior grupo consecutivo do resultado possui exatamente três dezenas.'
    ),
    (
        'PD_003',
        'Mais de três dezenas sequenciais',
        'O maior grupo consecutivo do resultado possui quatro, cinco ou seis dezenas.'
    )
) AS dados(padrao_cod, padrao_nome, padrao_descr)
WHERE grupo.grupo_cod = 'PG_001'
ON CONFLICT (padrao_cod) DO NOTHING;

INSERT INTO padroes_subgrupo (id_grupo, padrao_cod, padrao_nome, padrao_descr)
SELECT grupo.id_grupo, dados.padrao_cod, dados.padrao_nome, dados.padrao_descr
FROM padroes_grupo AS grupo
CROSS JOIN (
    VALUES
    (
        'PD_004',
        'Duas dezenas em linhas subjacentes na mesma coluna',
        'O maior grupo vertical possui exatamente duas dezenas na mesma coluna e em linhas imediatamente consecutivas.'
    ),
    (
        'PD_005',
        'Três dezenas em linhas subjacentes na mesma coluna',
        'O maior grupo vertical possui exatamente três dezenas na mesma coluna e em linhas imediatamente consecutivas.'
    ),
    (
        'PD_006',
        'Mais de três dezenas em linhas subjacentes na mesma coluna',
        'O maior grupo vertical possui quatro, cinco ou seis dezenas na mesma coluna e em linhas imediatamente consecutivas.'
    )
) AS dados(padrao_cod, padrao_nome, padrao_descr)
WHERE grupo.grupo_cod = 'PG_002'
ON CONFLICT (padrao_cod) DO NOTHING;

INSERT INTO padroes_subgrupo (id_grupo, padrao_cod, padrao_nome, padrao_descr)
SELECT grupo.id_grupo, dados.padrao_cod, dados.padrao_nome, dados.padrao_descr
FROM padroes_grupo AS grupo
CROSS JOIN (
    VALUES
    (
        'PD_007',
        'Duas dezenas na mesma linha',
        'Duas dezenas do resultado estão na mesma linha, independentemente de serem sequenciais.'
    ),
    (
        'PD_008',
        'Três dezenas na mesma linha',
        'Três dezenas do resultado estão na mesma linha, independentemente de serem sequenciais.'
    ),
    (
        'PD_009',
        'Mais de três dezenas na mesma linha',
        'Quatro, cinco ou seis dezenas do resultado estão na mesma linha, independentemente de serem sequenciais.'
    )
) AS dados(padrao_cod, padrao_nome, padrao_descr)
WHERE grupo.grupo_cod = 'PG_003'
ON CONFLICT (padrao_cod) DO NOTHING;

CREATE SEQUENCE IF NOT EXISTS padroes_subgrupo_codigo_seq
    AS BIGINT MINVALUE 1 START WITH 10;

SELECT SETVAL(
    'padroes_subgrupo_codigo_seq',
    GREATEST(
        9,
        COALESCE(MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT), 9)
    ),
    TRUE
)
FROM padroes_subgrupo;

COMMENT ON SEQUENCE padroes_subgrupo_codigo_seq IS
    'Gera a parte numérica de padrao_cod sem reutilizar códigos excluídos.';

COMMIT;
