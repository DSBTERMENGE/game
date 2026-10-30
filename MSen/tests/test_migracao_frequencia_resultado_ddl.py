"""Contrato estrutural da migração 017 e do esquema consolidado."""

from pathlib import Path
import unittest


RAIZ = Path(__file__).resolve().parents[2]
MIGRACAO = RAIZ / "database" / "migrations" / "017_ampliar_frequencia_resultado.sql"
ESQUEMA = RAIZ / "database" / "schema_postgresql.sql"


class MigracaoFrequenciaResultadoDDLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.migracao = MIGRACAO.read_text(encoding="utf-8")
        cls.esquema = ESQUEMA.read_text(encoding="utf-8")

    def test_migracao_acrescenta_as_tres_medidas(self) -> None:
        for coluna in ("qtd_intervalos", "intervalo_minimo", "intervalo_maximo"):
            self.assertIn(f"ADD COLUMN {coluna} INTEGER", self.migracao)

    def test_backfill_deriva_intervalos_dos_seis_resultados(self) -> None:
        self.assertIn("CROSS JOIN LATERAL UNNEST", self.migracao)
        self.assertIn("LAG(numero_ap)", self.migracao)
        self.assertIn("COUNT(intervalo)::INTEGER", self.migracao)
        self.assertIn("MIN(intervalo)::INTEGER", self.migracao)
        self.assertIn("MAX(intervalo)::INTEGER", self.migracao)

    def test_restricao_reconcilia_ocorrencias_e_intervalos(self) -> None:
        regra = "qtd_intervalos = num_oco - 1"
        self.assertIn(regra, self.migracao)
        self.assertIn(regra, self.esquema)
        self.assertIn("intervalo_maximo >= intervalo_minimo", self.migracao)

    def test_esquema_consolidado_contem_as_colunas(self) -> None:
        self.assertIn("qtd_intervalos INTEGER NOT NULL DEFAULT 0", self.esquema)
        self.assertIn("intervalo_minimo INTEGER", self.esquema)
        self.assertIn("intervalo_maximo INTEGER", self.esquema)


if __name__ == "__main__":
    unittest.main()
