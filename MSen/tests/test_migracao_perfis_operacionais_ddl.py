import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoPerfisOperacionaisDDLTestCase(unittest.TestCase):
    def test_015_antecede_a_016(self):
        migracoes = descobrir_migracoes(MIGRACOES)
        migracao_015 = next(item for item in migracoes if item.versao == "015")
        migracao_016 = next(item for item in migracoes if item.versao == "016")
        self.assertLess(migracoes.index(migracao_015), migracoes.index(migracao_016))

    def test_perfil_atual_nao_cria_historico(self):
        sql = (MIGRACOES / "015_criar_perfis_operacionais_atuais.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("codigo VARCHAR(80) PRIMARY KEY", sql)
        self.assertIn("quantidade_com_valor", sql)
        self.assertIn("quantidade_ausente", sql)
        self.assertIn("desvio_padrao_populacional", sql)
        self.assertNotIn("versao_perfil", sql)
        self.assertIn(
            "CREATE TABLE IF NOT EXISTS perfis_operacionais_atuais",
            ESQUEMA.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
