import unittest

from msen.padroes import (
    detectar_duas_dezenas_sequenciais,
    detectar_mais_de_tres_dezenas_sequenciais,
    detectar_tres_dezenas_sequenciais,
)


class DetectorPD002TestCase(unittest.TestCase):
    def test_casos_positivos_sao_exclusivos_de_pd002(self):
        casos = (
            (10, 25, 26, 27, 50, 58),
            (1, 2, 3, 10, 20, 60),
            (1, 10, 20, 58, 59, 60),
            (1, 2, 3, 20, 21, 40),
            (30, 10, 12, 11, 50, 60),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_duas_dezenas_sequenciais(dezenas))
                self.assertTrue(detectar_tres_dezenas_sequenciais(dezenas))
                self.assertFalse(detectar_mais_de_tres_dezenas_sequenciais(dezenas))

    def test_casos_negativos_nao_atendem_pd002(self):
        casos = (
            (1, 3, 5, 7, 9, 11),
            (10, 25, 26, 38, 50, 58),
            (1, 2, 3, 4, 20, 40),
            (1, 2, 10, 11, 30, 40),
            (1, 2, 20, 30, 59, 60),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_tres_dezenas_sequenciais(dezenas))

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
                    detectar_tres_dezenas_sequenciais(dezenas)


if __name__ == "__main__":
    unittest.main()
