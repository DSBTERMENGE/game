-- Migração 021: pesquisas reproduzíveis da seleção de dezenas.

BEGIN;

CREATE TABLE configuracoes_pesquisa_selecao (
    id_configuracao_selecao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    fator_k NUMERIC(12,6) NOT NULL,
    fator_j NUMERIC(12,6) NOT NULL,
    modo_quantidade VARCHAR(10) NOT NULL,
    quantidade_dezenas SMALLINT,
    horizonte_concursos SMALLINT NOT NULL DEFAULT 1,
    versao_calculo INTEGER NOT NULL,
    assinatura_sha256 CHAR(64) NOT NULL,
    estado VARCHAR(12) NOT NULL DEFAULT 'DISPONIVEL',
    criada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    arquivada_em TIMESTAMPTZ,

    CONSTRAINT uk_config_pesquisa_selecao_assinatura
        UNIQUE (assinatura_sha256),
    CONSTRAINT ck_config_pesquisa_selecao_nome
        CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_config_pesquisa_selecao_k
        CHECK (fator_k > 0 AND fator_k <= 1),
    CONSTRAINT ck_config_pesquisa_selecao_j
        CHECK (fator_j >= -fator_k AND fator_j <= fator_k),
    CONSTRAINT ck_config_pesquisa_selecao_quantidade CHECK (
        (modo_quantidade = 'MAX' AND quantidade_dezenas IS NULL)
        OR
        (modo_quantidade = 'FIXA' AND quantidade_dezenas BETWEEN 6 AND 60)
    ),
    CONSTRAINT ck_config_pesquisa_selecao_horizonte
        CHECK (horizonte_concursos >= 1),
    CONSTRAINT ck_config_pesquisa_selecao_versao
        CHECK (versao_calculo > 0),
    CONSTRAINT ck_config_pesquisa_selecao_assinatura
        CHECK (assinatura_sha256 ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_config_pesquisa_selecao_estado CHECK (
        (estado = 'DISPONIVEL' AND arquivada_em IS NULL)
        OR
        (estado = 'ARQUIVADA' AND arquivada_em IS NOT NULL)
    )
);

CREATE INDEX ix_config_pesquisa_selecao_estado
    ON configuracoes_pesquisa_selecao (estado, criada_em);

CREATE TABLE execucoes_pesquisa_selecao (
    id_execucao_selecao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_configuracao_selecao BIGINT NOT NULL,
    tipo_execucao VARCHAR(20) NOT NULL,
    configuracao_json JSONB NOT NULL,
    assinatura_configuracao CHAR(64) NOT NULL,
    assinatura_resultados CHAR(64) NOT NULL,
    versao_calculo INTEGER NOT NULL,
    concurso_corte_origem INTEGER NOT NULL,
    concurso_alvo_inicial INTEGER NOT NULL,
    concurso_alvo_final INTEGER NOT NULL,
    estado VARCHAR(24) NOT NULL DEFAULT 'PENDENTE',
    alvos_concluidos INTEGER NOT NULL DEFAULT 0,
    total_alvos INTEGER NOT NULL,
    erro_codigo VARCHAR(80),
    erro_mensagem TEXT,
    criada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    iniciada_em TIMESTAMPTZ,
    concluida_em TIMESTAMPTZ,

    CONSTRAINT fk_execucao_pesquisa_configuracao FOREIGN KEY (
        id_configuracao_selecao
    ) REFERENCES configuracoes_pesquisa_selecao (id_configuracao_selecao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT uk_execucao_pesquisa_origem UNIQUE (
        tipo_execucao, assinatura_configuracao, assinatura_resultados,
        versao_calculo, concurso_alvo_inicial, concurso_alvo_final
    ),
    CONSTRAINT ck_execucao_pesquisa_tipo
        CHECK (tipo_execucao IN ('BACKTEST', 'PREVISAO_FUTURA')),
    CONSTRAINT ck_execucao_pesquisa_json
        CHECK (JSONB_TYPEOF(configuracao_json) = 'object'),
    CONSTRAINT ck_execucao_pesquisa_assinatura_config
        CHECK (assinatura_configuracao ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_execucao_pesquisa_assinatura_resultados
        CHECK (assinatura_resultados ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_execucao_pesquisa_versao CHECK (versao_calculo > 0),
    CONSTRAINT ck_execucao_pesquisa_periodo CHECK (
        concurso_corte_origem > 0
        AND concurso_alvo_inicial > 0
        AND concurso_alvo_final >= concurso_alvo_inicial
        AND (
            (tipo_execucao = 'BACKTEST'
                AND concurso_alvo_inicial >= 500
                AND concurso_alvo_final <= concurso_corte_origem)
            OR
            (tipo_execucao = 'PREVISAO_FUTURA'
                AND concurso_alvo_inicial > concurso_corte_origem)
        )
    ),
    CONSTRAINT ck_execucao_pesquisa_totais CHECK (
        total_alvos = concurso_alvo_final - concurso_alvo_inicial + 1
        AND alvos_concluidos BETWEEN 0 AND total_alvos
    ),
    CONSTRAINT ck_execucao_pesquisa_estado CHECK (
        estado IN (
            'PENDENTE', 'EXECUTANDO', 'CANCELAMENTO_SOLICITADO',
            'CONCLUIDA', 'CANCELADA', 'FALHA'
        )
    ),
    CONSTRAINT ck_execucao_pesquisa_ciclo CHECK (
        (estado = 'PENDENTE'
            AND iniciada_em IS NULL AND concluida_em IS NULL
            AND erro_codigo IS NULL AND erro_mensagem IS NULL)
        OR
        (estado IN ('EXECUTANDO', 'CANCELAMENTO_SOLICITADO')
            AND iniciada_em IS NOT NULL AND concluida_em IS NULL
            AND erro_codigo IS NULL AND erro_mensagem IS NULL)
        OR
        (estado IN ('CONCLUIDA', 'CANCELADA')
            AND iniciada_em IS NOT NULL AND concluida_em IS NOT NULL
            AND erro_codigo IS NULL AND erro_mensagem IS NULL)
        OR
        (estado = 'FALHA'
            AND iniciada_em IS NOT NULL AND concluida_em IS NOT NULL
            AND erro_codigo IS NOT NULL AND BTRIM(erro_codigo) <> ''
            AND erro_mensagem IS NOT NULL AND BTRIM(erro_mensagem) <> '')
    )
);

CREATE INDEX ix_execucao_pesquisa_configuracao
    ON execucoes_pesquisa_selecao (id_configuracao_selecao, criada_em DESC);
CREATE INDEX ix_execucao_pesquisa_estado
    ON execucoes_pesquisa_selecao (estado, criada_em);
CREATE INDEX ix_execucao_pesquisa_comparacao
    ON execucoes_pesquisa_selecao (
        assinatura_resultados, versao_calculo,
        concurso_alvo_inicial, concurso_alvo_final
    );

CREATE OR REPLACE FUNCTION proteger_configuracao_pesquisa_selecao()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM execucoes_pesquisa_selecao
        WHERE id_configuracao_selecao = OLD.id_configuracao_selecao
    ) AND ROW(
        NEW.nome, NEW.fator_k, NEW.fator_j, NEW.modo_quantidade,
        NEW.quantidade_dezenas, NEW.horizonte_concursos, NEW.versao_calculo,
        NEW.assinatura_sha256
    ) IS DISTINCT FROM ROW(
        OLD.nome, OLD.fator_k, OLD.fator_j, OLD.modo_quantidade,
        OLD.quantidade_dezenas, OLD.horizonte_concursos, OLD.versao_calculo,
        OLD.assinatura_sha256
    ) THEN
        RAISE EXCEPTION 'A configuração usada por uma pesquisa é imutável.';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tg_proteger_configuracao_pesquisa_selecao
BEFORE UPDATE ON configuracoes_pesquisa_selecao
FOR EACH ROW EXECUTE FUNCTION proteger_configuracao_pesquisa_selecao();

CREATE TABLE alvos_pesquisa_selecao (
    id_alvo_selecao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_execucao_selecao BIGINT NOT NULL,
    numero_concurso_alvo INTEGER NOT NULL,
    numero_concurso_corte INTEGER NOT NULL,
    id_resultado BIGINT,
    situacao VARCHAR(20) NOT NULL,
    quantidade_configurada SMALLINT,
    quantidade_aprovada SMALLINT NOT NULL,
    quantidade_retornada SMALLINT NOT NULL,
    limite_nao_atingido BOOLEAN NOT NULL DEFAULT FALSE,
    quantidade_acertos SMALLINT,
    classe_acerto SMALLINT,
    quantidade_combinacoes_brutas BIGINT NOT NULL DEFAULT 0,
    motivo VARCHAR(160),
    selecionado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conferido_em TIMESTAMPTZ,

    CONSTRAINT fk_alvo_pesquisa_execucao FOREIGN KEY (id_execucao_selecao)
        REFERENCES execucoes_pesquisa_selecao (id_execucao_selecao)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_alvo_pesquisa_resultado FOREIGN KEY (id_resultado)
        REFERENCES resultados (id_resultado)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT uk_alvo_pesquisa_concurso
        UNIQUE (id_execucao_selecao, numero_concurso_alvo),
    CONSTRAINT ck_alvo_pesquisa_concursos CHECK (
        numero_concurso_alvo > 0
        AND numero_concurso_corte > 0
        AND numero_concurso_corte < numero_concurso_alvo
    ),
    CONSTRAINT ck_alvo_pesquisa_situacao CHECK (
        situacao IN ('AVALIADO', 'PENDENTE', 'NAO_AVALIAVEL')
    ),
    CONSTRAINT ck_alvo_pesquisa_quantidades CHECK (
        quantidade_aprovada BETWEEN 0 AND 60
        AND quantidade_retornada BETWEEN 0 AND quantidade_aprovada
        AND (
            (quantidade_configurada IS NULL
                AND quantidade_retornada = quantidade_aprovada
                AND NOT limite_nao_atingido)
            OR
            (quantidade_configurada BETWEEN 6 AND 60
                AND quantidade_retornada =
                    LEAST(quantidade_aprovada, quantidade_configurada)
                AND limite_nao_atingido =
                    (quantidade_aprovada < quantidade_configurada))
        )
    ),
    CONSTRAINT ck_alvo_pesquisa_acertos CHECK (
        (quantidade_acertos IS NULL AND classe_acerto IS NULL)
        OR
        (quantidade_acertos BETWEEN 0 AND 6
            AND classe_acerto = quantidade_acertos
            AND quantidade_acertos <= quantidade_retornada)
    ),
    CONSTRAINT ck_alvo_pesquisa_combinacoes
        CHECK (quantidade_combinacoes_brutas >= 0),
    CONSTRAINT ck_alvo_pesquisa_estado CHECK (
        (situacao = 'AVALIADO'
            AND id_resultado IS NOT NULL
            AND quantidade_acertos IS NOT NULL
            AND classe_acerto IS NOT NULL
            AND conferido_em IS NOT NULL)
        OR
        (situacao = 'PENDENTE'
            AND id_resultado IS NULL
            AND quantidade_acertos IS NULL
            AND classe_acerto IS NULL
            AND conferido_em IS NULL)
        OR
        (situacao = 'NAO_AVALIAVEL'
            AND quantidade_acertos IS NULL
            AND classe_acerto IS NULL
            AND motivo IS NOT NULL AND BTRIM(motivo) <> '')
    )
);

CREATE INDEX ix_alvo_pesquisa_situacao
    ON alvos_pesquisa_selecao (id_execucao_selecao, situacao);
CREATE INDEX ix_alvo_pesquisa_resultado
    ON alvos_pesquisa_selecao (id_resultado)
    WHERE id_resultado IS NOT NULL;

CREATE TABLE avaliacoes_dezenas_pesquisa (
    id_alvo_selecao BIGINT NOT NULL,
    dezena SMALLINT NOT NULL,
    estado_avaliacao VARCHAR(28) NOT NULL,
    ultima_ocorrencia INTEGER,
    quantidade_intervalos INTEGER NOT NULL,
    media_intervalos NUMERIC(18,6),
    desvio_padrao NUMERIC(18,6),
    centro_original NUMERIC(18,6),
    centro_ajustado NUMERIC(18,6),
    limite_inferior_exato NUMERIC(18,6),
    limite_superior_exato NUMERIC(18,6),
    limite_inferior INTEGER,
    limite_superior INTEGER,
    distancia_normalizada NUMERIC(24,12),
    distancia_absoluta NUMERIC(18,6),
    posicao_ranking SMALLINT,
    aprovada BOOLEAN NOT NULL,
    retornada BOOLEAN NOT NULL,

    CONSTRAINT pk_avaliacoes_dezenas_pesquisa
        PRIMARY KEY (id_alvo_selecao, dezena),
    CONSTRAINT fk_avaliacao_dezena_alvo FOREIGN KEY (id_alvo_selecao)
        REFERENCES alvos_pesquisa_selecao (id_alvo_selecao)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT ck_avaliacao_dezena_numero CHECK (dezena BETWEEN 1 AND 60),
    CONSTRAINT ck_avaliacao_dezena_estado CHECK (
        estado_avaliacao IN (
            'SEM_BASE', 'FORA_FAIXA',
            'APROVADA_RETORNADA', 'APROVADA_NAO_RETORNADA'
        )
    ),
    CONSTRAINT ck_avaliacao_dezena_quantidade
        CHECK (quantidade_intervalos >= 0),
    CONSTRAINT ck_avaliacao_dezena_booleans CHECK (
        NOT retornada OR aprovada
    ),
    CONSTRAINT ck_avaliacao_dezena_sem_base CHECK (
        (estado_avaliacao = 'SEM_BASE'
            AND quantidade_intervalos = 0
            AND ultima_ocorrencia IS NULL
            AND media_intervalos IS NULL AND desvio_padrao IS NULL
            AND centro_original IS NULL AND centro_ajustado IS NULL
            AND limite_inferior_exato IS NULL
            AND limite_superior_exato IS NULL
            AND limite_inferior IS NULL AND limite_superior IS NULL
            AND distancia_normalizada IS NULL
            AND distancia_absoluta IS NULL AND posicao_ranking IS NULL
            AND NOT aprovada AND NOT retornada)
        OR
        (estado_avaliacao <> 'SEM_BASE'
            AND quantidade_intervalos > 0
            AND ultima_ocorrencia IS NOT NULL
            AND media_intervalos IS NOT NULL
            AND desvio_padrao IS NOT NULL AND desvio_padrao >= 0
            AND centro_original IS NOT NULL AND centro_ajustado IS NOT NULL
            AND limite_inferior_exato IS NOT NULL
            AND limite_superior_exato IS NOT NULL
            AND limite_inferior_exato <= limite_superior_exato
            AND limite_inferior IS NOT NULL AND limite_superior IS NOT NULL
            AND limite_inferior <= limite_superior
            AND distancia_absoluta IS NOT NULL
            AND distancia_absoluta >= 0
            AND posicao_ranking BETWEEN 1 AND 60)
    ),
    CONSTRAINT ck_avaliacao_dezena_classificacao CHECK (
        (estado_avaliacao = 'FORA_FAIXA'
            AND NOT aprovada AND NOT retornada)
        OR
        (estado_avaliacao = 'APROVADA_RETORNADA'
            AND aprovada AND retornada)
        OR
        (estado_avaliacao = 'APROVADA_NAO_RETORNADA'
            AND aprovada AND NOT retornada)
        OR
        estado_avaliacao = 'SEM_BASE'
    ),
    CONSTRAINT ck_avaliacao_dezena_distancia CHECK (
        distancia_normalizada IS NULL OR distancia_normalizada >= 0
    )
);

CREATE UNIQUE INDEX uk_avaliacao_dezena_ranking
    ON avaliacoes_dezenas_pesquisa (id_alvo_selecao, posicao_ranking)
    WHERE posicao_ranking IS NOT NULL;
CREATE INDEX ix_avaliacao_dezena_retornada
    ON avaliacoes_dezenas_pesquisa (id_alvo_selecao, retornada);
CREATE INDEX ix_avaliacao_dezena_aprovada
    ON avaliacoes_dezenas_pesquisa (id_alvo_selecao, aprovada);
CREATE INDEX ix_avaliacao_dezena_historico
    ON avaliacoes_dezenas_pesquisa (dezena, estado_avaliacao);

COMMENT ON TABLE configuracoes_pesquisa_selecao IS
    'Configurações versionadas e assinadas do screener de dezenas.';
COMMENT ON TABLE execucoes_pesquisa_selecao IS
    'Execuções reproduzíveis de backtest ou previsão futura.';
COMMENT ON TABLE alvos_pesquisa_selecao IS
    'Resultado da seleção e conferência por concurso-alvo.';
COMMENT ON TABLE avaliacoes_dezenas_pesquisa IS
    'Avaliação auditável das 60 dezenas em cada concurso-alvo.';

COMMIT;

