-- Migração 033: amplia o catálogo com quarenta padrões geométricos candidatos.
--
-- Esta migração apenas cadastra grupos e padrões. Funções detectoras,
-- estatísticas e participação no screener permanecem vazias até implementação,
-- homologação e recálculo próprios.
--
-- Convenção provisória para revisão antes da aplicação:
--   PG_004 recebe diagonais cujo passo numérico é 11;
--   PG_006 recebe diagonais cujo passo numérico é 9.

BEGIN;

LOCK TABLE padroes_grupo IN SHARE ROW EXCLUSIVE MODE;
LOCK TABLE padroes_subgrupo IN SHARE ROW EXCLUSIVE MODE;

CREATE TEMPORARY TABLE grupos_expansao_padroes (
    grupo_ref TEXT PRIMARY KEY,
    grupo_cod_existente VARCHAR(20),
    grupo_nome VARCHAR(200) NOT NULL,
    grupo_descr TEXT NOT NULL
) ON COMMIT DROP;

INSERT INTO grupos_expansao_padroes
    (grupo_ref, grupo_cod_existente, grupo_nome, grupo_descr)
VALUES
    ('DIAGONAL_11', 'PG_004', 'Dezenas em diagonal à esquerda',
     'Alinhamentos diagonais entre centros das dezenas cujo passo numérico é 11.'),
    ('DIAGONAL_9', 'PG_006', 'Dezenas em diagonal à direita',
     'Alinhamentos diagonais entre centros das dezenas cujo passo numérico é 9.'),
    ('DUAS_LINHAS', 'PG_007', 'Dezenas em duas linhas',
     'As seis dezenas ocupam exatamente duas linhas do volante, adjacentes ou não.'),
    ('LINHA_COLUNA', 'PG_008', '1 linha e 1 coluna',
     'As dezenas estão contidas na união de uma única linha com uma única coluna.'),
    ('DUAS_COLUNAS', 'PG_009', 'Dezenas em duas Colunas',
     'As seis dezenas ocupam exatamente duas colunas do volante, adjacentes ou não.'),
    ('POLIGONAIS', NULL, 'Alinhamentos e linhas poligonais',
     'Padrões formados por pontos colineares ou por poucos trechos retilíneos conectados.'),
    ('CIRCULARIDADE', NULL, 'Circularidade',
     'Padrões definidos por distâncias iguais ou aproximadamente iguais em relação a um centro.'),
    ('ARCOS_ELIPSES', NULL, 'Arcos e elipses',
     'Disposições das dezenas sobre arcos circulares ou elipses, dentro de critérios geométricos definidos.') ;

DO $$
DECLARE
    grupo RECORD;
    numero BIGINT;
BEGIN
    IF EXISTS (
        SELECT 1
          FROM grupos_expansao_padroes catalogo
          LEFT JOIN padroes_grupo existente
            ON existente.grupo_cod = catalogo.grupo_cod_existente
         WHERE catalogo.grupo_cod_existente IS NOT NULL
           AND existente.id_grupo IS NULL
    ) THEN
        RAISE EXCEPTION
            'Migração 033 interrompida: um grupo existente esperado não foi encontrado.';
    END IF;

    FOR grupo IN
        SELECT grupo_ref, grupo_nome, grupo_descr
          FROM grupos_expansao_padroes
         WHERE grupo_cod_existente IS NULL
         ORDER BY grupo_ref
    LOOP
        IF NOT EXISTS (
            SELECT 1
              FROM padroes_grupo
             WHERE LOWER(BTRIM(grupo_nome)) = LOWER(BTRIM(grupo.grupo_nome))
        ) THEN
            SELECT NEXTVAL('padroes_grupo_codigo_seq') INTO numero;

            INSERT INTO padroes_grupo (grupo_cod, grupo_nome, grupo_descr)
            VALUES (
                'PG_' || LPAD(numero::TEXT, 3, '0'),
                grupo.grupo_nome,
                grupo.grupo_descr
            );
        END IF;
    END LOOP;
END;
$$;

CREATE TEMPORARY TABLE padroes_expansao (
    ordem SMALLINT PRIMARY KEY,
    grupo_ref TEXT NOT NULL REFERENCES grupos_expansao_padroes (grupo_ref),
    padrao_nome VARCHAR(200) NOT NULL,
    padrao_descr TEXT NOT NULL
) ON COMMIT DROP;

