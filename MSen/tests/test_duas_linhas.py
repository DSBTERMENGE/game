from datetime import date
from decimal import Decimal
import unittest

from msen.modelos import ResultadoEntrada
from msen.padroes.duas_linhas import (
    calcular_estatistica_duas_linhas,
    detectar_dezenas_em_duas_linhas,
)


class TestDuasLinhas(unittest.TestCase):
    def test_aceita_exatamente_duas_linhas_adjacentes(self):
        self.assertTrue(
            detectar_dezenas_em_duas_linhas((1, 10, 11, 12, 19, 20))
        )

    def test_aceita_exatamente_duas_linhas_nao_adjacentes(self):
        self.assertTrue(
            detectar_dezenas_em_duas_linhas((1, 2, 3, 4, 10, 21))
        )

    def test_recusa_uma_linha(self):
        self.assertFalse(
            detectar_dezenas_em_duas_linhas((1, 2, 3, 4, 5, 10))
        )

    def test_recusa_tres_linhas(self):
        self.assertFalse(
            detectar_dezenas_em_duas_linhas((1, 2, 11, 12, 21, 22))
        )

    def test_respeita_bordas_10_11_e_50_51(self):
        self.assertTrue(
            detectar_dezenas_em_duas_linhas((1, 10, 11, 12, 19, 20))
        )
        self.assertTrue(
            detectar_dezenas_em_duas_linhas((41, 50, 51, 52, 59, 60))
        )
        self.assertFalse(
            detectar_dezenas_em_duas_linhas((10, 11, 20, 21, 50, 51))
        )

    def test_recusa_quantidade_repeticao_e_limites_invalidos(self):
        invalidas = (
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 5),
            (0, 1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5, 61),
        )
        for dezenas in invalidas:
            with self.subTest(dezenas=dezenas):
                with self.assertRaises((TypeError, ValueError)):
                    detectar_dezenas_em_duas_linhas(dezenas)

    def test_calcula_estatistica_historica_pelo_mesmo_detector(self):
        historico = tuple(
            ResultadoEntrada.criar(
                data_resultado=date(2020, 1, numero),
                numero_ap=numero,
                resultados=dezenas,
            )
            for numero, dezenas in (
                (1, (1, 2, 3, 11, 12, 13)),
                (2, (1, 11, 21, 31, 41, 51)),
                (5, (41, 42, 43, 51, 52, 53)),
            )
        )

        estatistica = calcular_estatistica_duas_linhas(historico)

        self.assertEqual("PD_011", estatistica.padrao_cod)
        self.assertEqual((1, 5), estatistica.ocorrencias)
        self.assertEqual((4,), estatistica.intervalos)
        self.assertEqual(Decimal("4.000000"), estatistica.intervalo_medio)


if __name__ == "__main__":
    unittest.main()
