-- Migração 023: cada previsão da seleção de dezenas possui somente o próximo alvo.

BEGIN;

ALTER TABLE configuracoes_pesquisa_selecao
    ADD COLUMN versao_assinatura SMALLINT;

UPDATE configuracoes_pesquisa_selecao
SET versao_assinatura = 1,
    estado = 'ARQUIVADA',
    arquivada_em = COALESCE(arquivada_em, CURRENT_TIMESTAMP);

ALTER TABLE configuracoes_pesquisa_selecao
    ALTER COLUMN versao_assinatura SET NOT NULL,
    ALTER COLUMN versao_assinatura SET DEFAULT 2,
    ADD CONSTRAINT ck_config_pesquisa_selecao_versao_assinatura
        CHECK (versao_assinatura IN (1, 2)),
    DROP CONSTRAINT ck_config_pesquisa_selecao_horizonte,
    DROP COLUMN horizonte_concursos;

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
        NEW.quantidade_dezenas, NEW.versao_calculo,
        NEW.assinatura_sha256, NEW.versao_assinatura
    ) IS DISTINCT FROM ROW(
        OLD.nome, OLD.fator_k, OLD.fator_j, OLD.modo_quantidade,
        OLD.quantidade_dezenas, OLD.versao_calculo,
        OLD.assinatura_sha256, OLD.versao_assinatura
    ) THEN
        RAISE EXCEPTION 'A configuração usada por uma pesquisa é imutável.';
    END IF;
    RETURN NEW;
END;
$$;

COMMENT ON COLUMN configuracoes_pesquisa_selecao.versao_assinatura IS
    'Versão 1 identifica assinatura legada com horizonte; versão 2 não inclui horizonte.';

COMMIT;
