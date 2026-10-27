import unittest

from msen.padroes import (
    detectar_duas_dezenas_na_mesma_coluna,
    detectar_mais_de_tres_dezenas_na_mesma_coluna,
    detectar_tres_dezenas_na_mesma_coluna,
)


class DetectorPD005TestCase(unittest.TestCase):
    def test_casos_positivos_sao_exclusivos_de_pd005(self):
        casos = (
            (7, 17, 27, 34, 45, 56),
            (5, 15, 25, 32, 42, 59),
            (30, 40, 50, 1, 23, 56),
            (40, 20, 30, 1, 23, 56),
            (1, 11, 21, 35, 45, 60),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_duas_dezenas_na_mesma_coluna(dezenas))
                self.assertTrue(detectar_tres_dezenas_na_mesma_coluna(dezenas))
                self.assertFalse(detectar_mais_de_tres_dezenas_na_mesma_coluna(dezenas))

    def test_casos_negativos_nao_atendem_pd005(self):
        casos = (
            (1, 12, 23, 34, 45, 56),
            (10, 25, 35, 48, 51, 59),
            (5, 15, 25, 35, 48, 59),
            (5, 15, 22, 32, 48, 59),
            (5, 25, 45, 1, 32, 59),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_tres_dezenas_na_mesma_coluna(dezenas))

    def test_entrada_invalida_e_rejeitada(self):
        casos = (
            ((1, 2, 3), ValueError),
            ((1, 2, 3, 4, 5, 61), ValueError),
            ((1, 2, 3, 4, 5, 5), ValueError),
            ((1, 2, 3, 4, 5, True), TypeError),
        )
        for dezenas, erro in casos:
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(erro):
                    detectar_tres_dezenas_na_mesma_coluna(dezenas)


if __name__ == "__main__":
    unittest.main()
