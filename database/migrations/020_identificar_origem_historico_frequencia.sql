-- Migração 020: identidade dos resultados usados por cada geração histórica.

BEGIN;

ALTER TABLE geracoes_frequencia_dezenas
    ADD COLUMN assinatura_resultados CHAR(64) NOT NULL,
    ADD COLUMN quantidade_resultados INTEGER NOT NULL;

ALTER TABLE geracoes_frequencia_dezenas
    ADD CONSTRAINT ck_geracao_frequencia_assinatura_resultados CHECK (
        assinatura_resultados ~ '^[0-9a-f]{64}$'
    ),
    ADD CONSTRAINT ck_geracao_frequencia_quantidade_resultados CHECK (
        quantidade_resultados > 0
    );

COMMENT ON COLUMN geracoes_frequencia_dezenas.assinatura_resultados IS
    'SHA-256 canônico dos resultados entre o início da configuração e o concurso final.';
COMMENT ON COLUMN geracoes_frequencia_dezenas.quantidade_resultados IS
    'Quantidade de concursos que compõe a assinatura da origem da geração.';

COMMIT;
