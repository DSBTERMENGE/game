from decimal import Decimal
import unittest

from msen.services.backtest_selecao_dezenas import _media, _percentual


class MetricasBacktestSelecaoTest(unittest.TestCase):
    def test_percentual_e_media_usam_seis_casas(self) -> None:
        self.assertEqual(_percentual(1, 3), Decimal("33.333333"))
        self.assertEqual(_media(5, 2), Decimal("2.500000"))

    def test_denominador_zero_produz_ausencia_e_nao_zero(self) -> None:
        self.assertIsNone(_percentual(0, 0))
        self.assertIsNone(_media(0, 0))


if __name__ == "__main__":
    unittest.main()
