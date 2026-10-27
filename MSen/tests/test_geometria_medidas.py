"""Testes de áreas e centros de gravidade geométricos."""

from fractions import Fraction
import inspect
import unittest

from msen.geometria import (
    PontoGeometrico,
    RegiaoFechada,
    calcular_area_e_centro_gravidade,
    consolidar_regioes,
    medir_regiao,
)


def ponto(x: int | Fraction, y: int | Fraction) -> PontoGeometrico:
    return PontoGeometrico(Fraction(x), Fraction(y))


class GeometriaMedidasTestCase(unittest.TestCase):
    def test_exemplo_a_tem_area_e_centro_de_gravidade_previstos(self) -> None:
        resultado = calcular_area_e_centro_gravidade((1, 20, 30, 40, 50, 51))

        self.assertEqual(len(resultado.regioes), 1)
        self.assertEqual(resultado.area_total, Fraction(36))
        self.assertEqual(resultado.centro_gravidade, ponto(Fraction(33, 8), Fraction(5, 2)))

    def test_exemplo_b_soma_duas_areas_e_pondera_os_centroides(self) -> None:
        resultado = calcular_area_e_centro_gravidade((1, 2, 3, 10, 11, 20))

        self.assertEqual(len(resultado.regioes), 2)
        self.assertEqual(
            tuple(medida.area for medida in resultado.medidas_regioes),
            (Fraction(9, 4), Fraction(9, 4)),
        )
        self.assertEqual(resultado.area_total, Fraction(9, 2))
        self.assertEqual(resultado.centro_gravidade, ponto(Fraction(9, 2), Fraction(1, 2)))

    def test_exemplo_c_tem_area_zero_e_centro_nulo(self) -> None:
        resultado = calcular_area_e_centro_gravidade((1, 2, 3, 4, 5, 6))

        self.assertEqual(resultado.regioes, ())
        self.assertEqual(resultado.area_total, 0)
        self.assertIsNone(resultado.centro_gravidade)

    def test_ordem_de_entrada_nao_altera_o_resultado(self) -> None:
        crescente = calcular_area_e_centro_gravidade((1, 20, 30, 40, 50, 51))
        sorteio = calcular_area_e_centro_gravidade((20, 1, 51, 40, 30, 50))

        self.assertEqual(crescente, sorteio)

    def test_mede_triangulo_em_qualquer_orientacao(self) -> None:
        anti_horario = RegiaoFechada((ponto(0, 0), ponto(4, 0), ponto(0, 3)))
        horario = RegiaoFechada(tuple(reversed(anti_horario.vertices)))

        for regiao in (anti_horario, horario):
            with self.subTest(regiao=regiao):
                medida = medir_regiao(regiao)
                self.assertEqual(medida.area, 6)
                self.assertEqual(medida.centroide, ponto(Fraction(4, 3), 1))

    def test_mede_poligono_concavo(self) -> None:
        regiao = RegiaoFechada(
            (ponto(0, 0), ponto(2, 0), ponto(2, 1), ponto(1, 1), ponto(1, 2), ponto(0, 2))
        )

        medida = medir_regiao(regiao)

        self.assertEqual(medida.area, 3)
        self.assertEqual(medida.centroide, ponto(Fraction(5, 6), Fraction(5, 6)))

    def test_contorno_degenerado_tem_centroide_nulo(self) -> None:
        medida = medir_regiao(RegiaoFechada((ponto(0, 0), ponto(1, 0), ponto(2, 0))))

        self.assertEqual(medida.area, 0)
        self.assertIsNone(medida.centroide)

    def test_consolida_regioes_com_areas_diferentes(self) -> None:
        primeira = RegiaoFechada((ponto(0, 0), ponto(2, 0), ponto(0, 2)))
        segunda = RegiaoFechada((ponto(4, 0), ponto(5, 0), ponto(4, 1)))

        resultado = consolidar_regioes((primeira, segunda))

        self.assertEqual(resultado.area_total, Fraction(5, 2))
        self.assertEqual(resultado.centro_gravidade, ponto(Fraction(7, 5), Fraction(3, 5)))

    def test_rejeita_tipos_invalidos(self) -> None:
        with self.assertRaises(TypeError):
            medir_regiao("região")
        with self.assertRaises(TypeError):
            consolidar_regioes([RegiaoFechada((ponto(0, 0), ponto(1, 0), ponto(0, 1)))])

    def test_funcoes_publicas_possuem_docstrings_em_portugues(self) -> None:
        for funcao in (medir_regiao, consolidar_regioes, calcular_area_e_centro_gravidade):
            with self.subTest(funcao=funcao.__name__):
                documentacao = inspect.getdoc(funcao)
                self.assertTrue(documentacao)
                self.assertTrue("área" in documentacao.casefold() or "região" in documentacao.casefold())


if __name__ == "__main__":
    unittest.main()
