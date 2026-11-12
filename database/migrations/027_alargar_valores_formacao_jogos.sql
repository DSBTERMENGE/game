-- Migração 027: compatibiliza os valores calculados com os limites da configuração.

BEGIN;

ALTER TABLE formacoes_jogos_selecao
    ALTER COLUMN valor_maximo_previsto TYPE NUMERIC(24,2),
    ALTER COLUMN valor_efetivo TYPE NUMERIC(24,2);

COMMIT;
