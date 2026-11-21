import unittest

from msen.padroes import (
    analisar_arranjo_triangular,
    detectar_dezenas_arranjadas_em_formato_triangular,
)


class ArranjoTriangularTestCase(unittest.TestCase):
    def test_detecta_distribuicao_tres_dois_um(self):
        analise = analisar_arranjo_triangular((1, 3, 5, 21, 23, 41))

        self.assertIsNotNone(analise)
        self.assertEqual([1, 2, 3], sorted(analise.distribuicao))
        self.assertEqual(3, len(analise.lados))

    def test_detecta_distribuicao_dois_dois_dois(self):
        analise = analisar_arranjo_triangular((2, 4, 11, 14, 31, 32))

        self.assertIsNotNone(analise)
        self.assertEqual((2, 2, 2), analise.distribuicao)
        self.assertTrue(detectar_dezenas_arranjadas_em_formato_triangular(
            (2, 4, 11, 14, 31, 32)
        ))

    def test_vertice_conta_para_apenas_um_lado(self):
        analise = analisar_arranjo_triangular((1, 3, 5, 21, 23, 41))

        self.assertEqual(6, len(analise.atribuicao))
        self.assertEqual(6, sum(analise.distribuicao))

    def test_recusa_dezena_fora_dos_segmentos(self):
        self.assertFalse(detectar_dezenas_arranjadas_em_formato_triangular(
            (2, 4, 11, 14, 31, 59)
        ))

    def test_exige_seis_dezenas(self):
        with self.assertRaises(ValueError):
            analisar_arranjo_triangular((1, 3, 5, 21, 41))


if __name__ == "__main__":
    unittest.main()
