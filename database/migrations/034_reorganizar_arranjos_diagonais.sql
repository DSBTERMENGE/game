-- Migração 034: transforma os dois grupos direcionais ainda não implementados
-- em um único filtro categórico de arranjos diagonais.
--
-- A distribuição de assinaturas não é persistida. Ela será calculada a partir
-- de resultados e mantida em memória durante a execução do Screener.

BEGIN;

LOCK TABLE padroes_grupo IN SHARE ROW EXCLUSIVE MODE;
LOCK TABLE padroes_subgrupo IN SHARE ROW EXCLUSIVE MODE;

DO $$
DECLARE
    quantidade INTEGER;
BEGIN
    SELECT COUNT(*)
      INTO quantidade
      FROM padroes_grupo
     WHERE (grupo_cod, grupo_nome) IN (
        ('PG_004', 'Dezenas em diagonal à esquerda'),
        ('PG_006', 'Dezenas em diagonal à direita')
     );
    IF quantidade <> 2 THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: os grupos diagonais esperados divergiram.';
    END IF;

    SELECT COUNT(*)
      INTO quantidade
      FROM padroes_subgrupo p
      JOIN padroes_grupo g USING (id_grupo)
     WHERE (p.padrao_cod, p.padrao_nome, g.grupo_cod) IN (
        ('PD_013', 'Duas dezenas na diagonal de passo 11', 'PG_004'),
        ('PD_014', 'Três dezenas na diagonal de passo 11', 'PG_004'),
        ('PD_015', 'Quatro dezenas na diagonal de passo 11', 'PG_004'),
        ('PD_016', 'Cinco dezenas na diagonal de passo 11', 'PG_004'),
        ('PD_017', 'Seis dezenas na diagonal de passo 11', 'PG_004'),
        ('PD_018', 'Dois segmentos diagonais separados de passo 11', 'PG_004'),
        ('PD_019', 'Três pares diagonais separados de passo 11', 'PG_004'),
        ('PD_020', 'Duas dezenas na diagonal de passo 9', 'PG_006'),
        ('PD_021', 'Três dezenas na diagonal de passo 9', 'PG_006'),
        ('PD_022', 'Quatro dezenas na diagonal de passo 9', 'PG_006'),
        ('PD_023', 'Cinco dezenas na diagonal de passo 9', 'PG_006'),
        ('PD_024', 'Seis dezenas na diagonal de passo 9', 'PG_006'),
        ('PD_025', 'Dois segmentos diagonais separados de passo 9', 'PG_006'),
        ('PD_026', 'Três pares diagonais separados de passo 9', 'PG_006')
     );
    IF quantidade <> 14 THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: o catálogo diagonal foi alterado.';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM padroes_subgrupo
         WHERE padrao_cod BETWEEN 'PD_013' AND 'PD_026'
           AND (
                funcao_detectora IS NOT NULL
                OR num_oco IS NOT NULL
                OR total_sorteios IS NOT NULL
                OR percentual_ocorrencia IS NOT NULL
                OR intervalo_medio IS NOT NULL
                OR desv_padrao IS NOT NULL
           )
    ) THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: há função ou estatística diagonal.';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM resultado_classificacao_padrao r
          JOIN padroes_grupo g USING (id_grupo)
         WHERE g.grupo_cod IN ('PG_004', 'PG_006')
    ) THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: há classificação diagonal persistida.';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM criterios_validacao c
          LEFT JOIN padroes_grupo g USING (id_grupo)
          LEFT JOIN padroes_subgrupo p ON p.id_padrao = c.id_padrao
         WHERE g.grupo_cod IN ('PG_004', 'PG_006')
            OR p.padrao_cod BETWEEN 'PD_013' AND 'PD_026'
    ) THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: há critério ligado ao catálogo diagonal.';
    END IF;

    IF EXISTS (
        SELECT 1
          FROM avaliacoes_validacao a
          LEFT JOIN padroes_subgrupo esperado
            ON esperado.id_padrao = a.id_padrao_esperado
          LEFT JOIN padroes_subgrupo calculado
            ON calculado.id_padrao = a.id_padrao_calculado
         WHERE esperado.padrao_cod BETWEEN 'PD_013' AND 'PD_026'
            OR calculado.padrao_cod BETWEEN 'PD_013' AND 'PD_026'
    ) THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: há avaliação ligada ao catálogo diagonal.';
    END IF;
END;
$$;

