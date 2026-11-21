import unittest

from msen.padroes import (
    analisar_arranjo_circular,
    detectar_quatro_a_seis_dezenas_em_arranjo_circular,
)


class ArranjoCircularTestCase(unittest.TestCase):
    def test_detecta_seis_dezenas_no_mesmo_circulo(self):
        dezenas = (15, 17, 24, 28, 44, 48)

        analise = analisar_arranjo_circular(dezenas)

        self.assertIsNotNone(analise)
        self.assertEqual(6, len(analise.dezenas_circulares))
        self.assertTrue(detectar_quatro_a_seis_dezenas_em_arranjo_circular(dezenas))

    def test_recusa_quatro_dezenas_no_circulo(self):
        self.assertIsNone(analisar_arranjo_circular((1, 4, 31, 34, 50, 60)))

    def test_detecta_cinco_dezenas_e_aceita_uma_fora_do_circulo(self):
        analise = analisar_arranjo_circular((15, 17, 24, 28, 44, 60))

        self.assertIsNotNone(analise)
        self.assertEqual(5, len(analise.dezenas_circulares))

    def test_recusa_seis_pontos_alinhados(self):
        self.assertFalse(detectar_quatro_a_seis_dezenas_em_arranjo_circular(
            (1, 2, 3, 4, 5, 6)
        ))

    def test_centro_pode_ficar_fora_do_painel(self):
        analise = analisar_arranjo_circular((1, 2, 9, 12, 18, 25))

        self.assertIsNotNone(analise)
        self.assertTrue(
            analise.centro_x < 0 or analise.centro_x > 10
            or analise.centro_y < 0 or analise.centro_y > 6
        )

    def test_recusa_quarta_dezena_apenas_aproximada(self):
        self.assertIsNone(analisar_arranjo_circular((1, 7, 25, 26, 31, 49)))

    def test_valida_o_contrato_das_seis_dezenas(self):
        with self.assertRaises(ValueError):
            detectar_quatro_a_seis_dezenas_em_arranjo_circular((1, 2, 3, 4))


if __name__ == "__main__":
    unittest.main()
