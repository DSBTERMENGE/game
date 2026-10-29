import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoRemoverSemCorrespondenciaDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caminho = MIGRACOES / "010_remover_sem_correspondencia.sql"
        cls.sql = cls.caminho.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_010_e_a_ultima_migracao(self):
        migracoes = descobrir_migracoes(MIGRACOES)
        self.assertEqual("010", migracoes[-1].versao)
        self.assertEqual(self.caminho, migracoes[-1].caminho)

    def test_remove_linhas_e_contrato_antigo(self):
        self.assertIn("DELETE FROM resultado_classificacao_padrao", self.sql)
        self.assertIn("ALTER COLUMN id_padrao SET NOT NULL", self.sql)
        self.assertIn("DROP COLUMN estado_classificacao", self.sql)

    def test_esquema_novo_exige_padrao_e_nao_possui_estado(self):
        trecho = self.esquema.split(
            "CREATE TABLE IF NOT EXISTS resultado_classificacao_padrao", 1
        )[1].split(";", 1)[0]
        self.assertIn("id_padrao BIGINT NOT NULL", trecho)
        self.assertNotIn("estado_classificacao", trecho)


if __name__ == "__main__":
    unittest.main()
