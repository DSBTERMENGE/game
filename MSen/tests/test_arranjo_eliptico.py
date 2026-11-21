import unittest

from msen.padroes import (
    analisar_arranjo_eliptico,
    detectar_seis_dezenas_em_arranjo_eliptico,
)


class ArranjoElipticoTestCase(unittest.TestCase):
    def test_detecta_elipse_inclinada_com_dois_pares_simetricos(self):
        dezenas = (1, 2, 11, 13, 22, 23)

        analise = analisar_arranjo_eliptico(dezenas)

        self.assertIsNotNone(analise)
        self.assertAlmostEqual(45.0, analise.angulo_graus)
        self.assertLess(analise.semieixo_menor, analise.semieixo_maior)
        self.assertTrue(detectar_seis_dezenas_em_arranjo_eliptico(dezenas))

    def test_recusa_quatro_pontos_sem_pares_simetricos(self):
        self.assertFalse(detectar_seis_dezenas_em_arranjo_eliptico(
            (1, 2, 11, 13, 22, 24)
        ))

    def test_recusa_circulo(self):
        self.assertFalse(detectar_seis_dezenas_em_arranjo_eliptico(
            (15, 17, 24, 28, 44, 48)
        ))

    def test_exige_seis_dezenas(self):
        with self.assertRaises(ValueError):
            detectar_seis_dezenas_em_arranjo_eliptico((1, 2, 11, 13, 22))


if __name__ == "__main__":
    unittest.main()
