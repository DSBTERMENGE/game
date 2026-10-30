-- Migração 001: estrutura inicial do Game / MSen.
-- Compatível com PostgreSQL 12 ou superior.
-- Pressupõe conexão prévia ao database correto.

BEGIN;

CREATE TABLE IF NOT EXISTS schema_migrations (
    versao VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL,
    aplicada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_schema_migrations_versao_preenchida
        CHECK (BTRIM(versao) <> ''),
    CONSTRAINT ck_schema_migrations_nome_preenchido
        CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_schema_migrations_checksum_sha256
        CHECK (checksum_sha256 ~ '^[0-9a-f]{64}$')
);

COMMENT ON TABLE schema_migrations IS
    'Controle das migrações PostgreSQL aplicadas pelo projeto.';
COMMENT ON COLUMN schema_migrations.checksum_sha256 IS
    'SHA-256 em hexadecimal minúsculo do arquivo de migração aplicado.';

CREATE TABLE IF NOT EXISTS resultados (
    id_resultado BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_resultado DATE NOT NULL,
    numero_ap INTEGER NOT NULL,
    res_01 SMALLINT NOT NULL,
    res_02 SMALLINT NOT NULL,
    res_03 SMALLINT NOT NULL,
    res_04 SMALLINT NOT NULL,
    res_05 SMALLINT NOT NULL,
    res_06 SMALLINT NOT NULL,
    soma_res SMALLINT NOT NULL,
    media_aritmetica_res NUMERIC(10,6) NOT NULL,
    mediana_res NUMERIC(4,1) NOT NULL,
    desvio_padrao_media NUMERIC(10,6) NOT NULL,
    media_coordenada_x NUMERIC(7,6) NOT NULL,
    media_coordenada_y NUMERIC(7,6) NOT NULL,
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_resultados_numero_ap UNIQUE (numero_ap),
    CONSTRAINT ck_resultados_numero_ap_positivo CHECK (numero_ap > 0),
    CONSTRAINT ck_resultados_res_01_intervalo CHECK (res_01 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_02_intervalo CHECK (res_02 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_03_intervalo CHECK (res_03 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_04_intervalo CHECK (res_04 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_05_intervalo CHECK (res_05 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_res_06_intervalo CHECK (res_06 BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_distintos CHECK (
        res_01 <> res_02
        AND res_01 <> res_03
        AND res_01 <> res_04
        AND res_01 <> res_05
        AND res_01 <> res_06
        AND res_02 <> res_03
        AND res_02 <> res_04
        AND res_02 <> res_05
        AND res_02 <> res_06
        AND res_03 <> res_04
        AND res_03 <> res_05
        AND res_03 <> res_06
        AND res_04 <> res_05
        AND res_04 <> res_06
        AND res_05 <> res_06
    ),
    CONSTRAINT ck_resultados_soma_res CHECK (soma_res BETWEEN 21 AND 345),
    CONSTRAINT ck_resultados_media_aritmetica_res
        CHECK (media_aritmetica_res BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_mediana_res CHECK (mediana_res BETWEEN 1 AND 60),
    CONSTRAINT ck_resultados_desvio_padrao_media
        CHECK (desvio_padrao_media >= 0),
    CONSTRAINT ck_resultados_media_coordenada_x
        CHECK (media_coordenada_x BETWEEN 0 AND 9),
    CONSTRAINT ck_resultados_media_coordenada_y
        CHECK (media_coordenada_y BETWEEN 0 AND 5),
    CONSTRAINT ck_resultados_versao_calculo CHECK (versao_calculo > 0)
);

CREATE INDEX IF NOT EXISTS idx_resultados_data_resultado
    ON resultados (data_resultado);

COMMENT ON TABLE resultados IS
    'Resultados históricos e cálculos próprios de cada apresentação.';
COMMENT ON COLUMN resultados.id_resultado IS
    'Identificador interno automático, sem significado histórico.';
COMMENT ON COLUMN resultados.numero_ap IS
    'Número oficial e único da apresentação/concurso.';
COMMENT ON COLUMN resultados.res_01 IS 'Primeiro resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_02 IS 'Segundo resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_03 IS 'Terceiro resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_04 IS 'Quarto resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_05 IS 'Quinto resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.res_06 IS 'Sexto resultado na ordem da fonte.';
COMMENT ON COLUMN resultados.desvio_padrao_media IS
    'Desvio-padrão populacional dos seis resultados.';
COMMENT ON COLUMN resultados.media_coordenada_x IS
    'Média horizontal no sistema lógico de coordenadas da matriz.';
COMMENT ON COLUMN resultados.media_coordenada_y IS
    'Média vertical no sistema lógico de coordenadas da matriz.';

CREATE TABLE IF NOT EXISTS analise_geometrica_resultado (
    id_resultado BIGINT PRIMARY KEY,
    extensao_aberta NUMERIC(20,12) NOT NULL,
    perimetro_fechado NUMERIC(20,12) NOT NULL,
    quantidade_regioes SMALLINT NOT NULL,
    area_total NUMERIC(20,12) NOT NULL,
    centro_gravidade_x NUMERIC(20,12),
    centro_gravidade_y NUMERIC(20,12),
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_analise_geometrica_resultado
        FOREIGN KEY (id_resultado) REFERENCES resultados (id_resultado)
        ON DELETE CASCADE,
    CONSTRAINT ck_analise_geometrica_extensao_positiva
        CHECK (extensao_aberta > 0),
    CONSTRAINT ck_analise_geometrica_perimetro
        CHECK (perimetro_fechado >= extensao_aberta),
    CONSTRAINT ck_analise_geometrica_quantidade_regioes
        CHECK (quantidade_regioes >= 0),
    CONSTRAINT ck_analise_geometrica_area CHECK (area_total >= 0),
    CONSTRAINT ck_analise_geometrica_estado_area CHECK (
        (quantidade_regioes = 0 AND area_total = 0)
        OR (quantidade_regioes > 0 AND area_total > 0)
    ),
    CONSTRAINT ck_analise_geometrica_centro_completo CHECK (
        (centro_gravidade_x IS NULL) = (centro_gravidade_y IS NULL)
    ),
    CONSTRAINT ck_analise_geometrica_estado_centro CHECK (
        (area_total = 0 AND centro_gravidade_x IS NULL)
        OR (area_total > 0 AND centro_gravidade_x IS NOT NULL)
    ),
    CONSTRAINT ck_analise_geometrica_centro_x CHECK (
        centro_gravidade_x IS NULL OR centro_gravidade_x BETWEEN 0 AND 9
    ),
    CONSTRAINT ck_analise_geometrica_centro_y CHECK (
        centro_gravidade_y IS NULL OR centro_gravidade_y BETWEEN 0 AND 5
    ),
    CONSTRAINT ck_analise_geometrica_versao_calculo CHECK (versao_calculo > 0)
);

COMMENT ON TABLE analise_geometrica_resultado IS
    'Medidas derivadas da figura formada pelas dezenas em ordem crescente.';
COMMENT ON COLUMN analise_geometrica_resultado.extensao_aberta IS
    'Soma dos cinco segmentos consecutivos em unidades lógicas.';
COMMENT ON COLUMN analise_geometrica_resultado.perimetro_fechado IS
    'Extensão aberta acrescida do segmento entre a maior e a menor dezena.';
COMMENT ON COLUMN analise_geometrica_resultado.quantidade_regioes IS
    'Quantidade de regiões fechadas e limitadas identificadas na rede planar.';
COMMENT ON COLUMN analise_geometrica_resultado.area_total IS
    'Soma positiva das áreas de todas as regiões fechadas.';
COMMENT ON COLUMN analise_geometrica_resultado.centro_gravidade_x IS
    'Coordenada horizontal do centro de gravidade ponderado pelas áreas.';
COMMENT ON COLUMN analise_geometrica_resultado.centro_gravidade_y IS
    'Coordenada vertical do centro de gravidade ponderado pelas áreas.';

CREATE TABLE IF NOT EXISTS frequencia_de_resultado (
    id_dezena SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dezena SMALLINT NOT NULL,
    prim_oco INTEGER,
    ult_oco INTEGER,
    num_oco INTEGER NOT NULL DEFAULT 0,
    qtd_intervalos INTEGER NOT NULL DEFAULT 0,
    intervalo_minimo INTEGER,
    intervalo_maximo INTEGER,
    media_oco NUMERIC(12,6),
    mediana_oco NUMERIC(12,6),
    desv_padrao_oco NUMERIC(12,6),
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_frequencia_de_resultado_dezena UNIQUE (dezena),
    CONSTRAINT ck_frequencia_de_resultado_dezena
        CHECK (dezena BETWEEN 1 AND 60),
    CONSTRAINT ck_frequencia_de_resultado_num_oco CHECK (num_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_intervalos CHECK (
        (num_oco < 2 AND qtd_intervalos = 0
            AND intervalo_minimo IS NULL AND intervalo_maximo IS NULL)
        OR
        (num_oco >= 2 AND qtd_intervalos = num_oco - 1
            AND intervalo_minimo > 0
            AND intervalo_maximo >= intervalo_minimo)
    ),
    CONSTRAINT ck_frequencia_de_resultado_ordem_ocorrencias
        CHECK (prim_oco IS NULL OR ult_oco IS NULL OR prim_oco <= ult_oco),
    CONSTRAINT ck_frequencia_de_resultado_estado CHECK (
        (
            num_oco = 0
            AND prim_oco IS NULL
            AND ult_oco IS NULL
            AND media_oco IS NULL
            AND mediana_oco IS NULL
            AND desv_padrao_oco IS NULL
        )
        OR
        (
            num_oco = 1
            AND prim_oco IS NOT NULL
            AND ult_oco = prim_oco
            AND media_oco IS NULL
            AND mediana_oco IS NULL
            AND desv_padrao_oco IS NULL
        )
        OR
        (
            num_oco >= 2
            AND prim_oco IS NOT NULL
            AND ult_oco IS NOT NULL
            AND media_oco IS NOT NULL
            AND mediana_oco IS NOT NULL
            AND desv_padrao_oco IS NOT NULL
        )
    ),
    CONSTRAINT ck_frequencia_de_resultado_media_oco
        CHECK (media_oco IS NULL OR media_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_mediana_oco
        CHECK (mediana_oco IS NULL OR mediana_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_desv_padrao_oco
        CHECK (desv_padrao_oco IS NULL OR desv_padrao_oco >= 0),
    CONSTRAINT ck_frequencia_de_resultado_versao_calculo
        CHECK (versao_calculo > 0),
    CONSTRAINT fk_frequencia_de_resultado_prim_oco
        FOREIGN KEY (prim_oco)
        REFERENCES resultados (numero_ap)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_frequencia_de_resultado_ult_oco
        FOREIGN KEY (ult_oco)
        REFERENCES resultados (numero_ap)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE frequencia_de_resultado IS
    'Resumo derivado de ocorrências e intervalos para cada dezena de 01 a 60.';
COMMENT ON COLUMN frequencia_de_resultado.prim_oco IS
    'Número da primeira apresentação em que a dezena ocorreu.';
COMMENT ON COLUMN frequencia_de_resultado.ult_oco IS
    'Número da última apresentação em que a dezena ocorreu.';
COMMENT ON COLUMN frequencia_de_resultado.num_oco IS
    'Quantidade total de ocorrências da dezena.';
COMMENT ON COLUMN frequencia_de_resultado.qtd_intervalos IS
    'Quantidade de intervalos entre ocorrências simples consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.intervalo_minimo IS
    'Menor intervalo observado entre ocorrências simples consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.intervalo_maximo IS
    'Maior intervalo observado entre ocorrências simples consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.media_oco IS
    'Média dos intervalos entre ocorrências consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.mediana_oco IS
    'Mediana dos intervalos entre ocorrências consecutivas.';
COMMENT ON COLUMN frequencia_de_resultado.desv_padrao_oco IS
    'Desvio-padrão populacional dos intervalos entre ocorrências.';

INSERT INTO frequencia_de_resultado (dezena)
SELECT dezena
FROM GENERATE_SERIES(1, 60) AS dezenas(dezena)
ON CONFLICT (dezena) DO NOTHING;

CREATE TABLE IF NOT EXISTS configuracao_frequencia_dezenas (
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

CREATE OR REPLACE FUNCTION proteger_configuracao_frequencia_dezenas()
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

DROP TRIGGER IF EXISTS tg_proteger_configuracao_frequencia_dezenas
    ON configuracao_frequencia_dezenas;
CREATE TRIGGER tg_proteger_configuracao_frequencia_dezenas
BEFORE UPDATE OR DELETE ON configuracao_frequencia_dezenas
FOR EACH ROW EXECUTE FUNCTION proteger_configuracao_frequencia_dezenas();

CREATE OR REPLACE FUNCTION proteger_configuracao_frequencia_dezenas()
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

DROP TRIGGER IF EXISTS tg_proteger_configuracao_frequencia_dezenas
    ON configuracao_frequencia_dezenas;
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
) ON CONFLICT (id_configuracao) DO NOTHING;

CREATE TABLE IF NOT EXISTS geracoes_frequencia_dezenas (
    id_geracao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_configuracao SMALLINT NOT NULL DEFAULT 1,
    assinatura_configuracao CHAR(64) NOT NULL,
    configuracao_json JSONB NOT NULL,
    assinatura_resultados CHAR(64) NOT NULL,
    quantidade_resultados INTEGER NOT NULL,
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
    CONSTRAINT ck_geracao_frequencia_assinatura_resultados CHECK (
        assinatura_resultados ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT ck_geracao_frequencia_quantidade_resultados CHECK (
        quantidade_resultados > 0
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

CREATE UNIQUE INDEX IF NOT EXISTS uk_geracao_frequencia_ativa
    ON geracoes_frequencia_dezenas (estado)
    WHERE estado = 'ATIVA';

CREATE TABLE IF NOT EXISTS historico_frequencia_dezenas (
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
        AND ((quantidade_ocorrencias < 2 AND quantidade_intervalos = 0)
            OR (quantidade_ocorrencias >= 2
                AND quantidade_intervalos = quantidade_ocorrencias - 1))
    ),
    CONSTRAINT ck_historico_frequencia_estado_estatistico CHECK (
        (quantidade_intervalos = 0
            AND intervalo_minimo IS NULL AND intervalo_maximo IS NULL
            AND media_intervalos IS NULL AND mediana_intervalos IS NULL
            AND desvio_padrao_intervalos IS NULL AND previsao_central IS NULL
            AND limite_inferior_exato IS NULL AND limite_superior_exato IS NULL
            AND concurso_limite_inferior IS NULL
            AND concurso_limite_superior IS NULL)
        OR
        (quantidade_intervalos > 0
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
            AND concurso_limite_superior >= concurso_limite_inferior)
    )
);

CREATE INDEX IF NOT EXISTS ix_historico_frequencia_grafico
    ON historico_frequencia_dezenas (
        id_geracao, dezena, tipo_evento, numero_do_concurso
    );
CREATE INDEX IF NOT EXISTS ix_historico_frequencia_concurso
    ON historico_frequencia_dezenas (id_geracao, numero_do_concurso);

CREATE TABLE IF NOT EXISTS configuracao_frequencia_dezenas (
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

INSERT INTO configuracao_frequencia_dezenas (
    id_configuracao, nome, concurso_inicial, tamanho_inicial, regra_janela,
    tipo_evento, metodo_faixa, parametro_faixa, unidade_parametro,
    regra_arredondamento, versao_calculo, assinatura_sha256
) VALUES (
    1, 'Estudo acumulado inicial', 1, 500, 'INICIO_FIXO_FINAL_EXPANSIVO',
    'TODOS', 'MEDIA_MAIS_MENOS_DESVIO_PADRAO', 1.000000,
    'MULTIPLICADOR_DESVIO_PADRAO', 'LIMITES_EXTERNOS', 1,
    'a24e8a50eff1957fffcbbc923314e33c852a4333322e2b3d57c58e0b6aeb941f'
) ON CONFLICT (id_configuracao) DO NOTHING;

CREATE TABLE IF NOT EXISTS padroes_grupo (
    id_grupo BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    grupo_cod VARCHAR(20) NOT NULL,
    grupo_nome VARCHAR(200) NOT NULL,
    grupo_descr TEXT NOT NULL,

    CONSTRAINT uk_padroes_grupo_grupo_cod UNIQUE (grupo_cod),
    CONSTRAINT ck_padroes_grupo_grupo_cod_formato
        CHECK (grupo_cod ~ '^PG_[0-9]{3,}$'),
    CONSTRAINT ck_padroes_grupo_grupo_nome_preenchido
        CHECK (BTRIM(grupo_nome) <> ''),
    CONSTRAINT ck_padroes_grupo_grupo_descr_preenchida
        CHECK (BTRIM(grupo_descr) <> '')
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_padroes_grupo_nome_normalizado
    ON padroes_grupo (LOWER(BTRIM(grupo_nome)));

COMMENT ON TABLE padroes_grupo IS
    'Grupos conceituais usados para organizar padrões relacionados.';
COMMENT ON COLUMN padroes_grupo.id_grupo IS
    'Identificador interno automático do grupo.';
COMMENT ON COLUMN padroes_grupo.grupo_cod IS
    'Código estável e único do grupo, gerado pelo sistema.';
COMMENT ON COLUMN padroes_grupo.grupo_nome IS
    'Nome curto e editável do conceito agrupador.';
COMMENT ON COLUMN padroes_grupo.grupo_descr IS
    'Descrição detalhada e editável do conceito agrupador.';

INSERT INTO padroes_grupo (grupo_cod, grupo_nome, grupo_descr)
VALUES
(
    'PG_001',
    'Dezenas sequenciais',
    'Padrões baseados em grupos de dezenas consecutivas no resultado.'
),
(
    'PG_002',
    'Dezenas na mesma coluna',
    'Padrões baseados em dezenas posicionadas na mesma coluna da matriz.'
),
(
    'PG_003',
    'Dezenas na mesma linha',
    'Padrões baseados na quantidade de dezenas posicionadas na mesma linha da matriz.'
)
ON CONFLICT (grupo_cod) DO NOTHING;

CREATE SEQUENCE IF NOT EXISTS padroes_grupo_codigo_seq
    AS BIGINT MINVALUE 1 START WITH 4;

SELECT SETVAL(
    'padroes_grupo_codigo_seq',
    GREATEST(
        3,
        COALESCE(MAX(SUBSTRING(grupo_cod FROM 4)::BIGINT), 3)
    ),
    TRUE
)
FROM padroes_grupo;

COMMENT ON SEQUENCE padroes_grupo_codigo_seq IS
    'Gera a parte numérica de grupo_cod sem reutilizar códigos excluídos.';

CREATE TABLE IF NOT EXISTS padroes_subgrupo (
    id_padrao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_grupo BIGINT NOT NULL,
    padrao_cod VARCHAR(20) NOT NULL,
    padrao_nome VARCHAR(200) NOT NULL,
    padrao_descr TEXT NOT NULL,
    num_oco INTEGER,
    total_sorteios INTEGER,
    percentual_ocorrencia NUMERIC(9,6),
    intervalo_medio NUMERIC(12,6),
    desv_padrao NUMERIC(12,6),

    CONSTRAINT uk_padroes_padrao_cod UNIQUE (padrao_cod),
    CONSTRAINT ck_padroes_padrao_cod_formato
        CHECK (padrao_cod ~ '^PD_[0-9]{3,}$'),
    CONSTRAINT ck_padroes_padrao_nome_preenchido
        CHECK (BTRIM(padrao_nome) <> ''),
    CONSTRAINT ck_padroes_padrao_descr_preenchida
        CHECK (BTRIM(padrao_descr) <> ''),
    CONSTRAINT ck_padroes_num_oco
        CHECK (num_oco IS NULL OR num_oco >= 0),
    CONSTRAINT ck_padroes_total_sorteios
        CHECK (total_sorteios IS NULL OR total_sorteios > 0),
    CONSTRAINT ck_padroes_percentual_ocorrencia
        CHECK (
            percentual_ocorrencia IS NULL
            OR percentual_ocorrencia BETWEEN 0 AND 100
        ),
    CONSTRAINT ck_padroes_fotografia_ocorrencia CHECK (
        (
            total_sorteios IS NULL
            AND percentual_ocorrencia IS NULL
        )
        OR
        (
            total_sorteios IS NOT NULL
            AND num_oco IS NOT NULL
            AND num_oco <= total_sorteios
            AND percentual_ocorrencia IS NOT NULL
            AND percentual_ocorrencia = ROUND(
                num_oco::NUMERIC * 100 / total_sorteios,
                6
            )
        )
    ),
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
    ),
    CONSTRAINT fk_padroes_subgrupo_grupo
        FOREIGN KEY (id_grupo)
        REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_padroes_subgrupo_nome_no_grupo
    ON padroes_subgrupo (id_grupo, LOWER(BTRIM(padrao_nome)));

CREATE UNIQUE INDEX IF NOT EXISTS uk_padroes_subgrupo_grupo_padrao
    ON padroes_subgrupo (id_grupo, id_padrao);

COMMENT ON TABLE padroes_subgrupo IS
    'Padrões específicos vinculados a grupos e suas estatísticas históricas.';
COMMENT ON COLUMN padroes_subgrupo.id_padrao IS
    'Identificador interno automático, sem significado funcional.';
COMMENT ON COLUMN padroes_subgrupo.id_grupo IS
    'Grupo conceitual obrigatório ao qual o padrão pertence.';
COMMENT ON COLUMN padroes_subgrupo.padrao_cod IS
    'Código estável e único usado para vincular o cadastro ao detector Python.';
COMMENT ON COLUMN padroes_subgrupo.padrao_nome IS
    'Nome curto e editável apresentado ao usuário.';
COMMENT ON COLUMN padroes_subgrupo.padrao_descr IS
    'Descrição detalhada e editável da regra reconhecida pelo detector.';
COMMENT ON COLUMN padroes_subgrupo.num_oco IS
    'Quantidade de resultados históricos que correspondem ao padrão; nulo antes do cálculo.';
COMMENT ON COLUMN padroes_subgrupo.total_sorteios IS
    'Total de sorteios da fotografia histórica atual; nulo antes do cálculo.';
COMMENT ON COLUMN padroes_subgrupo.percentual_ocorrencia IS
    'Incidência atual do padrão: num_oco / total_sorteios * 100, com seis casas.';
COMMENT ON COLUMN padroes_subgrupo.intervalo_medio IS
    'Média dos intervalos entre ocorrências; nula quando existem menos de duas ocorrências.';
COMMENT ON COLUMN padroes_subgrupo.desv_padrao IS
    'Desvio-padrão populacional dos intervalos; nulo quando existem menos de duas ocorrências.';

INSERT INTO padroes_subgrupo (id_grupo, padrao_cod, padrao_nome, padrao_descr)
SELECT grupo.id_grupo, dados.padrao_cod, dados.padrao_nome, dados.padrao_descr
FROM padroes_grupo AS grupo
CROSS JOIN (
    VALUES
    (
        'PD_001',
        'Duas dezenas sequenciais',
        'O maior grupo consecutivo do resultado possui exatamente duas dezenas.'
    ),
    (
        'PD_002',
        'Três dezenas sequenciais',
        'O maior grupo consecutivo do resultado possui exatamente três dezenas.'
    ),
    (
        'PD_003',
        'Mais de três dezenas sequenciais',
        'O maior grupo consecutivo do resultado possui quatro, cinco ou seis dezenas.'
    )
) AS dados(padrao_cod, padrao_nome, padrao_descr)
WHERE grupo.grupo_cod = 'PG_001'
ON CONFLICT (padrao_cod) DO NOTHING;

INSERT INTO padroes_subgrupo (id_grupo, padrao_cod, padrao_nome, padrao_descr)
SELECT grupo.id_grupo, dados.padrao_cod, dados.padrao_nome, dados.padrao_descr
FROM padroes_grupo AS grupo
CROSS JOIN (
    VALUES
    (
        'PD_004',
        'Duas dezenas em linhas subjacentes na mesma coluna',
        'O maior grupo vertical possui exatamente duas dezenas na mesma coluna e em linhas imediatamente consecutivas.'
    ),
    (
        'PD_005',
        'Três dezenas em linhas subjacentes na mesma coluna',
        'O maior grupo vertical possui exatamente três dezenas na mesma coluna e em linhas imediatamente consecutivas.'
    ),
    (
        'PD_006',
        'Mais de três dezenas em linhas subjacentes na mesma coluna',
        'O maior grupo vertical possui quatro, cinco ou seis dezenas na mesma coluna e em linhas imediatamente consecutivas.'
    )
) AS dados(padrao_cod, padrao_nome, padrao_descr)
WHERE grupo.grupo_cod = 'PG_002'
ON CONFLICT (padrao_cod) DO NOTHING;

INSERT INTO padroes_subgrupo (id_grupo, padrao_cod, padrao_nome, padrao_descr)
SELECT grupo.id_grupo, dados.padrao_cod, dados.padrao_nome, dados.padrao_descr
FROM padroes_grupo AS grupo
CROSS JOIN (
    VALUES
    (
        'PD_007',
        'Duas dezenas na mesma linha',
        'Duas dezenas do resultado estão na mesma linha, independentemente de serem sequenciais.'
    ),
    (
        'PD_008',
        'Três dezenas na mesma linha',
        'Três dezenas do resultado estão na mesma linha, independentemente de serem sequenciais.'
    ),
    (
        'PD_009',
        'Mais de três dezenas na mesma linha',
        'Quatro, cinco ou seis dezenas do resultado estão na mesma linha, independentemente de serem sequenciais.'
    )
) AS dados(padrao_cod, padrao_nome, padrao_descr)
WHERE grupo.grupo_cod = 'PG_003'
ON CONFLICT (padrao_cod) DO NOTHING;

CREATE SEQUENCE IF NOT EXISTS padroes_subgrupo_codigo_seq
    AS BIGINT MINVALUE 1 START WITH 10;

SELECT SETVAL(
    'padroes_subgrupo_codigo_seq',
    GREATEST(
        9,
        COALESCE(MAX(SUBSTRING(padrao_cod FROM 4)::BIGINT), 9)
    ),
    TRUE
)
FROM padroes_subgrupo;

COMMENT ON SEQUENCE padroes_subgrupo_codigo_seq IS
    'Gera a parte numérica de padrao_cod sem reutilizar códigos excluídos.';

CREATE TABLE IF NOT EXISTS resultado_classificacao_padrao (
    id_classificacao BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_resultado BIGINT NOT NULL,
    id_grupo BIGINT NOT NULL,
    id_padrao BIGINT NOT NULL,
    versao_calculo SMALLINT NOT NULL DEFAULT 1,
    calculado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_resultado_classificacao_resultado_grupo
        UNIQUE (id_resultado, id_grupo),
    CONSTRAINT fk_resultado_classificacao_resultado
        FOREIGN KEY (id_resultado) REFERENCES resultados (id_resultado)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_resultado_classificacao_grupo
        FOREIGN KEY (id_grupo) REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_resultado_classificacao_padrao_do_grupo
        FOREIGN KEY (id_grupo, id_padrao)
        REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT ck_resultado_classificacao_versao
        CHECK (versao_calculo > 0)
);

CREATE INDEX IF NOT EXISTS ix_resultado_classificacao_grupo_padrao
    ON resultado_classificacao_padrao (id_grupo, id_padrao);

COMMENT ON TABLE resultado_classificacao_padrao IS
    'Ocorrências reais de padrões identificadas nos resultados históricos.';
COMMENT ON COLUMN resultado_classificacao_padrao.id_padrao IS
    'Padrão efetivamente identificado no resultado e no grupo.';
COMMENT ON COLUMN resultado_classificacao_padrao.versao_calculo IS
    'Versão da função classificadora usada para produzir o registro.';
COMMENT ON COLUMN resultado_classificacao_padrao.calculado_em IS
    'Data e hora em que a classificação foi calculada.';

CREATE TABLE IF NOT EXISTS amostras_validacao (
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

CREATE TABLE IF NOT EXISTS criterios_validacao (
    id_criterio BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(80) NOT NULL,
    nome VARCHAR(200) NOT NULL,
    categoria VARCHAR(20) NOT NULL,
    funcao_python VARCHAR(300) NOT NULL,
    tipo_resultado VARCHAR(20) NOT NULL,
    precisao_decimal SMALLINT,
    id_grupo BIGINT,
    assinatura_funcao CHAR(64) NOT NULL,
    assinatura_regra CHAR(64) NOT NULL,
    assinatura_regra CHAR(64) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_criterios_validacao_codigo UNIQUE (codigo),
    CONSTRAINT uk_criterios_validacao_id_grupo UNIQUE (id_criterio, id_grupo),
    CONSTRAINT ck_criterios_validacao_codigo_preenchido CHECK (BTRIM(codigo) <> ''),
    CONSTRAINT ck_criterios_validacao_nome_preenchido CHECK (BTRIM(nome) <> ''),
    CONSTRAINT ck_criterios_validacao_funcao_preenchida
        CHECK (BTRIM(funcao_python) <> ''),
    CONSTRAINT ck_criterios_validacao_categoria
        CHECK (categoria IN ('ESTATISTICA', 'GEOMETRIA', 'PADRAO')),
    CONSTRAINT ck_criterios_validacao_tipo
        CHECK (tipo_resultado IN ('INTEIRO', 'DECIMAL', 'PADRAO')),
    CONSTRAINT ck_criterios_validacao_categoria_tipo_grupo CHECK (
        (categoria = 'PADRAO' AND tipo_resultado = 'PADRAO' AND id_grupo IS NOT NULL)
        OR
        (categoria IN ('ESTATISTICA', 'GEOMETRIA')
            AND tipo_resultado IN ('INTEIRO', 'DECIMAL') AND id_grupo IS NULL)
    ),
    CONSTRAINT ck_criterios_validacao_precisao CHECK (
        (tipo_resultado = 'DECIMAL' AND precisao_decimal BETWEEN 0 AND 18)
        OR
        (tipo_resultado IN ('INTEIRO', 'PADRAO') AND precisao_decimal IS NULL)
    ),
    CONSTRAINT ck_criterios_validacao_assinatura
        CHECK (assinatura_funcao ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_criterios_validacao_assinatura_regra
        CHECK (assinatura_regra ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_criterios_validacao_assinatura_regra
        CHECK (assinatura_regra ~ '^[0-9a-f]{64}$'),
    CONSTRAINT ck_criterios_validacao_estado
        CHECK (estado IN ('PENDENTE', 'APROVADO', 'REPROVADO')),
    CONSTRAINT fk_criterios_validacao_grupo
        FOREIGN KEY (id_grupo) REFERENCES padroes_grupo (id_grupo)
        ON UPDATE RESTRICT ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS avaliacoes_validacao (
    id_resultado BIGINT NOT NULL,
    id_criterio BIGINT NOT NULL,
    id_grupo BIGINT,
    referencia_conferida BOOLEAN NOT NULL DEFAULT FALSE,
    estado_valor_esperado VARCHAR(30),
    valor_esperado NUMERIC,
    estado_valor_calculado VARCHAR(30),
    valor_calculado NUMERIC,
    estado_padrao_esperado VARCHAR(30),
    id_padrao_esperado BIGINT,
    estado_padrao_calculado VARCHAR(30),
    id_padrao_calculado BIGINT,
    executado BOOLEAN NOT NULL DEFAULT FALSE,
    assinatura_executada CHAR(64),
    aprovado CHAR(1),
    diferenca NUMERIC,
    calculado_em TIMESTAMPTZ,
    referencia_origem VARCHAR(30),
    referencia_revisor VARCHAR(200),
    referencia_observacao TEXT,
    referencia_conferida_em TIMESTAMPTZ,

    CONSTRAINT pk_avaliacoes_validacao PRIMARY KEY (id_resultado, id_criterio),
    CONSTRAINT ck_avaliacoes_validacao_modo CHECK (
        (id_grupo IS NULL
            AND estado_padrao_esperado IS NULL AND id_padrao_esperado IS NULL
            AND estado_padrao_calculado IS NULL AND id_padrao_calculado IS NULL)
        OR
        (id_grupo IS NOT NULL
            AND estado_valor_esperado IS NULL AND valor_esperado IS NULL
            AND estado_valor_calculado IS NULL AND valor_calculado IS NULL
            AND diferenca IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_referencia_numerica CHECK (
        id_grupo IS NOT NULL
        OR
        (referencia_conferida
            AND estado_valor_esperado IN ('VALOR_IDENTIFICADO', 'SEM_VALOR')
            AND ((estado_valor_esperado = 'VALOR_IDENTIFICADO'
                    AND valor_esperado IS NOT NULL)
                OR (estado_valor_esperado = 'SEM_VALOR'
                    AND valor_esperado IS NULL)))
        OR
        (NOT referencia_conferida
            AND estado_valor_esperado IS NULL AND valor_esperado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_referencia_padrao CHECK (
        id_grupo IS NULL
        OR
        (
            referencia_conferida
            AND estado_padrao_esperado IN ('PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA')
            AND (
                (estado_padrao_esperado = 'PADRAO_IDENTIFICADO'
                    AND id_padrao_esperado IS NOT NULL)
                OR
                (estado_padrao_esperado = 'SEM_CORRESPONDENCIA'
                    AND id_padrao_esperado IS NULL)
            )
        )
        OR
        (NOT referencia_conferida
            AND estado_padrao_esperado IS NULL AND id_padrao_esperado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_execucao_numerica CHECK (
        id_grupo IS NOT NULL
        OR
        (executado
            AND estado_valor_calculado IN ('VALOR_IDENTIFICADO', 'SEM_VALOR')
            AND ((estado_valor_calculado = 'VALOR_IDENTIFICADO'
                    AND valor_calculado IS NOT NULL)
                OR (estado_valor_calculado = 'SEM_VALOR'
                    AND valor_calculado IS NULL)))
        OR
        (NOT executado
            AND estado_valor_calculado IS NULL AND valor_calculado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_execucao_padrao CHECK (
        id_grupo IS NULL
        OR
        (
            executado
            AND estado_padrao_calculado IN ('PADRAO_IDENTIFICADO', 'SEM_CORRESPONDENCIA')
            AND (
                (estado_padrao_calculado = 'PADRAO_IDENTIFICADO'
                    AND id_padrao_calculado IS NOT NULL)
                OR
                (estado_padrao_calculado = 'SEM_CORRESPONDENCIA'
                    AND id_padrao_calculado IS NULL)
            )
        )
        OR
        (NOT executado
            AND estado_padrao_calculado IS NULL AND id_padrao_calculado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_execucao CHECK (
        (executado
            AND assinatura_executada ~ '^[0-9a-f]{64}$'
            AND calculado_em IS NOT NULL)
        OR
        (NOT executado
            AND assinatura_executada IS NULL
            AND calculado_em IS NULL
            AND diferenca IS NULL
            AND aprovado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_aprovado CHECK (
        aprovado IS NULL OR aprovado IN ('S', 'N')
    ),
    CONSTRAINT ck_avaliacoes_validacao_comparacao CHECK (
        (referencia_conferida AND executado AND aprovado IN ('S', 'N'))
        OR
        ((NOT referencia_conferida OR NOT executado) AND aprovado IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_diferenca CHECK (
        id_grupo IS NOT NULL
        OR
        (referencia_conferida AND executado AND diferenca IS NOT NULL)
        OR
        ((NOT referencia_conferida OR NOT executado) AND diferenca IS NULL)
    ),
    CONSTRAINT ck_avaliacoes_validacao_revisor CHECK (
        (referencia_conferida
            AND referencia_origem IN ('HUMANO', 'IA', 'TESTE_AUTOMATIZADO')
            AND BTRIM(referencia_revisor) <> ''
            AND referencia_conferida_em IS NOT NULL)
        OR
        (NOT referencia_conferida
            AND referencia_origem IS NULL AND referencia_revisor IS NULL
            AND referencia_observacao IS NULL AND referencia_conferida_em IS NULL)
    ),
    CONSTRAINT fk_avaliacoes_validacao_amostra
        FOREIGN KEY (id_resultado) REFERENCES amostras_validacao (id_resultado)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_validacao_criterio
        FOREIGN KEY (id_criterio) REFERENCES criterios_validacao (id_criterio)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_validacao_criterio_grupo
        FOREIGN KEY (id_criterio, id_grupo)
        REFERENCES criterios_validacao (id_criterio, id_grupo)
        ON UPDATE RESTRICT ON DELETE CASCADE,
    CONSTRAINT fk_avaliacoes_validacao_padrao_esperado
        FOREIGN KEY (id_grupo, id_padrao_esperado)
        REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_avaliacoes_validacao_padrao_calculado
        FOREIGN KEY (id_grupo, id_padrao_calculado)
        REFERENCES padroes_subgrupo (id_grupo, id_padrao)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS ix_avaliacoes_validacao_criterio_aprovado
    ON avaliacoes_validacao (id_criterio, aprovado);

COMMENT ON TABLE criterios_validacao IS
    'Catálogo das funções cuja assinatura precisa ser homologada.';
COMMENT ON COLUMN criterios_validacao.assinatura_regra IS
    'SHA-256 automático da definição matemática e semântica do critério.';
COMMENT ON COLUMN criterios_validacao.assinatura_regra IS
    'SHA-256 automático da definição matemática e semântica do critério.';
COMMENT ON TABLE avaliacoes_validacao IS
    'Comparação entre o resultado esperado e o calculado por amostra e função.';
COMMENT ON COLUMN avaliacoes_validacao.aprovado IS
    'NULL enquanto pendente, S quando coincide e N quando diverge.';
COMMENT ON COLUMN avaliacoes_validacao.estado_padrao_esperado IS
    'PADRAO_IDENTIFICADO ou SEM_CORRESPONDENCIA; NULL significa pendente.';
COMMENT ON COLUMN avaliacoes_validacao.estado_valor_esperado IS
    'VALOR_IDENTIFICADO ou SEM_VALOR para referência numérica conferida.';
COMMENT ON COLUMN avaliacoes_validacao.referencia_origem IS
    'Origem independente que produziu e conferiu o esperado.';

CREATE TABLE IF NOT EXISTS estado_algoritmo_selecao (
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

CREATE OR REPLACE FUNCTION proteger_estado_algoritmo_selecao()
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

DROP TRIGGER IF EXISTS tg_proteger_estado_algoritmo_selecao
    ON estado_algoritmo_selecao;
CREATE TRIGGER tg_proteger_estado_algoritmo_selecao
BEFORE UPDATE OR DELETE ON estado_algoritmo_selecao
FOR EACH ROW EXECUTE FUNCTION proteger_estado_algoritmo_selecao();

INSERT INTO estado_algoritmo_selecao (id_estado)
VALUES (1)
ON CONFLICT (id_estado) DO NOTHING;

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

CREATE TABLE IF NOT EXISTS perfis_operacionais_atuais (
    codigo VARCHAR(80) PRIMARY KEY,
    categoria VARCHAR(20) NOT NULL,
    quantidade_resultados BIGINT NOT NULL,
    quantidade_com_valor BIGINT NOT NULL,
    quantidade_ausente BIGINT NOT NULL,
    media NUMERIC,
    desvio_padrao_populacional NUMERIC,
    minimo NUMERIC,
    maximo NUMERIC,
    calculado_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ck_perfis_operacionais_codigo CHECK (BTRIM(codigo) <> ''),
    CONSTRAINT ck_perfis_operacionais_categoria
        CHECK (categoria IN ('ESTATISTICA', 'GEOMETRIA')),
    CONSTRAINT ck_perfis_operacionais_quantidades CHECK (
        quantidade_resultados >= 0
        AND quantidade_com_valor >= 0
        AND quantidade_ausente >= 0
        AND quantidade_com_valor + quantidade_ausente = quantidade_resultados
    ),
    CONSTRAINT ck_perfis_operacionais_valores CHECK (
        (quantidade_com_valor = 0 AND media IS NULL
            AND desvio_padrao_populacional IS NULL
            AND minimo IS NULL AND maximo IS NULL)
        OR
        (quantidade_com_valor > 0 AND media IS NOT NULL
            AND desvio_padrao_populacional IS NOT NULL
            AND minimo IS NOT NULL AND maximo IS NOT NULL AND minimo <= maximo)
    )
);

COMMENT ON TABLE perfis_operacionais_atuais IS
    'Resumo substituível dos perfis numéricos calculados sobre todos os resultados atuais.';
COMMENT ON COLUMN perfis_operacionais_atuais.quantidade_ausente IS
    'Valores nulos legítimos, como centro de gravidade ausente quando não há área.';

COMMIT;
