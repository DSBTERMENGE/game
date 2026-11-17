DO $$
DECLARE
    quantidade INTEGER;
    grupo BIGINT;
    funcao VARCHAR(500);
BEGIN
    SELECT COUNT(*), MIN(id_grupo), MIN(funcao_detectora)
      INTO quantidade, grupo, funcao
      FROM padroes_subgrupo
     WHERE id_padrao = 17;

    IF quantidade <> 1 OR grupo <> 8 THEN
        RAISE EXCEPTION
            'O padrão de duas linhas esperado em id_padrao=17 e id_grupo=8 não foi encontrado.';
    END IF;

    IF funcao IS NOT NULL
       AND funcao <> 'msen.padroes.duas_linhas.detectar_dezenas_em_duas_linhas' THEN
        RAISE EXCEPTION
            'O padrão de duas linhas já possui outra função cadastrada.';
    END IF;

    UPDATE padroes_subgrupo
       SET funcao_detectora =
           'msen.padroes.duas_linhas.detectar_dezenas_em_duas_linhas'
     WHERE id_padrao = 17;
END;
$$;
