import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoAssinaturaRegraDDLTestCase(unittest.TestCase):
    def test_014_antecede_a_015(self):
        migracoes = descobrir_migracoes(MIGRACOES)
        migracao_014 = next(item for item in migracoes if item.versao == "014")
        migracao_015 = next(item for item in migracoes if item.versao == "015")
        self.assertLess(migracoes.index(migracao_014), migracoes.index(migracao_015))

    def test_assinatura_regra_e_obrigatoria_e_validada(self):
        sql = (MIGRACOES / "014_adicionar_assinatura_regra_validacao.sql").read_text(
            encoding="utf-8"
        )
        self.assertIn("ADD COLUMN assinatura_regra CHAR(64) NOT NULL", sql)
        self.assertIn("assinatura_regra ~ '^[0-9a-f]{64}$'", sql)
        esquema = ESQUEMA.read_text(encoding="utf-8")
        self.assertIn("assinatura_regra CHAR(64) NOT NULL", esquema)


if __name__ == "__main__":
    unittest.main()
