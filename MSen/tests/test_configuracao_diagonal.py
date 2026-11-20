import unittest

from msen.padroes import (
    detectar_configuracao_diagonal,
    identificar_linhas_configuracao_diagonal,
)


class ConfiguracaoDiagonalTestCase(unittest.TestCase):
    def test_detecta_uma_diagonal_em_cada_sentido(self):
        self.assertTrue(detectar_configuracao_diagonal((4, 15, 26, 37, 48, 59)))
        self.assertTrue(detectar_configuracao_diagonal((6, 15, 24, 33, 42, 51)))
        self.assertEqual(
            1, len(identificar_linhas_configuracao_diagonal((4, 15, 26, 37, 48, 59)))
        )

    def test_detecta_duas_diagonais_ortogonais_cobrindo_as_seis_dezenas(self):
        dezenas = (6, 15, 17, 24, 28, 33)

        linhas = identificar_linhas_configuracao_diagonal(dezenas)

        self.assertTrue(detectar_configuracao_diagonal(dezenas))
        self.assertEqual(("PASSO_11", "PASSO_9"), tuple(item.sentido for item in linhas))

    def test_recusa_os_tres_casos_incorretos_observados_no_painel(self):
        invalidas = (
            (2, 6, 15, 17, 28, 38),
            (6, 13, 18, 24, 36, 42),
            (10, 19, 21, 28, 49, 51),
        )
        for dezenas in invalidas:
            with self.subTest(dezenas=dezenas):
                self.assertFalse(detectar_configuracao_diagonal(dezenas))
                self.assertEqual((), identificar_linhas_configuracao_diagonal(dezenas))

    def test_recusa_duas_diagonais_paralelas(self):
        self.assertFalse(detectar_configuracao_diagonal((1, 4, 12, 15, 23, 26)))


if __name__ == "__main__":
    unittest.main()
