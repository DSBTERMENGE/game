-- Migração 011: conjunto de resultados usado para homologar funções.

BEGIN;

CREATE TABLE amostras_validacao (
    id_resultado BIGINT PRIMARY KEY,
    ordem SMALLINT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    incluido_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_amostras_validacao_ordem UNIQUE (ordem),
    CONSTRAINT ck_amostras_validacao_ordem_positiva CHECK (ordem > 0),
    CONSTRAINT fk_amostras_validacao_resultado
        FOREIGN KEY (id_resultado) REFERENCES resultados (id_resultado)
        ON UPDATE RESTRICT ON DELETE CASCADE
);

COMMENT ON TABLE amostras_validacao IS
    'Resultados selecionados como entradas para homologação das funções.';
COMMENT ON COLUMN amostras_validacao.id_resultado IS
    'PK e FK para resultados; as dezenas não são duplicadas nesta tabela.';
COMMENT ON COLUMN amostras_validacao.ordem IS
    'Ordem estável de apresentação e execução da amostra.';
COMMENT ON COLUMN amostras_validacao.ativo IS
    'Indica se a amostra participa da homologação atual.';
COMMENT ON COLUMN amostras_validacao.incluido_em IS
    'Data e hora de inclusão do resultado no conjunto de validação.';

COMMIT;
