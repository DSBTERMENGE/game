-- Migração 005: reserva e inicializa os padrões verticais de linhas subjacentes.

BEGIN;

DO $$
DECLARE
    grupo_colunas BIGINT;
BEGIN
    SELECT id_grupo INTO grupo_colunas
    FROM padroes_grupo
    WHERE grupo_cod = 'PG_002';

    IF grupo_colunas IS NULL THEN
        RAISE EXCEPTION 'O grupo PG_002 não foi encontrado.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM padroes_subgrupo
        WHERE padrao_cod IN ('PD_004', 'PD_005', 'PD_006')
          AND id_grupo <> grupo_colunas
    ) THEN
        RAISE EXCEPTION
            'Um código reservado de PD_004 a PD_006 pertence a outro grupo.';
    END IF;
END;
$$;

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
  AND NOT EXISTS (
      SELECT 1
      FROM padroes_subgrupo existente
      WHERE existente.padrao_cod = dados.padrao_cod
  );

SELECT SETVAL(
    'padroes_subgrupo_codigo_seq',
    GREATEST(
        6,
        COALESCE(MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT), 6)
    ),
    TRUE
)
FROM padroes_subgrupo;

COMMIT;
