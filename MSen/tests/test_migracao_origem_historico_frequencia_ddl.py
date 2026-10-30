"""Contrato estrutural da migração 020."""

from pathlib import Path
import unittest

from msen.database import descobrir_migracoes


RAIZ = Path(__file__).resolve().parents[2]
MIGRACOES = RAIZ / "database" / "migrations"
MIGRACAO = MIGRACOES / "020_identificar_origem_historico_frequencia.sql"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoOrigemHistoricoFrequenciaDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = MIGRACAO.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_020_e_a_ultima_migracao(self) -> None:
        self.assertEqual("020", descobrir_migracoes(MIGRACOES)[-1].versao)

    def test_guarda_assinatura_e_quantidade_da_origem(self) -> None:
        for trecho in (
            "assinatura_resultados CHAR(64) NOT NULL",
            "quantidade_resultados INTEGER NOT NULL",
            "assinatura_resultados ~ '^[0-9a-f]{64}$'",
            "quantidade_resultados > 0",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.sql)
                self.assertIn(trecho, self.esquema)


if __name__ == "__main__":
    unittest.main()
