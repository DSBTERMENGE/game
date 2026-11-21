import unittest

from msen.padroes import detectar_dezenas_em_duas_colunas
from msen.services import construir_desenho_ocorrencia_validacao


class DuasColunasTestCase(unittest.TestCase):
    def test_detecta_sem_considerar_adjacencia_ou_distribuicao(self):
        casos = (
            (1, 11, 21, 31, 41, 2),
            (1, 11, 21, 31, 2, 12),
            (1, 11, 21, 2, 12, 22),
            (1, 11, 21, 31, 41, 10),
        )
        for dezenas in casos:
            with self.subTest(dezenas=dezenas):
                self.assertTrue(detectar_dezenas_em_duas_colunas(dezenas))

    def test_recusa_uma_ou_tres_colunas(self):
        self.assertFalse(detectar_dezenas_em_duas_colunas((1, 11, 21, 31, 41, 51)))
        self.assertFalse(detectar_dezenas_em_duas_colunas((1, 11, 2, 12, 3, 13)))

    def test_desenha_exatamente_as_duas_colunas(self):
        desenho = construir_desenho_ocorrencia_validacao(
            detectar_dezenas_em_duas_colunas, (1, 11, 21, 2, 12, 22)
        )

        self.assertEqual([0.5, 1.5], [item.x1 for item in desenho.segmentos])
        self.assertTrue(all(item.tipo == "vertical" for item in desenho.segmentos))


if __name__ == "__main__":
    unittest.main()
