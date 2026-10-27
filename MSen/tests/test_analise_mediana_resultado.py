from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analisar_mediana_resultado import calcular_mediana_combinacao


class AnaliseMedianaResultadoTestCase(unittest.TestCase):
    def test_calcula_mediana_independente_da_ordem(self):
        self.assertEqual(
            Decimal("25"), calcular_mediana_combinacao((50, 10, 40, 20, 30, 1))
        )

    def test_calcula_meio_decimal(self):
        self.assertEqual(
            Decimal("3.5"), calcular_mediana_combinacao((1, 2, 3, 4, 5, 6))
        )


if __name__ == "__main__":
    unittest.main()
