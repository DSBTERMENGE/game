"""Testes de soma, média aritmética e mediana de uma linha."""

from decimal import Decimal
import unittest

from msen.calculos import calcular_media_aritmetica, calcular_mediana, calcular_soma
from msen.modelos import ResultadoEntrada


def criar_resultado(valores) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado="11/10/2026",
        numero_ap=3069,
        resultados=valores,
    )


class EstatisticasLinhaTestCase(unittest.TestCase):
    def test_exemplo_de_referencia_do_concurso_3069(self) -> None:
        resultado = criar_resultado([47, 5, 22, 44, 57, 19])

        self.assertEqual(calcular_soma(resultado), 194)
        self.assertEqual(calcular_media_aritmetica(resultado), Decimal("32.333333"))
        self.assertEqual(calcular_mediana(resultado), Decimal("33.0"))

    def test_calculos_do_menor_conjunto_possivel(self) -> None:
        resultado = criar_resultado([1, 2, 3, 4, 5, 6])

        self.assertEqual(calcular_soma(resultado), 21)
        self.assertEqual(calcular_media_aritmetica(resultado), Decimal("3.500000"))
        self.assertEqual(calcular_mediana(resultado), Decimal("3.5"))

    def test_calculos_do_maior_conjunto_possivel(self) -> None:
        resultado = criar_resultado([55, 56, 57, 58, 59, 60])

        self.assertEqual(calcular_soma(resultado), 345)
        self.assertEqual(calcular_media_aritmetica(resultado), Decimal("57.500000"))
        self.assertEqual(calcular_mediana(resultado), Decimal("57.5"))

    def test_mediana_independe_da_ordem_de_entrada(self) -> None:
        crescente = criar_resultado([1, 2, 3, 4, 5, 6])
        fora_de_ordem = criar_resultado([6, 1, 5, 2, 4, 3])

        self.assertEqual(calcular_mediana(crescente), calcular_mediana(fora_de_ordem))
        self.assertEqual(fora_de_ordem.resultados, (6, 1, 5, 2, 4, 3))

    def test_resultados_decimais_usam_decimal_e_precisao_aprovada(self) -> None:
        resultado = criar_resultado([1, 2, 3, 4, 5, 7])
        media = calcular_media_aritmetica(resultado)
        mediana = calcular_mediana(resultado)

        self.assertIsInstance(media, Decimal)
        self.assertIsInstance(mediana, Decimal)
        self.assertEqual(media, Decimal("3.666667"))
        self.assertEqual(media.as_tuple().exponent, -6)
        self.assertEqual(mediana.as_tuple().exponent, -1)

    def test_funcoes_nao_alteram_o_modelo_de_entrada(self) -> None:
        resultado = criar_resultado([47, 5, 22, 44, 57, 19])
        valores_antes = resultado.resultados

        calcular_soma(resultado)
        calcular_media_aritmetica(resultado)
        calcular_mediana(resultado)

        self.assertEqual(resultado.resultados, valores_antes)


if __name__ == "__main__":
    unittest.main()
