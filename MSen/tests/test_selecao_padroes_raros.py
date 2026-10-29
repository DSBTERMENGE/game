from decimal import Decimal
import unittest

from msen.database.padroes_repository import _validar_limite_percentual
from msen.services import selecionar_padroes_raros


class SelecaoPadroesRarosTestCase(unittest.TestCase):
    def test_normaliza_limite_com_seis_casas(self):
        self.assertEqual(
            Decimal("10.000000"), _validar_limite_percentual("10")
        )
        self.assertEqual(
            Decimal("2.997719"), _validar_limite_percentual("2.997719")
        )

    def test_rejeita_limite_invalido(self):
        for valor in (-1, 101, "nan", "texto"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                _validar_limite_percentual(valor)
        for valor in (True, None, 1.5):
            with self.subTest(valor=valor), self.assertRaises(TypeError):
                _validar_limite_percentual(valor)  # type: ignore[arg-type]

    def test_servico_exige_conexao_real(self):
        with self.assertRaises(TypeError):
            selecionar_padroes_raros(
                object(), limite_percentual=10, total_sorteios=3069
            )


if __name__ == "__main__":
    unittest.main()
