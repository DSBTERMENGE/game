import unittest

from msen.padroes import (
    analisar_arranjo_retangular,
    detectar_arranjo_quadrado_ou_retangulo,
)


class ArranjoRetangularTestCase(unittest.TestCase):
    def test_detecta_retangulo_alinhado_ao_painel(self):
        analise = analisar_arranjo_retangular((1, 4, 7, 17, 21, 51))

        self.assertIsNotNone(analise)
        self.assertEqual(4, len(analise.lados))
        self.assertIn(sorted(analise.distribuicao), ([1, 1, 1, 3], [1, 1, 2, 2]))

    def test_detecta_quadrado_inclinado(self):
        analise = analisar_arranjo_retangular((16, 27, 34, 38, 47, 56))

        self.assertIsNotNone(analise)
        self.assertAlmostEqual(-45.0, analise.angulo_graus)
        self.assertTrue(detectar_arranjo_quadrado_ou_retangulo(
            (16, 27, 34, 38, 47, 56)
        ))

    def test_vertice_e_atribuido_a_somente_um_lado(self):
        analise = analisar_arranjo_retangular((1, 4, 7, 17, 21, 51))

        self.assertEqual(6, len(analise.atribuicao))
        self.assertEqual(6, sum(analise.distribuicao))

    def test_recusa_quatro_dezenas_alinhadas_no_mesmo_lado(self):
        self.assertIsNone(analisar_arranjo_retangular((1, 2, 3, 4, 11, 14)))

    def test_recusa_ponto_interno_ou_fora_do_contorno(self):
        self.assertFalse(detectar_arranjo_quadrado_ou_retangulo(
            (1, 4, 7, 17, 25, 51)
        ))


if __name__ == "__main__":
    unittest.main()
