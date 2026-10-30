import inspect
import unittest

from tests import oraculo_referencias_independentes as oraculo


class OraculoReferenciasIndependentesTestCase(unittest.TestCase):
    def test_nao_importa_funcoes_aferidas(self):
        fonte = inspect.getsource(oraculo)
        for proibido in ("msen.calculos", "msen.geometria", "msen.padroes"):
            self.assertNotIn(proibido, fonte)

    def test_estatisticas_manuais_de_um_a_seis(self):
        valores = oraculo.referencias_estatisticas((1, 2, 3, 4, 5, 6))
        self.assertEqual(21, valores["EST_SOMA"])
        self.assertEqual("3.500000", str(valores["EST_MEDIA"]))
        self.assertEqual("3.5", str(valores["EST_MEDIANA"]))
        self.assertEqual("1.707825", str(valores["EST_DESVIO_PADRAO"]))

    def test_classificacoes_exclusivas_conhecidas(self):
        casos = {
            "PAD_PD_001": (1, 2, 10, 20, 30, 40),
            "PAD_PD_002": (1, 2, 3, 20, 40, 60),
            "PAD_PD_003": (1, 2, 3, 4, 20, 40),
            "PAD_PD_004": (1, 11, 22, 33, 44, 55),
            "PAD_PD_005": (1, 11, 21, 32, 43, 54),
            "PAD_PD_006": (1, 11, 21, 31, 42, 53),
            "PAD_PD_007": (1, 2, 11, 21, 31, 41),
            "PAD_PD_008": (1, 2, 3, 11, 21, 31),
            "PAD_PD_009": (1, 2, 3, 4, 11, 21),
        }
        for codigo, dezenas in casos.items():
            with self.subTest(codigo=codigo):
                self.assertTrue(oraculo.referencias_padroes(dezenas)[codigo])

    def test_geometria_independente_sem_cruzamento(self):
        valores = oraculo.referencias_geometricas((1, 20, 30, 40, 50, 51))
        self.assertEqual(1, valores["GEO_REGIOES"])
        self.assertEqual("36.0", str(valores["GEO_AREA"]))
        self.assertEqual("4.125", str(valores["GEO_CENTRO_X"]))
        self.assertEqual("2.5", str(valores["GEO_CENTRO_Y"]))

    def test_geometria_independente_com_cruzamento(self):
        valores = oraculo.referencias_geometricas((1, 2, 3, 10, 11, 20))
        self.assertEqual(2, valores["GEO_REGIOES"])
        self.assertEqual("4.5", str(valores["GEO_AREA"]))
        self.assertEqual("4.5", str(valores["GEO_CENTRO_X"]))
        self.assertEqual("0.5", str(valores["GEO_CENTRO_Y"]))

    def test_geometria_independente_colinear_sem_centro(self):
        valores = oraculo.referencias_geometricas((1, 2, 3, 4, 5, 6))
        self.assertEqual(0, valores["GEO_REGIOES"])
        self.assertEqual("0", str(valores["GEO_AREA"]))
        self.assertIsNone(valores["GEO_CENTRO_X"])
        self.assertIsNone(valores["GEO_CENTRO_Y"])


if __name__ == "__main__":
    unittest.main()
