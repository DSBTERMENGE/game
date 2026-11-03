-- Migração 022: lotes autorizados de jogos da seleção de dezenas.

BEGIN;

CREATE TABLE lotes_jogos_selecao (
    id_lote_jogos BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_alvo_selecao BIGINT NOT NULL,
    quantidade_dezenas SMALLINT NOT NULL,
    quantidade_combinacoes BIGINT NOT NULL,
    estado VARCHAR(16) NOT NULL DEFAULT 'GERANDO',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    concluido_em TIMESTAMPTZ,

    CONSTRAINT fk_lote_jogos_alvo FOREIGN KEY (id_alvo_selecao)
        REFERENCES alvos_pesquisa_selecao (id_alvo_selecao)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT ck_lote_jogos_quantidades CHECK (
        quantidade_dezenas BETWEEN 6 AND 60
        AND quantidade_combinacoes > 0
    ),
    CONSTRAINT ck_lote_jogos_estado CHECK (
        (estado = 'GERANDO' AND concluido_em IS NULL)
        OR (estado = 'CONCLUIDO' AND concluido_em IS NOT NULL)
        OR (estado = 'CANCELADO' AND concluido_em IS NOT NULL)
    )
);

CREATE INDEX ix_lote_jogos_alvo
    ON lotes_jogos_selecao (id_alvo_selecao, criado_em);

CREATE TABLE jogos_selecao_dezenas (
    id_lote_jogos BIGINT NOT NULL,
    ordem BIGINT NOT NULL,
    dezena_1 SMALLINT NOT NULL,
    dezena_2 SMALLINT NOT NULL,
    dezena_3 SMALLINT NOT NULL,
    dezena_4 SMALLINT NOT NULL,
    dezena_5 SMALLINT NOT NULL,
    dezena_6 SMALLINT NOT NULL,

    CONSTRAINT pk_jogos_selecao PRIMARY KEY (id_lote_jogos, ordem),
    CONSTRAINT fk_jogos_selecao_lote FOREIGN KEY (id_lote_jogos)
        REFERENCES lotes_jogos_selecao (id_lote_jogos)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT uk_jogos_selecao_dezenas UNIQUE (
        id_lote_jogos, dezena_1, dezena_2, dezena_3,
        dezena_4, dezena_5, dezena_6
    ),
    CONSTRAINT ck_jogos_selecao_ordem CHECK (ordem > 0),
    CONSTRAINT ck_jogos_selecao_dezenas CHECK (
        dezena_1 BETWEEN 1 AND 60
        AND dezena_1 < dezena_2 AND dezena_2 < dezena_3
        AND dezena_3 < dezena_4 AND dezena_4 < dezena_5
        AND dezena_5 < dezena_6 AND dezena_6 <= 60
    )
);

COMMIT;
