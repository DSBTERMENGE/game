from decimal import Decimal
import unittest

from msen.calculos import (
    calcular_distribuicao_quadrantes,
    calcular_resumo_historico_quadrantes,
    identificar_quadrante,
)


class QuadrantesTest(unittest.TestCase):
    def test_limites_dos_quatro_quadrantes(self):
        self.assertEqual(2, identificar_quadrante(5))
        self.assertEqual(1, identificar_quadrante(6))
        self.assertEqual(2, identificar_quadrante(21))
        self.assertEqual(1, identificar_quadrante(30))
        self.assertEqual(3, identificar_quadrante(31))
        self.assertEqual(4, identificar_quadrante(40))

    def test_codigo_3021_respeita_ordem_q1_q2_q3_q4(self):
        resultado = calcular_distribuicao_quadrantes((6, 17, 30, 31, 42, 60))
        self.assertEqual((3, 0, 2, 1), resultado.contagens)
        self.assertEqual("3021", resultado.codigo)

    def test_distribuicao_independe_da_ordem(self):
        esperado = calcular_distribuicao_quadrantes((6, 17, 30, 31, 42, 60))
        self.assertEqual(
            esperado,
            calcular_distribuicao_quadrantes((60, 42, 31, 30, 17, 6)),
        )

    def test_resumo_trata_codigo_como_categoria_e_eixos_separadamente(self):
        resumo = calcular_resumo_historico_quadrantes((
            (6, 17, 30, 31, 42, 60),
            (1, 2, 3, 4, 5, 6),
        ))
        frequencias = {item.codigo: item for item in resumo.frequencias}
        self.assertEqual(2, resumo.quantidade_resultados)
        self.assertEqual(Decimal("50.000000"), frequencias["3021"].percentual)
        self.assertEqual(Decimal("2.000000"), resumo.quadrantes[0].media)
        self.assertEqual(Decimal("1.000000"), resumo.quadrantes[0].desvio_padrao_populacional)
        self.assertEqual(Decimal("2.500000"), resumo.quadrantes[1].media)

    def test_resumo_vazio_e_dezenas_invalidas_sao_rejeitados(self):
        with self.assertRaises(ValueError):
            calcular_resumo_historico_quadrantes(())
        with self.assertRaises(ValueError):
            calcular_distribuicao_quadrantes((1, 2, 3, 4, 5, 5))


if __name__ == "__main__":
    unittest.main()
