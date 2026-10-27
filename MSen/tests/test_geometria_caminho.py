"""Testes do caminho geométrico e de suas medidas básicas."""

from decimal import Decimal
from fractions import Fraction
import inspect
import unittest

from msen.geometria import (
    PontoGeometrico,
    calcular_extensao_aberta,
    calcular_perimetro_fechado,
    construir_caminho_aberto,
    construir_percurso_fechado,
    construir_vertices,
)


class GeometriaCaminhoTestCase(unittest.TestCase):
    def assert_decimal_quase_igual(
        self, calculado: Decimal, esperado: Decimal, tolerancia: str = "0.000000000001"
    ) -> None:
        self.assertLessEqual(abs(calculado - esperado), Decimal(tolerancia))

    def test_constroi_vertices_do_exemplo_sem_cruzamento(self) -> None:
        self.assertEqual(
            construir_vertices([1, 20, 30, 40, 50, 51]),
            (
                PontoGeometrico(Fraction(0), Fraction(0)),
                PontoGeometrico(Fraction(9), Fraction(1)),
                PontoGeometrico(Fraction(9), Fraction(2)),
                PontoGeometrico(Fraction(9), Fraction(3)),
                PontoGeometrico(Fraction(9), Fraction(4)),
                PontoGeometrico(Fraction(0), Fraction(5)),
            ),
        )

    def test_ordena_as_dezenas_sem_alterar_a_entrada(self) -> None:
        dezenas = [20, 1, 51, 40, 30, 50]
        copia = dezenas.copy()
        self.assertEqual(
            construir_vertices(dezenas),
            construir_vertices([1, 20, 30, 40, 50, 51]),
        )
        self.assertEqual(dezenas, copia)

    def test_caminho_aberto_possui_cinco_segmentos_encadeados(self) -> None:
        segmentos = construir_caminho_aberto([1, 20, 30, 40, 50, 51])
        self.assertEqual(len(segmentos), 5)
        for atual, seguinte in zip(segmentos, segmentos[1:]):
            self.assertEqual(atual.fim, seguinte.inicio)

    def test_percurso_fechado_possui_seis_segmentos_e_retorna_ao_inicio(self) -> None:
        segmentos = construir_percurso_fechado([1, 20, 30, 40, 50, 51])
        self.assertEqual(len(segmentos), 6)
        self.assertEqual(segmentos[-1].fim, segmentos[0].inicio)

    def test_medidas_do_exemplo_sem_cruzamento(self) -> None:
        raiz_82 = Decimal(82).sqrt()
        self.assert_decimal_quase_igual(
            calcular_extensao_aberta([1, 20, 30, 40, 50, 51]),
            Decimal(3) + Decimal(2) * raiz_82,
        )
        self.assert_decimal_quase_igual(
            calcular_perimetro_fechado([1, 20, 30, 40, 50, 51]),
            Decimal(8) + Decimal(2) * raiz_82,
        )

    def test_medidas_do_exemplo_cruzado(self) -> None:
        raiz_82 = Decimal(82).sqrt()
        self.assert_decimal_quase_igual(
            calcular_extensao_aberta([1, 2, 3, 10, 11, 20]),
            Decimal(18) + raiz_82,
        )
        self.assert_decimal_quase_igual(
            calcular_perimetro_fechado([1, 2, 3, 10, 11, 20]),
            Decimal(18) + Decimal(2) * raiz_82,
        )

    def test_medidas_da_figura_colinear(self) -> None:
        self.assertEqual(calcular_extensao_aberta([1, 2, 3, 4, 5, 6]), Decimal(5))
        self.assertEqual(calcular_perimetro_fechado([1, 2, 3, 4, 5, 6]), Decimal(10))

    def test_rejeita_quantidade_invalida(self) -> None:
        for dezenas in ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5, 6, 7]):
            with self.subTest(dezenas=dezenas):
                with self.assertRaisesRegex(ValueError, "exatamente seis"):
                    construir_vertices(dezenas)

    def test_rejeita_dezenas_repetidas_ou_fora_da_faixa(self) -> None:
        with self.assertRaisesRegex(ValueError, "diferentes"):
            construir_vertices([1, 2, 3, 4, 5, 5])
        for dezenas in ([0, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 61]):
            with self.subTest(dezenas=dezenas):
                with self.assertRaisesRegex(ValueError, "entre 1 e 60"):
                    construir_vertices(dezenas)

    def test_rejeita_tipos_invalidos(self) -> None:
        for dezenas in ("123456", [1, 2, 3, 4, 5, True], [1, 2, 3, 4, 5, 6.0]):
            with self.subTest(dezenas=dezenas):
                with self.assertRaises(TypeError):
                    construir_vertices(dezenas)

    def test_funcoes_publicas_possuem_documentacao_em_portugues(self) -> None:
        for funcao in (
            construir_vertices, construir_caminho_aberto, construir_percurso_fechado,
            calcular_extensao_aberta, calcular_perimetro_fechado,
        ):
            with self.subTest(funcao=funcao.__name__):
                self.assertTrue(inspect.getdoc(funcao))
                self.assertIn("dezenas", inspect.getdoc(funcao).casefold())


if __name__ == "__main__":
    unittest.main()
