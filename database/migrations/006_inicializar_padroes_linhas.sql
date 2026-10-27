-- Migração 006: reserva e inicializa os padrões de dezenas na mesma linha.

BEGIN;

INSERT INTO padroes_grupo (grupo_cod, grupo_nome, grupo_descr)
VALUES (
    'PG_003',
    'Dezenas na mesma linha',
    'Padrões baseados na quantidade de dezenas posicionadas na mesma linha da matriz.'
)
ON CONFLICT (grupo_cod) DO NOTHING;

DO $$
DECLARE
    grupo_linhas BIGINT;
BEGIN
    SELECT id_grupo INTO grupo_linhas
    FROM padroes_grupo
    WHERE grupo_cod = 'PG_003';

    IF grupo_linhas IS NULL THEN
        RAISE EXCEPTION 'O grupo PG_003 não foi encontrado.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM padroes_subgrupo
        WHERE padrao_cod IN ('PD_007', 'PD_008', 'PD_009')
          AND id_grupo <> grupo_linhas
    ) THEN
        RAISE EXCEPTION
            'Um código reservado de PD_007 a PD_009 pertence a outro grupo.';
    END IF;
END;
$$;

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
  AND NOT EXISTS (
      SELECT 1
      FROM padroes_subgrupo existente
      WHERE existente.padrao_cod = dados.padrao_cod
  );

SELECT SETVAL(
    'padroes_grupo_codigo_seq',
    GREATEST(
        3,
        COALESCE(MAX(SUBSTRING(grupo_cod FROM 4)::BIGINT), 3)
    ),
    TRUE
)
FROM padroes_grupo;

SELECT SETVAL(
    'padroes_subgrupo_codigo_seq',
    GREATEST(
        9,
        COALESCE(MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT), 9)
    ),
    TRUE
)
FROM padroes_subgrupo;

COMMIT;
