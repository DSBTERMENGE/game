-- Migração 013: estado global da validação do algoritmo de seleção.

BEGIN;

CREATE TABLE estado_algoritmo_selecao (
    id_estado SMALLINT PRIMARY KEY DEFAULT 1,
    atualizado BOOLEAN NOT NULL DEFAULT FALSE,
    motivo VARCHAR(300) NOT NULL DEFAULT 'AGUARDANDO_HOMOLOGACAO_INICIAL',
    assinatura_catalogo_homologado CHAR(64),
    assinatura_conjunto_resultados CHAR(64),
    quantidade_resultados BIGINT NOT NULL DEFAULT 0,
    homologado_em TIMESTAMPTZ,
    perfis_atualizados_em TIMESTAMPTZ,
    cobertura_confirmada_em TIMESTAMPTZ,
    alterado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_estado_algoritmo_linha_unica CHECK (id_estado = 1),
    CONSTRAINT ck_estado_algoritmo_motivo_preenchido CHECK (BTRIM(motivo) <> ''),
    CONSTRAINT ck_estado_algoritmo_quantidade CHECK (quantidade_resultados >= 0),
    CONSTRAINT ck_estado_algoritmo_assinatura_catalogo CHECK (
        assinatura_catalogo_homologado IS NULL
        OR assinatura_catalogo_homologado ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT ck_estado_algoritmo_assinatura_resultados CHECK (
        assinatura_conjunto_resultados IS NULL
        OR assinatura_conjunto_resultados ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT ck_estado_algoritmo_atualizado_com_evidencias CHECK (
        NOT atualizado
        OR (
            assinatura_catalogo_homologado IS NOT NULL
            AND assinatura_conjunto_resultados IS NOT NULL
            AND homologado_em IS NOT NULL
            AND perfis_atualizados_em IS NOT NULL
            AND cobertura_confirmada_em IS NOT NULL
        )
    )
);

CREATE FUNCTION proteger_estado_algoritmo_selecao()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'A linha única do estado do algoritmo não pode ser excluída.';
    END IF;
    IF NEW.id_estado <> OLD.id_estado THEN
        RAISE EXCEPTION 'A identidade da linha única do estado não pode ser alterada.';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tg_proteger_estado_algoritmo_selecao
BEFORE UPDATE OR DELETE ON estado_algoritmo_selecao
FOR EACH ROW EXECUTE FUNCTION proteger_estado_algoritmo_selecao();

INSERT INTO estado_algoritmo_selecao (id_estado)
VALUES (1);

COMMENT ON TABLE estado_algoritmo_selecao IS
    'Linha única com as evidências que liberam ou bloqueiam o algoritmo de seleção.';
COMMENT ON COLUMN estado_algoritmo_selecao.atualizado IS
    'FALSE bloqueia o Screener; TRUE exige homologação, perfis e cobertura confirmados.';
COMMENT ON COLUMN estado_algoritmo_selecao.motivo IS
    'Diagnóstico técnico; a interface exibe somente atualizado ou desatualizado.';
COMMENT ON COLUMN estado_algoritmo_selecao.assinatura_catalogo_homologado IS
    'SHA-256 do conjunto de critérios e assinaturas homologados.';
COMMENT ON COLUMN estado_algoritmo_selecao.assinatura_conjunto_resultados IS
    'SHA-256 da identidade do conjunto de resultados usado nos perfis atuais.';
COMMENT ON COLUMN estado_algoritmo_selecao.quantidade_resultados IS
    'Quantidade de resultados válidos considerada no recálculo dos perfis atuais.';

COMMIT;
