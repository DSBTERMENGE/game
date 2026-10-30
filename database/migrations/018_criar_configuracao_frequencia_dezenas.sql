-- Migração 018: configuração reproduzível do estudo de frequência das dezenas.

BEGIN;

CREATE TABLE configuracao_frequencia_dezenas (
    id_configuracao SMALLINT PRIMARY KEY DEFAULT 1,
    nome VARCHAR(120) NOT NULL,
    concurso_inicial INTEGER NOT NULL,
    tamanho_inicial INTEGER NOT NULL,
    regra_janela VARCHAR(40) NOT NULL,
    tipo_evento VARCHAR(10) NOT NULL,
    metodo_faixa VARCHAR(50) NOT NULL,
    parametro_faixa NUMERIC(12,6) NOT NULL,
    unidade_parametro VARCHAR(40) NOT NULL,
    regra_arredondamento VARCHAR(30) NOT NULL,
    versao_calculo INTEGER NOT NULL,
    assinatura_sha256 CHAR(64) NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_config_frequencia_linha_unica CHECK (id_configuracao = 1),
    CONSTRAINT ck_config_frequencia_nome CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_config_frequencia_concurso CHECK (concurso_inicial > 0),
    CONSTRAINT ck_config_frequencia_tamanho CHECK (tamanho_inicial > 0),
    CONSTRAINT ck_config_frequencia_regra_janela CHECK (
        regra_janela IN ('INICIO_FIXO_FINAL_EXPANSIVO')
    ),
    CONSTRAINT ck_config_frequencia_tipo_evento CHECK (
        tipo_evento IN ('TODOS', 'SIMPLES', '2VS', '3VS')
    ),
    CONSTRAINT ck_config_frequencia_metodo_faixa CHECK (
        metodo_faixa IN ('MEDIA_MAIS_MENOS_DESVIO_PADRAO')
    ),
    CONSTRAINT ck_config_frequencia_parametro CHECK (parametro_faixa > 0),
    CONSTRAINT ck_config_frequencia_unidade CHECK (
        unidade_parametro IN ('MULTIPLICADOR_DESVIO_PADRAO')
    ),
    CONSTRAINT ck_config_frequencia_arredondamento CHECK (
        regra_arredondamento IN ('LIMITES_EXTERNOS')
    ),
    CONSTRAINT ck_config_frequencia_versao CHECK (versao_calculo > 0),
    CONSTRAINT ck_config_frequencia_assinatura CHECK (
        assinatura_sha256 ~ '^[0-9a-f]{64}$'
    )
);

CREATE FUNCTION proteger_configuracao_frequencia_dezenas()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'A configuração ativa de frequência não pode ser excluída.';
    END IF;
    IF NEW.id_configuracao <> OLD.id_configuracao THEN
        RAISE EXCEPTION 'A identidade da configuração ativa não pode ser alterada.';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tg_proteger_configuracao_frequencia_dezenas
BEFORE UPDATE OR DELETE ON configuracao_frequencia_dezenas
FOR EACH ROW EXECUTE FUNCTION proteger_configuracao_frequencia_dezenas();

INSERT INTO configuracao_frequencia_dezenas (
    id_configuracao, nome, concurso_inicial, tamanho_inicial, regra_janela,
    tipo_evento, metodo_faixa, parametro_faixa, unidade_parametro,
    regra_arredondamento, versao_calculo, assinatura_sha256
) VALUES (
    1, 'Estudo acumulado inicial', 1, 500, 'INICIO_FIXO_FINAL_EXPANSIVO',
    'TODOS', 'MEDIA_MAIS_MENOS_DESVIO_PADRAO', 1.000000,
    'MULTIPLICADOR_DESVIO_PADRAO', 'LIMITES_EXTERNOS', 1,
    'a24e8a50eff1957fffcbbc923314e33c852a4333322e2b3d57c58e0b6aeb941f'
);

COMMENT ON TABLE configuracao_frequencia_dezenas IS
    'Linha única com a configuração ativa e reproduzível do estudo de frequências.';
COMMENT ON COLUMN configuracao_frequencia_dezenas.parametro_faixa IS
    'Valor cuja interpretação depende obrigatoriamente da unidade_parametro explícita.';
COMMENT ON COLUMN configuracao_frequencia_dezenas.assinatura_sha256 IS
    'SHA-256 do JSON canônico de todos os campos capazes de alterar o resultado.';

COMMIT;
