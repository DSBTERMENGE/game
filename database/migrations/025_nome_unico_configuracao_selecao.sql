BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT LOWER(BTRIM(nome))
        FROM configuracoes_pesquisa_selecao
        GROUP BY LOWER(BTRIM(nome))
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION
            'Existem configurações de seleção com nomes equivalentes.';
    END IF;
END $$;

CREATE UNIQUE INDEX uk_config_pesquisa_nome_normalizado
    ON configuracoes_pesquisa_selecao (LOWER(BTRIM(nome)));

COMMIT;