INSERT INTO padroes_expansao (ordem, grupo_ref, padrao_nome, padrao_descr)
VALUES
    (1, 'DIAGONAL_11', 'Duas dezenas na diagonal de passo 11',
     'O maior alinhamento em uma diagonal de passo 11 contém exatamente duas dezenas.'),
    (2, 'DIAGONAL_11', 'Três dezenas na diagonal de passo 11',
     'O maior alinhamento em uma diagonal de passo 11 contém exatamente três dezenas.'),
    (3, 'DIAGONAL_11', 'Quatro dezenas na diagonal de passo 11',
     'O maior alinhamento em uma diagonal de passo 11 contém exatamente quatro dezenas.'),
    (4, 'DIAGONAL_11', 'Cinco dezenas na diagonal de passo 11',
     'O maior alinhamento em uma diagonal de passo 11 contém exatamente cinco dezenas.'),
    (5, 'DIAGONAL_11', 'Seis dezenas na diagonal de passo 11',
     'As seis dezenas pertencem ao mesmo alinhamento diagonal de passo 11.'),
    (6, 'DIAGONAL_11', 'Dois segmentos diagonais separados de passo 11',
     'As dezenas formam dois segmentos distintos e separados em diagonais de passo 11.'),
    (7, 'DIAGONAL_11', 'Três pares diagonais separados de passo 11',
     'As seis dezenas formam três pares distintos em diagonais de passo 11.'),

    (8, 'DIAGONAL_9', 'Duas dezenas na diagonal de passo 9',
     'O maior alinhamento em uma diagonal de passo 9 contém exatamente duas dezenas.'),
    (9, 'DIAGONAL_9', 'Três dezenas na diagonal de passo 9',
     'O maior alinhamento em uma diagonal de passo 9 contém exatamente três dezenas.'),
    (10, 'DIAGONAL_9', 'Quatro dezenas na diagonal de passo 9',
     'O maior alinhamento em uma diagonal de passo 9 contém exatamente quatro dezenas.'),
    (11, 'DIAGONAL_9', 'Cinco dezenas na diagonal de passo 9',
     'O maior alinhamento em uma diagonal de passo 9 contém exatamente cinco dezenas.'),
    (12, 'DIAGONAL_9', 'Seis dezenas na diagonal de passo 9',
     'As seis dezenas pertencem ao mesmo alinhamento diagonal de passo 9.'),
    (13, 'DIAGONAL_9', 'Dois segmentos diagonais separados de passo 9',
     'As dezenas formam dois segmentos distintos e separados em diagonais de passo 9.'),
    (14, 'DIAGONAL_9', 'Três pares diagonais separados de passo 9',
     'As seis dezenas formam três pares distintos em diagonais de passo 9.'),

    (15, 'DUAS_LINHAS', 'Padrão 2L',
     'As seis dezenas ocupam exatamente duas linhas do volante, adjacentes ou não.'),
    (16, 'DUAS_LINHAS', 'Duas linhas adjacentes',
     'As seis dezenas ocupam exatamente duas linhas consecutivas do volante.'),
    (17, 'DUAS_LINHAS', 'Duas linhas não adjacentes',
     'As seis dezenas ocupam exatamente duas linhas não consecutivas do volante.'),
    (18, 'DUAS_LINHAS', 'Duas linhas com distribuição 5 mais 1',
     'Cinco dezenas estão em uma linha e uma dezena está em outra linha.'),
    (19, 'DUAS_LINHAS', 'Duas linhas com distribuição 4 mais 2',
     'Quatro dezenas estão em uma linha e duas dezenas estão em outra linha.'),
    (20, 'DUAS_LINHAS', 'Duas linhas com distribuição 3 mais 3',
     'Três dezenas estão em cada uma das duas linhas ocupadas.'),

    (21, 'DUAS_COLUNAS', 'Dezenas em 2H',
     'As seis dezenas ocupam exatamente duas colunas do volante, adjacentes ou não.'),
    (22, 'DUAS_COLUNAS', 'Duas colunas adjacentes',
     'As seis dezenas ocupam exatamente duas colunas consecutivas do volante.'),
    (23, 'DUAS_COLUNAS', 'Duas colunas não adjacentes',
     'As seis dezenas ocupam exatamente duas colunas não consecutivas do volante.'),
    (24, 'DUAS_COLUNAS', 'Duas colunas com distribuição 5 mais 1',
     'Cinco dezenas estão em uma coluna e uma dezena está em outra coluna.'),
    (25, 'DUAS_COLUNAS', 'Duas colunas com distribuição 4 mais 2',
     'Quatro dezenas estão em uma coluna e duas dezenas estão em outra coluna.'),
    (26, 'DUAS_COLUNAS', 'Duas colunas com distribuição 3 mais 3',
     'Três dezenas estão em cada uma das duas colunas ocupadas.'),

    (27, 'LINHA_COLUNA', '6 dezenas distribuidas em L , T ou Cruz',
     'As seis dezenas estão contidas na união de uma linha e uma coluna do volante.'),
    (28, 'LINHA_COLUNA', 'Configuração em L',
     'As seis dezenas formam uma configuração semelhante à letra L na união de uma linha e uma coluna.'),
    (29, 'LINHA_COLUNA', 'Configuração em T',
     'As seis dezenas formam uma configuração semelhante à letra T na união de uma linha e uma coluna.'),
    (30, 'LINHA_COLUNA', 'Configuração em cruz',
     'As seis dezenas formam uma cruz na união de uma linha e uma coluna.'),

    (31, 'POLIGONAIS', 'Seis dezenas em uma única reta',
     'Os centros das seis dezenas são colineares.'),
    (32, 'POLIGONAIS', 'Exatamente cinco dezenas em uma única reta',
     'Os centros de exatamente cinco dezenas são colineares e a sexta dezena está fora da reta.'),
    (33, 'POLIGONAIS', 'Linha poligonal com dois trechos retilíneos',
     'Os centros das dezenas formam uma linha poligonal composta por dois trechos retilíneos.'),
    (34, 'POLIGONAIS', 'Linha poligonal com três trechos retilíneos',
     'Os centros das dezenas formam uma linha poligonal composta por três trechos retilíneos.'),

    (35, 'CIRCULARIDADE', 'Quatro ou cinco dezenas equidistantes de um vértice',
     'Quatro ou cinco centros de dezenas têm a mesma distância de um dos quatro vértices do volante.'),
    (36, 'CIRCULARIDADE', 'Seis dezenas equidistantes de um vértice',
     'Os seis centros de dezenas têm a mesma distância de um dos quatro vértices do volante.'),
    (37, 'CIRCULARIDADE', 'Seis dezenas em circunferência de centro livre',
     'Os seis centros de dezenas pertencem à mesma circunferência, cujo centro é calculado livremente.'),
    (38, 'CIRCULARIDADE', 'Circunferência aproximada de centro livre',
     'Os seis centros de dezenas aproximam uma circunferência de centro livre dentro de tolerância configurável.'),

    (39, 'ARCOS_ELIPSES', 'Quatro a seis dezenas no mesmo arco circular',
     'De quatro a seis centros de dezenas pertencem ao mesmo arco de uma circunferência.'),
    (40, 'ARCOS_ELIPSES', 'Seis dezenas em elipse aproximada',
     'Os seis centros de dezenas aproximam uma elipse dentro de tolerância e restrições configuráveis.');

