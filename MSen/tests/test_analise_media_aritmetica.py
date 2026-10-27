from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analisar_media_aritmetica import resumir_distribuicao


class AnaliseMediaAritmeticaTestCase(unittest.TestCase):
    def test_resume_distribuicao_controlada(self):
        resumo = resumir_distribuicao(
            (Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40"))
        )
        self.assertEqual(4, resumo["quantidade"])
        self.assertEqual("10.000000", resumo["minimo"])
        self.assertEqual("25.000000", resumo["media_das_medias"])
        self.assertEqual("25.000000", resumo["mediana_das_medias"])
        self.assertEqual("40.000000", resumo["maximo"])
        self.assertEqual("11.180340", resumo["desvio_padrao_populacional"])

    def test_rejeita_distribuicao_vazia(self):
        with self.assertRaises(ValueError):
            resumir_distribuicao(())


if __name__ == "__main__":
    unittest.main()
