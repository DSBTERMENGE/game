-- Migração 002: cadastro e resumo estatístico dos padrões.
-- Compatível com PostgreSQL 12 ou superior.
-- Pressupõe conexão prévia ao database correto.

BEGIN;

CREATE TABLE padroes (
    id_padrao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    padrao_cod VARCHAR(20) NOT NULL,
    padrao_nome VARCHAR(200) NOT NULL,
    padrao_descr TEXT NOT NULL,
    num_oco INTEGER,
    intervalo_medio NUMERIC(12,6),
    desv_padrao NUMERIC(12,6),

    CONSTRAINT uk_padroes_padrao_cod UNIQUE (padrao_cod),
    CONSTRAINT uk_padroes_padrao_nome UNIQUE (padrao_nome),
    CONSTRAINT ck_padroes_padrao_cod_formato
        CHECK (padrao_cod ~ '^PD_[0-9]{3,}$'),
    CONSTRAINT ck_padroes_padrao_nome_preenchido
        CHECK (BTRIM(padrao_nome) <> ''),
    CONSTRAINT ck_padroes_padrao_descr_preenchida
        CHECK (BTRIM(padrao_descr) <> ''),
    CONSTRAINT ck_padroes_num_oco
        CHECK (num_oco IS NULL OR num_oco >= 0),
    CONSTRAINT ck_padroes_intervalo_medio
        CHECK (intervalo_medio IS NULL OR intervalo_medio >= 0),
    CONSTRAINT ck_padroes_desv_padrao
        CHECK (desv_padrao IS NULL OR desv_padrao >= 0),
    CONSTRAINT ck_padroes_estado_estatistico CHECK (
        (
            num_oco IS NULL
            AND intervalo_medio IS NULL
            AND desv_padrao IS NULL
        )
        OR
        (
            num_oco BETWEEN 0 AND 1
            AND intervalo_medio IS NULL
            AND desv_padrao IS NULL
        )
        OR
        (
            num_oco >= 2
            AND intervalo_medio IS NOT NULL
            AND desv_padrao IS NOT NULL
        )
    )
);

COMMENT ON TABLE padroes IS
    'Cadastro dos padrões e resumo estatístico calculado sobre os resultados históricos.';
COMMENT ON COLUMN padroes.id_padrao IS
    'Identificador interno automático, sem significado funcional.';
COMMENT ON COLUMN padroes.padrao_cod IS
    'Código estável e único usado para vincular o cadastro ao detector Python.';
COMMENT ON COLUMN padroes.padrao_nome IS
    'Nome curto e editável apresentado ao usuário.';
COMMENT ON COLUMN padroes.padrao_descr IS
    'Descrição detalhada e editável da regra reconhecida pelo detector.';
COMMENT ON COLUMN padroes.num_oco IS
    'Quantidade de resultados históricos que correspondem ao padrão; nulo antes do cálculo.';
COMMENT ON COLUMN padroes.intervalo_medio IS
    'Média dos intervalos entre ocorrências; nula quando existem menos de duas ocorrências.';
COMMENT ON COLUMN padroes.desv_padrao IS
    'Desvio-padrão populacional dos intervalos; nulo quando existem menos de duas ocorrências.';

COMMIT;