DO $$
DECLARE
    padrao RECORD;
    grupo_id BIGINT;
    numero BIGINT;
BEGIN
    FOR padrao IN
        SELECT catalogo.ordem,
               catalogo.grupo_ref,
               catalogo.padrao_nome,
               catalogo.padrao_descr,
               grupo.grupo_cod_existente,
               grupo.grupo_nome
          FROM padroes_expansao catalogo
          JOIN grupos_expansao_padroes grupo USING (grupo_ref)
         ORDER BY catalogo.ordem
    LOOP
        SELECT existente.id_grupo
          INTO grupo_id
          FROM padroes_grupo existente
         WHERE (padrao.grupo_cod_existente IS NOT NULL
                AND existente.grupo_cod = padrao.grupo_cod_existente)
            OR (padrao.grupo_cod_existente IS NULL
                AND LOWER(BTRIM(existente.grupo_nome)) =
                    LOWER(BTRIM(padrao.grupo_nome)));

        IF grupo_id IS NULL THEN
            RAISE EXCEPTION
                'Migração 033 interrompida: grupo % não foi resolvido.',
                padrao.grupo_ref;
        END IF;

        IF NOT EXISTS (
            SELECT 1
              FROM padroes_subgrupo existente
             WHERE existente.id_grupo = grupo_id
               AND LOWER(BTRIM(existente.padrao_nome)) =
                   LOWER(BTRIM(padrao.padrao_nome))
        ) THEN
            SELECT NEXTVAL('padroes_subgrupo_codigo_seq') INTO numero;

            INSERT INTO padroes_subgrupo (
                id_grupo,
                padrao_cod,
                padrao_nome,
                padrao_descr,
                funcao_detectora
            ) VALUES (
                grupo_id,
                'PD_' || LPAD(numero::TEXT, 3, '0'),
                padrao.padrao_nome,
                padrao.padrao_descr,
                NULL
            );
        END IF;
    END LOOP;
END;
$$;

DO $$
DECLARE
    quantidade INTEGER;
BEGIN
    SELECT COUNT(*)
      INTO quantidade
      FROM padroes_expansao catalogo
      JOIN grupos_expansao_padroes grupo USING (grupo_ref)
      JOIN padroes_grupo grupo_real
        ON (grupo.grupo_cod_existente IS NOT NULL
            AND grupo_real.grupo_cod = grupo.grupo_cod_existente)
        OR (grupo.grupo_cod_existente IS NULL
            AND LOWER(BTRIM(grupo_real.grupo_nome)) =
                LOWER(BTRIM(grupo.grupo_nome)))
      JOIN padroes_subgrupo padrao_real
        ON padrao_real.id_grupo = grupo_real.id_grupo
       AND LOWER(BTRIM(padrao_real.padrao_nome)) =
           LOWER(BTRIM(catalogo.padrao_nome));

    IF quantidade <> 40 THEN
        RAISE EXCEPTION
            'Migração 033 interrompida: foram conferidos % dos 40 padrões.',
            quantidade;
    END IF;
END;
$$;

COMMIT;
