-- Migração 004: organiza padrões em grupos conceituais.
-- Compatível com PostgreSQL 12 ou superior.

BEGIN;

CREATE TABLE padroes_grupo (
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

CREATE UNIQUE INDEX uk_padroes_grupo_nome_normalizado
    ON padroes_grupo (LOWER(BTRIM(grupo_nome)));

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
    );

CREATE SEQUENCE padroes_grupo_codigo_seq AS BIGINT MINVALUE 1 START WITH 3;
SELECT SETVAL('padroes_grupo_codigo_seq', 2, TRUE);

ALTER TABLE padroes RENAME TO padroes_subgrupo;
ALTER SEQUENCE padroes_codigo_seq RENAME TO padroes_subgrupo_codigo_seq;

SELECT SETVAL(
    'padroes_subgrupo_codigo_seq',
    GREATEST(
        3,
        COALESCE(MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT), 3)
    ),
    TRUE
)
FROM padroes_subgrupo;

SELECT SETVAL(
    'padroes_subgrupo_codigo_seq',
    GREATEST(
        3,
        COALESCE(MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT), 3)
    ),
    TRUE
)
FROM padroes_subgrupo;

ALTER TABLE padroes_subgrupo
    ADD COLUMN id_grupo BIGINT;

UPDATE padroes_subgrupo
SET id_grupo = (
    SELECT id_grupo
    FROM padroes_grupo
    WHERE grupo_cod = 'PG_001'
)
WHERE padrao_cod IN ('PD_001', 'PD_002', 'PD_003');

UPDATE padroes_subgrupo
SET id_grupo = (
    SELECT id_grupo
    FROM padroes_grupo
    WHERE grupo_cod = 'PG_002'
)
WHERE padrao_cod IN ('PD_004', 'PD_005', 'PD_006');

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM padroes_subgrupo WHERE id_grupo IS NULL) THEN
        RAISE EXCEPTION
            'Existem padrões sem classificação aprovada; migração 004 interrompida.';
    END IF;
END;
$$;

ALTER TABLE padroes_subgrupo
    ALTER COLUMN id_grupo SET NOT NULL,
    DROP CONSTRAINT uk_padroes_padrao_nome,
    ADD CONSTRAINT fk_padroes_subgrupo_grupo
        FOREIGN KEY (id_grupo)
        REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT;

CREATE UNIQUE INDEX uk_padroes_subgrupo_nome_no_grupo
    ON padroes_subgrupo (id_grupo, LOWER(BTRIM(padrao_nome)));

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
COMMENT ON SEQUENCE padroes_grupo_codigo_seq IS
    'Gera a parte numérica de grupo_cod sem reutilizar códigos excluídos.';

COMMENT ON TABLE padroes_subgrupo IS
    'Padrões específicos vinculados a grupos e suas estatísticas históricas.';
COMMENT ON COLUMN padroes_subgrupo.id_grupo IS
    'Grupo conceitual obrigatório ao qual o padrão pertence.';
COMMENT ON SEQUENCE padroes_subgrupo_codigo_seq IS
    'Gera a parte numérica de padrao_cod sem reutilizar códigos excluídos.';

COMMIT;
