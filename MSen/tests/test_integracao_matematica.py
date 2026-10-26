"""Revisão integrada das validações e funções matemáticas já aprovadas."""

from decimal import Decimal
import unittest

from msen.calculos import (
    calcular_desvio_padrao_media,
    calcular_frequencias,
    calcular_media_aritmetica,
    calcular_media_espacial,
    calcular_mediana,
    calcular_soma,
)
from msen.modelos import ErroValidacaoResultado, ResultadoEntrada


class IntegracaoMatematicaTestCase(unittest.TestCase):
    def test_fluxo_completo_da_apresentacao_3069(self) -> None:
        resultado = ResultadoEntrada.criar(
            data_resultado="11/10/2026",
            numero_ap=3069,
            resultados=[47, 5, 22, 44, 57, 19],
        )

        self.assertEqual(calcular_soma(resultado), 194)
        self.assertEqual(calcular_media_aritmetica(resultado), Decimal("32.333333"))
        self.assertEqual(calcular_mediana(resultado), Decimal("33.0"))
        self.assertEqual(
            calcular_desvio_padrao_media(resultado), Decimal("18.217818")
        )
        media_espacial = calcular_media_espacial(resultado)
        self.assertEqual(media_espacial.x, Decimal("4.666667"))
        self.assertEqual(media_espacial.y, Decimal("2.666667"))

    def test_fluxo_historico_com_intervalos_confirmados(self) -> None:
        resultados = [
            ResultadoEntrada.criar(
                data_resultado="01/01/2026",
                numero_ap=20,
                resultados=[2, 3, 4, 5, 6, 7],
            ),
            ResultadoEntrada.criar(
                data_resultado="02/01/2026",
                numero_ap=35,
                resultados=[1, 2, 8, 9, 10, 11],
            ),
            ResultadoEntrada.criar(
                data_resultado="03/01/2026",
                numero_ap=50,
                resultados=[2, 12, 13, 14, 15, 16],
            ),
        ]

        frequencias = calcular_frequencias(resultados)
        dezena_02 = frequencias[1]

        self.assertEqual(len(frequencias), 60)
        self.assertEqual(dezena_02.ocorrencias, (20, 35, 50))
        self.assertEqual(dezena_02.intervalos, (15, 15))
        self.assertEqual(dezena_02.num_oco, 3)
        self.assertEqual(dezena_02.media_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.mediana_oco, Decimal("15.000000"))
        self.assertEqual(dezena_02.desv_padrao_oco, Decimal("0.000000"))

    def test_repeticao_e_bloqueada_antes_de_todos_os_calculos(self) -> None:
        with self.assertRaises(ErroValidacaoResultado) as contexto:
            ResultadoEntrada.criar(
                data_resultado="11/10/2026",
                numero_ap=3069,
                resultados=[47, 5, 22, 44, 47, 19],
            )

        self.assertEqual(contexto.exception.codigo, "RESULTADO_REPETIDO")

    def test_calculos_nao_modificam_resultados_originais(self) -> None:
        resultado = ResultadoEntrada.criar(
            data_resultado="11/10/2026",
            numero_ap=3069,
            resultados=[47, 5, 22, 44, 57, 19],
        )
        estado_original = resultado.resultados

        calcular_soma(resultado)
        calcular_media_aritmetica(resultado)
        calcular_mediana(resultado)
        calcular_desvio_padrao_media(resultado)
        calcular_media_espacial(resultado)
        calcular_frequencias([resultado])

        self.assertEqual(resultado.resultados, estado_original)


if __name__ == "__main__":
    unittest.main()
