"""Testes das coordenadas lógicas e da média espacial."""

from decimal import Decimal
import unittest

from msen.calculos import MediaEspacial, calcular_coordenada, calcular_media_espacial
from msen.modelos import ResultadoEntrada


def criar_resultado(valores) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado="11/10/2026",
        numero_ap=3069,
        resultados=valores,
    )


class CoordenadasTestCase(unittest.TestCase):
    def test_quatro_cantos_confirmados_da_matriz(self) -> None:
        self.assertEqual(calcular_coordenada(1), (0, 0))
        self.assertEqual(calcular_coordenada(10), (9, 0))
        self.assertEqual(calcular_coordenada(51), (0, 5))
        self.assertEqual(calcular_coordenada(60), (9, 5))

    def test_inicio_de_cada_linha_tem_x_zero(self) -> None:
        for numero, y in ((1, 0), (11, 1), (21, 2), (31, 3), (41, 4), (51, 5)):
            with self.subTest(numero=numero):
                self.assertEqual(calcular_coordenada(numero), (0, y))

    def test_final_de_cada_linha_tem_x_nove(self) -> None:
        for numero, y in ((10, 0), (20, 1), (30, 2), (40, 3), (50, 4), (60, 5)):
            with self.subTest(numero=numero):
                self.assertEqual(calcular_coordenada(numero), (9, y))

    def test_rejeita_numero_fora_da_matriz(self) -> None:
        for numero in (0, 61):
            with self.subTest(numero=numero):
                with self.assertRaisesRegex(ValueError, "entre 1 e 60"):
                    calcular_coordenada(numero)

    def test_rejeita_tipo_que_nao_seja_inteiro(self) -> None:
        for numero in (1.0, "1", True):
            with self.subTest(numero=numero):
                with self.assertRaisesRegex(TypeError, "número inteiro"):
                    calcular_coordenada(numero)

    def test_media_espacial_do_exemplo_3069(self) -> None:
        resultado = criar_resultado([47, 5, 22, 44, 57, 19])

        self.assertEqual(
            calcular_media_espacial(resultado),
            MediaEspacial(x=Decimal("4.666667"), y=Decimal("2.666667")),
        )

    def test_media_espacial_decimal_estudada(self) -> None:
        # Coordenadas X somam 12 e Y somam 26: média (2; 4,333333...).
        resultado = criar_resultado([41, 42, 43, 44, 51, 57])

        self.assertEqual(
            calcular_media_espacial(resultado),
            MediaEspacial(x=Decimal("2.000000"), y=Decimal("4.333333")),
        )

    def test_media_espacial_independe_da_ordem(self) -> None:
        primeira_ordem = criar_resultado([41, 42, 43, 44, 51, 57])
        segunda_ordem = criar_resultado([57, 51, 44, 43, 42, 41])

        self.assertEqual(
            calcular_media_espacial(primeira_ordem),
            calcular_media_espacial(segunda_ordem),
        )

    def test_media_usa_decimal_com_seis_casas(self) -> None:
        media = calcular_media_espacial(criar_resultado([41, 42, 43, 44, 51, 57]))

        self.assertIsInstance(media.x, Decimal)
        self.assertIsInstance(media.y, Decimal)
        self.assertEqual(media.x.as_tuple().exponent, -6)
        self.assertEqual(media.y.as_tuple().exponent, -6)

    def test_calculo_nao_altera_o_resultado(self) -> None:
        resultado = criar_resultado([41, 42, 43, 44, 51, 57])
        valores_antes = resultado.resultados

        calcular_media_espacial(resultado)

        self.assertEqual(resultado.resultados, valores_antes)


if __name__ == "__main__":
    unittest.main()