ALTER TABLE padroes_grupo
    ADD COLUMN tipo_avaliacao VARCHAR(30) NOT NULL DEFAULT 'BOOLEANO',
    ADD COLUMN funcao_analisadora VARCHAR(500),
    ADD CONSTRAINT ck_padroes_grupo_tipo_avaliacao CHECK (
        tipo_avaliacao IN ('BOOLEANO', 'CATEGORICO_PERCENTUAL')
    ),
    ADD CONSTRAINT ck_padroes_grupo_funcao_analisadora_preenchida CHECK (
        funcao_analisadora IS NULL OR BTRIM(funcao_analisadora) <> ''
    ),
    ADD CONSTRAINT ck_padroes_grupo_avaliacao_funcao CHECK (
        (tipo_avaliacao = 'BOOLEANO' AND funcao_analisadora IS NULL)
        OR
        (
            tipo_avaliacao = 'CATEGORICO_PERCENTUAL'
            AND funcao_analisadora IS NOT NULL
            AND BTRIM(funcao_analisadora) <> ''
        )
    );

COMMENT ON COLUMN padroes_grupo.tipo_avaliacao IS
    'Contrato de execução do grupo: booleano individual ou categórico percentual.';
COMMENT ON COLUMN padroes_grupo.funcao_analisadora IS
    'Nome Python qualificado da função categórica compartilhada pelo grupo.';

UPDATE padroes_grupo
   SET grupo_nome = 'Arranjos diagonais',
       grupo_descr = 'Analisa as dezenas intermediárias P2 a P5 e calcula assinaturas xDyE, em que D representa a diagonal de passo 9 e E a diagonal de passo 11. A referência não entra na contagem; V, V invertido e X não criam categorias diferentes. Antes do funil, a mesma função calcula nos resultados históricos os pares arranjo/percentual e os mantém em memória. Para cada combinação, os arranjos calculados são comparados com essa tabela e com o limite global informado no Screener. Qualquer arranjo abaixo do limite elimina a combinação; arranjo sem ocorrência histórica equivale a 0%. Use Ver tuplas para consultar a tabela histórica usada pela execução.',
       tipo_avaliacao = 'CATEGORICO_PERCENTUAL',
       funcao_analisadora =
           'msen.padroes.diagonais.analisar_assinaturas_diagonais'
 WHERE grupo_cod = 'PG_004';

UPDATE padroes_subgrupo
   SET padrao_nome = 'Configurações diagonais xDyE',
       padrao_descr = 'Filtro categórico compartilhado do grupo Arranjos diagonais. A função analisa P2 a P5, calcula os arranjos xDyE e compara seus percentuais históricos com o limite global do Screener. A combinação é eliminada quando ao menos um arranjo está abaixo do limite; arranjo ausente do histórico equivale a 0%. Use Ver tuplas para consultar ocorrências, denominador e percentuais calculados pela função real.',
       funcao_detectora = NULL
 WHERE padrao_cod = 'PD_013';

DELETE FROM padroes_subgrupo
 WHERE padrao_cod BETWEEN 'PD_014' AND 'PD_026';

DELETE FROM padroes_grupo
 WHERE grupo_cod = 'PG_006';

DO $$
DECLARE
    quantidade INTEGER;
BEGIN
    SELECT COUNT(*)
      INTO quantidade
      FROM padroes_grupo g
      JOIN padroes_subgrupo p USING (id_grupo)
     WHERE g.grupo_cod = 'PG_004'
       AND g.grupo_nome = 'Arranjos diagonais'
       AND g.tipo_avaliacao = 'CATEGORICO_PERCENTUAL'
       AND g.funcao_analisadora =
           'msen.padroes.diagonais.analisar_assinaturas_diagonais'
       AND p.padrao_cod = 'PD_013'
       AND p.padrao_nome = 'Configurações diagonais xDyE'
       AND p.funcao_detectora IS NULL;
    IF quantidade <> 1 THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: o filtro diagonal final divergiu.';
    END IF;

    IF EXISTS (
        SELECT 1 FROM padroes_grupo WHERE grupo_cod = 'PG_006'
    ) OR EXISTS (
        SELECT 1
          FROM padroes_subgrupo
         WHERE padrao_cod BETWEEN 'PD_014' AND 'PD_026'
    ) THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: registros obsoletos permaneceram.';
    END IF;

    SELECT COUNT(*)
      INTO quantidade
      FROM padroes_grupo
     WHERE tipo_avaliacao = 'BOOLEANO'
       AND funcao_analisadora IS NOT NULL;
    IF quantidade <> 0 THEN
        RAISE EXCEPTION
            'Migração 034 interrompida: grupo booleano recebeu analisadora.';
    END IF;
END;
$$;

COMMIT;
