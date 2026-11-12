-- Migração 028: Gestão do desenvolvimento do Game.

BEGIN;

CREATE TABLE manutencao_sistema (
    id_manutencao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo VARCHAR(32) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    criterios_conclusao TEXT,
    prioridade VARCHAR(16) NOT NULL DEFAULT 'NORMAL',
    status_trabalho VARCHAR(32) NOT NULL DEFAULT 'NAO_INICIADO',
    status_publicacao VARCHAR(32) NOT NULL DEFAULT 'NAO_APLICAVEL',
    origem_registro VARCHAR(16) NOT NULL DEFAULT 'USUARIO',
    pagina_origem VARCHAR(300),
    referencia VARCHAR(1000),
    observacao_publicacao TEXT,
    chave_idempotencia CHAR(64) NOT NULL,
    versao_registro INTEGER NOT NULL DEFAULT 1,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    iniciado_em TIMESTAMPTZ,
    concluido_em TIMESTAMPTZ,
    publicado_em TIMESTAMPTZ,
    arquivado_em TIMESTAMPTZ,

    CONSTRAINT uk_manutencao_idempotencia UNIQUE (chave_idempotencia),
    CONSTRAINT ck_manutencao_tipo CHECK (tipo IN (
        'ERRO', 'MAU_FUNCIONAMENTO', 'MODIFICACAO',
        'NOVA_FUNCIONALIDADE', 'NAO_CLASSIFICADO'
    )),
    CONSTRAINT ck_manutencao_prioridade CHECK (
        prioridade IN ('BAIXA', 'NORMAL', 'ALTA', 'URGENTE')
    ),
    CONSTRAINT ck_manutencao_status_trabalho CHECK (status_trabalho IN (
        'NAO_INICIADO', 'EM_ANALISE', 'EM_ANDAMENTO',
        'AGUARDANDO_VALIDACAO', 'CONCLUIDO', 'CANCELADO'
    )),
    CONSTRAINT ck_manutencao_status_publicacao CHECK (status_publicacao IN (
        'NAO_APLICAVEL', 'AGUARDANDO_PUBLICACAO',
        'PUBLICADO', 'FALHA_PUBLICACAO'
    )),
    CONSTRAINT ck_manutencao_origem CHECK (
        origem_registro IN ('USUARIO', 'IA', 'SISTEMA')
    ),
    CONSTRAINT ck_manutencao_textos CHECK (
        BTRIM(titulo) <> '' AND BTRIM(descricao) <> ''
        AND versao_registro > 0
        AND chave_idempotencia ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT uk_manutencao_idempotencia UNIQUE (chave_idempotencia),
    CONSTRAINT uk_manutencao_idempotencia UNIQUE (chave_idempotencia),
    CONSTRAINT ck_manutencao_conclusao CHECK (
        status_trabalho <> 'CONCLUIDO'
        OR (criterios_conclusao IS NOT NULL
            AND BTRIM(criterios_conclusao) <> ''
            AND concluido_em IS NOT NULL)
    ),
    CONSTRAINT ck_manutencao_publicacao CHECK (
        (status_publicacao <> 'PUBLICADO' OR publicado_em IS NOT NULL)
        AND (status_publicacao <> 'FALHA_PUBLICACAO'
            OR (observacao_publicacao IS NOT NULL
                AND BTRIM(observacao_publicacao) <> ''))
    )
);

CREATE INDEX ix_manutencao_consulta
    ON manutencao_sistema (arquivado_em, atualizado_em DESC);
CREATE INDEX ix_manutencao_titulo_busca
    ON manutencao_sistema (LOWER(titulo));
CREATE INDEX ix_manutencao_filtros
    ON manutencao_sistema
    (tipo, prioridade, status_trabalho, status_publicacao);

CREATE TABLE manutencao_sistema_historico (
    id_evento BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_manutencao BIGINT NOT NULL,
    tipo_evento VARCHAR(32) NOT NULL,
    versao_registro INTEGER NOT NULL,
    origem_evento VARCHAR(16) NOT NULL,
    dados_json JSONB NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_manutencao_historico FOREIGN KEY (id_manutencao)
        REFERENCES manutencao_sistema (id_manutencao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_manutencao_historico CHECK (
        tipo_evento IN (
            'CRIADO', 'ATUALIZADO', 'ARQUIVADO', 'DESARQUIVADO',
            'REABERTO', 'STATUS_ALTERADO', 'PUBLICACAO_ALTERADA'
        )
        AND versao_registro > 0
        AND origem_evento IN ('USUARIO', 'IA', 'SISTEMA')
        AND jsonb_typeof(dados_json) = 'object'
    )
);

CREATE INDEX ix_manutencao_historico_registro
    ON manutencao_sistema_historico (id_manutencao, criado_em, id_evento);

CREATE OR REPLACE FUNCTION impedir_alteracao_historico_manutencao()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'O histórico da manutenção é imutável.';
END;
$$;

CREATE TRIGGER tg_historico_manutencao_imutavel
BEFORE UPDATE OR DELETE ON manutencao_sistema_historico
FOR EACH ROW EXECUTE FUNCTION impedir_alteracao_historico_manutencao();

COMMIT;
