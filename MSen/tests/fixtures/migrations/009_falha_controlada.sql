-- Migração propositalmente inválida, usada somente para provar o rollback.
BEGIN;
CREATE TABLE teste_rollback_migracao_16_3 (id INTEGER PRIMARY KEY);
SELECT * FROM tabela_inexistente_rollback_16_3;
COMMIT;
