-- Migração 003: cadastros iniciais e sequência estável de códigos de padrões.
-- Compatível com PostgreSQL 12 ou superior.

BEGIN;

INSERT INTO padroes (padrao_cod, padrao_nome, padrao_descr)
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
ON CONFLICT (padrao_cod) DO NOTHING;

CREATE SEQUENCE padroes_codigo_seq AS BIGINT MINVALUE 1 START WITH 4;

SELECT SETVAL(
    'padroes_codigo_seq',
    GREATEST(
        3,
        COALESCE(
            MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT),
            3
        )
    ),
    TRUE
)
FROM padroes;

COMMENT ON SEQUENCE padroes_codigo_seq IS
    'Gera a parte numérica de padrao_cod sem reutilizar códigos excluídos.';

COMMIT;
