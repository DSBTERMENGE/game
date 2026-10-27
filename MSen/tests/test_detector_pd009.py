import unittest

from msen.padroes import (
    detectar_duas_dezenas_na_mesma_linha,
    detectar_mais_de_tres_dezenas_na_mesma_linha,
    detectar_tres_dezenas_na_mesma_linha,
)


class DetectorPD009TestCase(unittest.TestCase):
    def test_casos_positivos_sao_exclusivos_de_pd009(self):
        casos = (
            (31, 33, 36, 40, 45, 56),
            (41, 42, 43, 44, 45, 56),
            (1, 2, 3, 4, 5, 6),
            (9, 1, 7, 3, 25, 46),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_duas_dezenas_na_mesma_linha(dezenas))
                self.assertFalse(detectar_tres_dezenas_na_mesma_linha(dezenas))
                self.assertTrue(detectar_mais_de_tres_dezenas_na_mesma_linha(dezenas))

    def test_casos_negativos_nao_atendem_pd009(self):
        casos = (
            (1, 12, 23, 34, 45, 56),
            (1, 5, 18, 27, 44, 59),
            (21, 25, 30, 34, 45, 56),
            (1, 5, 9, 12, 18, 44),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_mais_de_tres_dezenas_na_mesma_linha(dezenas))

    def test_entrada_invalida_e_rejeitada(self):
        for dezenas, erro in (
            ((1, 2, 3), ValueError),
            ((1, 2, 3, 4, 5, 61), ValueError),
            ((1, 2, 3, 4, 5, 5), ValueError),
            ((1, 2, 3, 4, 5, True), TypeError),
        ):
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(erro):
                    detectar_mais_de_tres_dezenas_na_mesma_linha(dezenas)


if __name__ == "__main__":
    unittest.main()
