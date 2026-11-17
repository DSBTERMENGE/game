DO $$
DECLARE
    quantidade INTEGER;
    grupo BIGINT;
    funcao VARCHAR(500);
BEGIN
    SELECT COUNT(*), MIN(id_grupo), MIN(funcao_detectora)
      INTO quantidade, grupo, funcao
      FROM padroes_subgrupo
     WHERE id_padrao = 19;

    IF quantidade <> 1 OR grupo <> 5 THEN
        RAISE EXCEPTION
            'O padrão diagonal esperado em id_padrao=19 e id_grupo=5 não foi encontrado.';
    END IF;

    IF funcao IS NOT NULL
       AND funcao <> 'msen.padroes.diagonais.calcular_categorias_diagonais' THEN
        RAISE EXCEPTION
            'O padrão diagonal já possui outra função cadastrada.';
    END IF;

    UPDATE padroes_subgrupo
       SET funcao_detectora =
           'msen.padroes.diagonais.calcular_categorias_diagonais'
     WHERE id_padrao = 19;
END;
$$;
