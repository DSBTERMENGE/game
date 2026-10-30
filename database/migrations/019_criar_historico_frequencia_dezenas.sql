-- Migração 019: gerações e fotografias históricas da frequência das dezenas.

BEGIN;

CREATE TABLE geracoes_frequencia_dezenas (
    id_geracao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_configuracao SMALLINT NOT NULL DEFAULT 1,
    assinatura_configuracao CHAR(64) NOT NULL,
    configuracao_json JSONB NOT NULL,
    versao_calculo INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PROVISORIA',
    concurso_inicial INTEGER NOT NULL,
    concurso_final INTEGER,
    quantidade_fotografias INTEGER NOT NULL DEFAULT 0,
    criada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    concluida_em TIMESTAMPTZ,

    CONSTRAINT fk_geracao_frequencia_configuracao FOREIGN KEY (id_configuracao)
        REFERENCES configuracao_frequencia_dezenas (id_configuracao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_geracao_frequencia_assinatura CHECK (
        assinatura_configuracao ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT ck_geracao_frequencia_json CHECK (
        JSONB_TYPEOF(configuracao_json) = 'object'
    ),
    CONSTRAINT ck_geracao_frequencia_versao CHECK (versao_calculo > 0),
    CONSTRAINT ck_geracao_frequencia_estado CHECK (
        estado IN ('PROVISORIA', 'ATIVA')
    ),
    CONSTRAINT ck_geracao_frequencia_concursos CHECK (
        concurso_inicial > 0
        AND (concurso_final IS NULL OR concurso_final >= concurso_inicial)
    ),
    CONSTRAINT ck_geracao_frequencia_quantidade CHECK (
        quantidade_fotografias >= 0
    ),
    CONSTRAINT ck_geracao_frequencia_ativa_concluida CHECK (
        estado <> 'ATIVA'
        OR (concurso_final IS NOT NULL AND concluida_em IS NOT NULL)
    )
);

CREATE UNIQUE INDEX uk_geracao_frequencia_ativa
    ON geracoes_frequencia_dezenas (estado)
    WHERE estado = 'ATIVA';

CREATE TABLE historico_frequencia_dezenas (
    id_historico BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_geracao BIGINT NOT NULL,
    numero_do_concurso INTEGER NOT NULL,
    dezena SMALLINT NOT NULL,
    tipo_evento VARCHAR(10) NOT NULL,
    quantidade_ocorrencias INTEGER NOT NULL,
    quantidade_intervalos INTEGER NOT NULL,
    intervalo_minimo INTEGER,
    intervalo_maximo INTEGER,
    media_intervalos NUMERIC(18,6),
    mediana_intervalos NUMERIC(18,6),
    desvio_padrao_intervalos NUMERIC(18,6),
    previsao_central NUMERIC(18,6),
    limite_inferior_exato NUMERIC(18,6),
    limite_superior_exato NUMERIC(18,6),
    concurso_limite_inferior INTEGER,
    concurso_limite_superior INTEGER,

    CONSTRAINT fk_historico_frequencia_geracao FOREIGN KEY (id_geracao)
        REFERENCES geracoes_frequencia_dezenas (id_geracao)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT uk_historico_frequencia_fotografia UNIQUE (
        id_geracao, numero_do_concurso, dezena, tipo_evento
    ),
    CONSTRAINT ck_historico_frequencia_concurso CHECK (numero_do_concurso > 0),
    CONSTRAINT ck_historico_frequencia_dezena CHECK (dezena BETWEEN 1 AND 60),
    CONSTRAINT ck_historico_frequencia_tipo CHECK (
        tipo_evento IN ('SIMPLES', '2VS', '3VS')
    ),
    CONSTRAINT ck_historico_frequencia_quantidades CHECK (
        quantidade_ocorrencias >= 0
        AND quantidade_intervalos >= 0
        AND (
            (quantidade_ocorrencias < 2 AND quantidade_intervalos = 0)
            OR
            (quantidade_ocorrencias >= 2
                AND quantidade_intervalos = quantidade_ocorrencias - 1)
        )
    ),
    CONSTRAINT ck_historico_frequencia_estado_estatistico CHECK (
        (
            quantidade_intervalos = 0
            AND intervalo_minimo IS NULL AND intervalo_maximo IS NULL
            AND media_intervalos IS NULL AND mediana_intervalos IS NULL
            AND desvio_padrao_intervalos IS NULL
            AND previsao_central IS NULL
            AND limite_inferior_exato IS NULL AND limite_superior_exato IS NULL
            AND concurso_limite_inferior IS NULL
            AND concurso_limite_superior IS NULL
        )
        OR
        (
            quantidade_intervalos > 0
            AND intervalo_minimo IS NOT NULL AND intervalo_minimo > 0
            AND intervalo_maximo IS NOT NULL
            AND intervalo_maximo >= intervalo_minimo
            AND media_intervalos IS NOT NULL
            AND media_intervalos BETWEEN intervalo_minimo AND intervalo_maximo
            AND mediana_intervalos IS NOT NULL
            AND mediana_intervalos BETWEEN intervalo_minimo AND intervalo_maximo
            AND desvio_padrao_intervalos IS NOT NULL
            AND desvio_padrao_intervalos >= 0
            AND previsao_central IS NOT NULL
            AND limite_inferior_exato IS NOT NULL
            AND limite_inferior_exato <= previsao_central
            AND limite_superior_exato IS NOT NULL
            AND limite_superior_exato >= previsao_central
            AND concurso_limite_inferior IS NOT NULL
            AND concurso_limite_inferior > 0
            AND concurso_limite_superior IS NOT NULL
            AND concurso_limite_superior >= concurso_limite_inferior
        )
    )
);

CREATE INDEX ix_historico_frequencia_grafico
    ON historico_frequencia_dezenas (
        id_geracao, dezena, tipo_evento, numero_do_concurso
    );

CREATE INDEX ix_historico_frequencia_concurso
    ON historico_frequencia_dezenas (id_geracao, numero_do_concurso);

COMMENT ON TABLE geracoes_frequencia_dezenas IS
    'Gerações isoladas que permitem construir e conferir uma nova série antes da troca ativa.';
COMMENT ON COLUMN geracoes_frequencia_dezenas.configuracao_json IS
    'JSON canônico da configuração usada, preservado junto à assinatura para reprodução.';
COMMENT ON TABLE historico_frequencia_dezenas IS
    'Fotografia por concurso, dezena e tipo de evento, sem copiar as dezenas dos resultados.';
COMMENT ON COLUMN historico_frequencia_dezenas.numero_do_concurso IS
    'Corte temporal inclusivo da fotografia; nenhum resultado posterior pode participar.';
COMMENT ON COLUMN historico_frequencia_dezenas.limite_inferior_exato IS
    'Limite decimal antes do arredondamento operacional externo.';
COMMENT ON COLUMN historico_frequencia_dezenas.concurso_limite_inferior IS
    'Primeiro concurso inteiro e inclusivo da faixa operacional futura.';

COMMIT;
