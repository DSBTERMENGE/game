-- Migração 026: configuração e jogos finais após Screener e classificação.

BEGIN;

CREATE TABLE formacoes_jogos_selecao (
    id_formacao_jogos BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_alvo_selecao BIGINT NOT NULL,
    quantidade_dezenas SMALLINT NOT NULL,
    quantidade_combinacoes_brutas BIGINT NOT NULL,
    quantidade_jogos_solicitada BIGINT NOT NULL,
    valor_unitario NUMERIC(14,2) NOT NULL,
    valor_maximo_previsto NUMERIC(20,2)
        GENERATED ALWAYS AS (quantidade_jogos_solicitada * valor_unitario) STORED,
    versao_formacao SMALLINT NOT NULL,
    fotografia_screener_json JSONB NOT NULL,
    assinatura_screener CHAR(64) NOT NULL,
    versao_classificador SMALLINT NOT NULL,
    assinatura_classificador CHAR(64) NOT NULL,
    chave_idempotencia CHAR(64) NOT NULL,
    quantidade_examinada BIGINT NOT NULL DEFAULT 0,
    quantidade_reprovada BIGINT NOT NULL DEFAULT 0,
    quantidade_aprovada BIGINT NOT NULL DEFAULT 0,
    quantidade_disponibilizada BIGINT NOT NULL DEFAULT 0,
    valor_efetivo NUMERIC(20,2)
        GENERATED ALWAYS AS (quantidade_disponibilizada * valor_unitario) STORED,
    estado VARCHAR(32) NOT NULL DEFAULT 'CONFIGURADA',
    erro_codigo VARCHAR(80),
    erro_mensagem VARCHAR(500),
    criada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    iniciada_em TIMESTAMPTZ,
    processada_em TIMESTAMPTZ,
    concluida_em TIMESTAMPTZ,

    CONSTRAINT fk_formacao_jogos_alvo FOREIGN KEY (id_alvo_selecao)
        REFERENCES alvos_pesquisa_selecao (id_alvo_selecao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT uk_formacao_jogos_idempotencia UNIQUE (chave_idempotencia),
    CONSTRAINT ck_formacao_jogos_configuracao CHECK (
        quantidade_dezenas BETWEEN 6 AND 60
        AND quantidade_combinacoes_brutas BETWEEN 1 AND 50063860
        AND quantidade_jogos_solicitada BETWEEN 1 AND 50063860
        AND valor_unitario > 0
        AND versao_formacao > 0
        AND versao_classificador > 0
        AND jsonb_typeof(fotografia_screener_json) = 'object'
        AND assinatura_screener ~ '^[0-9a-f]{64}$'
        AND assinatura_classificador ~ '^[0-9a-f]{64}$'
        AND chave_idempotencia ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT ck_formacao_jogos_totais CHECK (
        quantidade_examinada BETWEEN 0 AND quantidade_combinacoes_brutas
        AND quantidade_reprovada >= 0
        AND quantidade_aprovada >= 0
        AND quantidade_examinada = quantidade_reprovada + quantidade_aprovada
        AND quantidade_disponibilizada BETWEEN 0 AND quantidade_aprovada
        AND quantidade_disponibilizada <= quantidade_jogos_solicitada
    ),
    CONSTRAINT ck_formacao_jogos_estado CHECK (
        estado IN (
            'CONFIGURADA', 'PROCESSANDO', 'AGUARDANDO_CONFIRMACAO',
            'CONCLUIDA', 'CANCELADA', 'FALHOU'
        )
    ),
    CONSTRAINT ck_formacao_jogos_fechamento CHECK (
        (estado = 'CONFIGURADA' AND quantidade_examinada = 0
            AND iniciada_em IS NULL AND processada_em IS NULL AND concluida_em IS NULL)
        OR (estado = 'PROCESSANDO' AND iniciada_em IS NOT NULL
            AND processada_em IS NULL AND concluida_em IS NULL)
        OR (estado = 'AGUARDANDO_CONFIRMACAO'
            AND quantidade_examinada = quantidade_combinacoes_brutas
            AND quantidade_disponibilizada = LEAST(
                quantidade_jogos_solicitada, quantidade_aprovada
            )
            AND iniciada_em IS NOT NULL AND processada_em IS NOT NULL
            AND concluida_em IS NULL)
        OR (estado = 'CONCLUIDA'
            AND quantidade_examinada = quantidade_combinacoes_brutas
            AND quantidade_disponibilizada = LEAST(
                quantidade_jogos_solicitada, quantidade_aprovada
            )
            AND iniciada_em IS NOT NULL AND processada_em IS NOT NULL
            AND concluida_em IS NOT NULL)
        OR (estado = 'CANCELADA' AND iniciada_em IS NOT NULL
            AND concluida_em IS NOT NULL)
        OR (estado = 'FALHOU' AND iniciada_em IS NOT NULL
            AND concluida_em IS NOT NULL AND erro_codigo IS NOT NULL
            AND BTRIM(erro_codigo) <> '' AND erro_mensagem IS NOT NULL
            AND BTRIM(erro_mensagem) <> '')
    )
);

CREATE INDEX ix_formacao_jogos_alvo
    ON formacoes_jogos_selecao (id_alvo_selecao, criada_em DESC);

CREATE TABLE jogos_finais_selecao (
    id_formacao_jogos BIGINT NOT NULL,
    posicao_classificacao BIGINT NOT NULL,
    dezena_1 SMALLINT NOT NULL,
    dezena_2 SMALLINT NOT NULL,
    dezena_3 SMALLINT NOT NULL,
    dezena_4 SMALLINT NOT NULL,
    dezena_5 SMALLINT NOT NULL,
    dezena_6 SMALLINT NOT NULL,
    pontuacao_classificacao NUMERIC(24,12) NOT NULL,
    evidencias_classificacao JSONB NOT NULL,

    CONSTRAINT pk_jogos_finais_selecao
        PRIMARY KEY (id_formacao_jogos, posicao_classificacao),
    CONSTRAINT fk_jogos_finais_formacao FOREIGN KEY (id_formacao_jogos)
        REFERENCES formacoes_jogos_selecao (id_formacao_jogos)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT uk_jogos_finais_dezenas UNIQUE (
        id_formacao_jogos, dezena_1, dezena_2, dezena_3,
        dezena_4, dezena_5, dezena_6
    ),
    CONSTRAINT ck_jogos_finais_posicao CHECK (posicao_classificacao > 0),
    CONSTRAINT ck_jogos_finais_evidencias CHECK (
        jsonb_typeof(evidencias_classificacao) = 'object'
    ),
    CONSTRAINT ck_jogos_finais_dezenas CHECK (
        dezena_1 BETWEEN 1 AND 60
        AND dezena_1 < dezena_2 AND dezena_2 < dezena_3
        AND dezena_3 < dezena_4 AND dezena_4 < dezena_5
        AND dezena_5 < dezena_6 AND dezena_6 <= 60
    )
);

CREATE OR REPLACE FUNCTION proteger_configuracao_formacao_jogos()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF ROW(
        NEW.id_alvo_selecao, NEW.quantidade_dezenas,
        NEW.quantidade_combinacoes_brutas, NEW.quantidade_jogos_solicitada,
        NEW.valor_unitario, NEW.versao_formacao,
        NEW.fotografia_screener_json, NEW.assinatura_screener,
        NEW.versao_classificador, NEW.assinatura_classificador,
        NEW.chave_idempotencia
    ) IS DISTINCT FROM ROW(
        OLD.id_alvo_selecao, OLD.quantidade_dezenas,
        OLD.quantidade_combinacoes_brutas, OLD.quantidade_jogos_solicitada,
        OLD.valor_unitario, OLD.versao_formacao,
        OLD.fotografia_screener_json, OLD.assinatura_screener,
        OLD.versao_classificador, OLD.assinatura_classificador,
        OLD.chave_idempotencia
    ) THEN
        RAISE EXCEPTION 'A configuração da formação de jogos é imutável.';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tg_proteger_configuracao_formacao_jogos
BEFORE UPDATE ON formacoes_jogos_selecao
FOR EACH ROW EXECUTE FUNCTION proteger_configuracao_formacao_jogos();

CREATE OR REPLACE FUNCTION proteger_jogo_final_selecao()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Um jogo final classificado não pode ser alterado.';
END;
$$;

CREATE TRIGGER tg_proteger_jogo_final_selecao
BEFORE UPDATE ON jogos_finais_selecao
FOR EACH ROW EXECUTE FUNCTION proteger_jogo_final_selecao();

COMMIT;
