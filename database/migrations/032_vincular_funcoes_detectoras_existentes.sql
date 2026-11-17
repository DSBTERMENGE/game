-- Migração 032: transfere para os novos vínculos os nove detectores existentes.
--
-- A migração exige correspondência integral entre padrão, grupo, critério e
-- função já registrada. Qualquer divergência aborta a transação inteira.

BEGIN;

CREATE TEMPORARY TABLE vinculos_detectores_migracao (
    padrao_cod VARCHAR(32) PRIMARY KEY,
    funcao_detectora VARCHAR(500) NOT NULL
) ON COMMIT DROP;

INSERT INTO vinculos_detectores_migracao (padrao_cod, funcao_detectora) VALUES
    ('PD_001', 'msen.padroes.sequenciais.detectar_duas_dezenas_sequenciais'),
    ('PD_002', 'msen.padroes.sequenciais.detectar_tres_dezenas_sequenciais'),
    ('PD_003', 'msen.padroes.sequenciais.detectar_mais_de_tres_dezenas_sequenciais'),
    ('PD_004', 'msen.padroes.mesma_coluna.detectar_duas_dezenas_na_mesma_coluna'),
    ('PD_005', 'msen.padroes.mesma_coluna.detectar_tres_dezenas_na_mesma_coluna'),
    ('PD_006', 'msen.padroes.mesma_coluna.detectar_mais_de_tres_dezenas_na_mesma_coluna'),
    ('PD_007', 'msen.padroes.mesma_linha.detectar_duas_dezenas_na_mesma_linha'),
    ('PD_008', 'msen.padroes.mesma_linha.detectar_tres_dezenas_na_mesma_linha'),
    ('PD_009', 'msen.padroes.mesma_linha.detectar_mais_de_tres_dezenas_na_mesma_linha');

DO $$
DECLARE
    quantidade INTEGER;
BEGIN
    SELECT COUNT(*)
      INTO quantidade
      FROM vinculos_detectores_migracao v
      JOIN padroes_subgrupo p USING (padrao_cod);

    IF quantidade <> 9 THEN
        RAISE EXCEPTION
            'Migração 032 interrompida: nem todos os nove padrões foram encontrados.';
    END IF;

    SELECT COUNT(*)
      INTO quantidade
      FROM vinculos_detectores_migracao v
      JOIN padroes_subgrupo p USING (padrao_cod)
      JOIN criterios_validacao c
        ON c.id_grupo = p.id_grupo
       AND c.codigo = 'PAD_' || p.padrao_cod
       AND c.categoria = 'PADRAO'
       AND c.funcao_python = v.funcao_detectora;

    IF quantidade <> 9 THEN
        RAISE EXCEPTION
            'Migração 032 interrompida: critério, grupo ou função divergente.';
    END IF;
END;
$$;

UPDATE padroes_subgrupo p
   SET funcao_detectora = v.funcao_detectora
  FROM vinculos_detectores_migracao v
 WHERE p.padrao_cod = v.padrao_cod;

UPDATE criterios_validacao c
   SET id_padrao = p.id_padrao
  FROM padroes_subgrupo p
  JOIN vinculos_detectores_migracao v USING (padrao_cod)
 WHERE c.id_grupo = p.id_grupo
   AND c.codigo = 'PAD_' || p.padrao_cod
   AND c.categoria = 'PADRAO'
   AND c.funcao_python = v.funcao_detectora;

DO $$
DECLARE
    quantidade INTEGER;
BEGIN
    SELECT COUNT(*)
      INTO quantidade
      FROM vinculos_detectores_migracao v
      JOIN padroes_subgrupo p
        ON p.padrao_cod = v.padrao_cod
       AND p.funcao_detectora = v.funcao_detectora
      JOIN criterios_validacao c
        ON c.id_padrao = p.id_padrao
       AND c.id_grupo = p.id_grupo
       AND c.codigo = 'PAD_' || p.padrao_cod
       AND c.funcao_python = p.funcao_detectora;

    IF quantidade <> 9 THEN
        RAISE EXCEPTION
            'Migração 032 interrompida: a conferência final dos vínculos falhou.';
    END IF;
END;
$$;

COMMIT;
