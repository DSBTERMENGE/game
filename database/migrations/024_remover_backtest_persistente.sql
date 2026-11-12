BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM lotes_jogos_selecao l
        JOIN alvos_pesquisa_selecao a USING (id_alvo_selecao)
        JOIN execucoes_pesquisa_selecao e USING (id_execucao_selecao)
        WHERE e.tipo_execucao = 'BACKTEST'
    ) THEN
        RAISE EXCEPTION
            'A migração não pode remover backtests vinculados a lotes de jogos.';
    END IF;
END $$;

-- As tabelas continuam sendo usadas pelos registros do screener. A exclusão
-- abaixo alcança somente as execuções do processo persistente descontinuado;
-- alvos e avaliações correspondentes são removidos pelas chaves em cascata.
DELETE FROM execucoes_pesquisa_selecao
WHERE tipo_execucao = 'BACKTEST';

DROP INDEX IF EXISTS ix_execucao_pesquisa_comparacao;

ALTER TABLE execucoes_pesquisa_selecao
    DROP CONSTRAINT ck_execucao_pesquisa_periodo,
    DROP CONSTRAINT ck_execucao_pesquisa_tipo;

ALTER TABLE execucoes_pesquisa_selecao
    ADD CONSTRAINT ck_execucao_pesquisa_tipo
        CHECK (tipo_execucao = 'PREVISAO_FUTURA'),
    ADD CONSTRAINT ck_execucao_pesquisa_periodo
        CHECK (
            concurso_corte_origem > 0
            AND concurso_alvo_inicial > concurso_corte_origem
            AND concurso_alvo_final >= concurso_alvo_inicial
        );

COMMIT;
