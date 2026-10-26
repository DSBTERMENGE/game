"""Testes do desvio-padrão populacional."""

from decimal import Decimal
import unittest

from msen.calculos import (
    calcular_desvio_padrao_media,
    calcular_desvio_padrao_populacional,
)
from msen.modelos import ResultadoEntrada


def criar_resultado(valores) -> ResultadoEntrada:
    return ResultadoEntrada.criar(
        data_resultado="11/10/2026",
        numero_ap=3069,
        resultados=valores,
    )


class DesvioPadraoTestCase(unittest.TestCase):
    def test_exemplo_de_referencia_do_concurso_3069(self) -> None:
        resultado = criar_resultado([47, 5, 22, 44, 57, 19])

        self.assertEqual(
            calcular_desvio_padrao_media(resultado),
            Decimal("18.217818"),
        )

    def test_exemplo_populacional_classico(self) -> None:
        # Média 5, variância populacional 4 e desvio-padrão 2.
        valores = [2, 4, 4, 4, 5, 5, 7, 9]

        self.assertEqual(
            calcular_desvio_padrao_populacional(valores),
            Decimal("2.000000"),
        )

    def test_funcao_generica_com_valores_iguais_produz_zero(self) -> None:
        self.assertEqual(
            calcular_desvio_padrao_populacional([5, 5, 5, 5, 5, 5]),
            Decimal("0.000000"),
        )

    def test_um_unico_intervalo_produz_zero(self) -> None:
        self.assertEqual(
            calcular_desvio_padrao_populacional([15]),
            Decimal("0.000000"),
        )

    def test_resultado_independe_da_ordem(self) -> None:
        primeira_ordem = criar_resultado([47, 5, 22, 44, 57, 19])
        segunda_ordem = criar_resultado([19, 57, 44, 22, 5, 47])

        self.assertEqual(
            calcular_desvio_padrao_media(primeira_ordem),
            calcular_desvio_padrao_media(segunda_ordem),
        )

    def test_usa_decimal_com_seis_casas(self) -> None:
        desvio = calcular_desvio_padrao_populacional(
            [Decimal("1.1"), Decimal("2.2"), Decimal("3.3")]
        )

        self.assertIsInstance(desvio, Decimal)
        self.assertEqual(desvio, Decimal("0.898146"))
        self.assertEqual(desvio.as_tuple().exponent, -6)

    def test_rejeita_sequencia_vazia(self) -> None:
        with self.assertRaisesRegex(ValueError, "ao menos um valor"):
            calcular_desvio_padrao_populacional([])

    def test_rejeita_float_texto_e_booleano(self) -> None:
        for valor in (1.5, "1.5", True):
            with self.subTest(valor=valor):
                with self.assertRaisesRegex(TypeError, "int ou Decimal"):
                    calcular_desvio_padrao_populacional([1, valor])

    def test_funcao_nao_altera_o_modelo(self) -> None:
        resultado = criar_resultado([47, 5, 22, 44, 57, 19])
        valores_antes = resultado.resultados

        calcular_desvio_padrao_media(resultado)

        self.assertEqual(resultado.resultados, valores_antes)


if __name__ == "__main__":
    unittest.main()
