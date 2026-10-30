import unittest
from pathlib import Path

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoReferenciasIndependentesDDLTestCase(unittest.TestCase):
    def test_016_permanece_na_sequencia_de_migracoes(self):
        versoes = tuple(item.versao for item in descobrir_migracoes(MIGRACOES))
        self.assertIn("016", versoes)
        self.assertEqual("020", versoes[-1])

    def test_representa_valor_ausente_e_identifica_revisor(self):
        sql = (MIGRACOES / "016_referencias_independentes_validacao.sql").read_text(
            encoding="utf-8"
        )
        for elemento in (
            "estado_valor_esperado",
            "VALOR_IDENTIFICADO', 'SEM_VALOR",
            "referencia_origem",
            "referencia_revisor",
            "referencia_conferida_em",
        ):
            with self.subTest(elemento=elemento):
                self.assertIn(elemento, sql)
                self.assertIn(elemento, ESQUEMA.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
