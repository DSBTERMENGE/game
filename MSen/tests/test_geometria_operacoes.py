"""Testes das operações geométricas exatas compartilhadas."""

from fractions import Fraction
import unittest

from msen.geometria import (
    PontoGeometrico,
    SegmentoGeometrico,
    calcular_distancia_quadrada,
    calcular_produto_escalar,
    calcular_produto_vetorial,
    calcular_vetor,
    ponto_pertence_ao_segmento,
    sao_colineares,
    sao_paralelos,
    sao_perpendiculares,
)


def ponto(x: int | Fraction, y: int | Fraction) -> PontoGeometrico:
    return PontoGeometrico(Fraction(x), Fraction(y))


def segmento(
    inicio: tuple[int, int], fim: tuple[int, int]
) -> SegmentoGeometrico:
    return SegmentoGeometrico(ponto(*inicio), ponto(*fim))


class GeometriaOperacoesTestCase(unittest.TestCase):
    def test_calcula_vetor_exato_com_fracoes(self) -> None:
        self.assertEqual(
            (Fraction(3, 2), Fraction(-5, 2)),
            calcular_vetor(ponto(Fraction(1, 2), 3), ponto(2, Fraction(1, 2))),
        )

    def test_calcula_distancia_quadrada_sem_raiz(self) -> None:
        self.assertEqual(Fraction(25), calcular_distancia_quadrada(ponto(1, 1), ponto(4, 5)))

    def test_produto_vetorial_identifica_orientacao_e_colinearidade(self) -> None:
        origem = ponto(0, 0)
        self.assertEqual(1, calcular_produto_vetorial(origem, ponto(1, 0), ponto(0, 1)))
        self.assertEqual(-1, calcular_produto_vetorial(origem, ponto(0, 1), ponto(1, 0)))
        self.assertEqual(0, calcular_produto_vetorial(origem, ponto(1, 1), ponto(2, 2)))
        self.assertTrue(sao_colineares(origem, ponto(1, 1), ponto(2, 2)))

    def test_produto_escalar_identifica_angulo_reto(self) -> None:
        self.assertEqual(0, calcular_produto_escalar(ponto(0, 0), ponto(2, 0), ponto(0, 3)))

    def test_identifica_segmentos_paralelos_em_sentidos_opostos(self) -> None:
        self.assertTrue(
            sao_paralelos(segmento((0, 0), (2, 2)), segmento((5, 4), (3, 2)))
        )

    def test_comprimentos_iguais_nao_significam_paralelismo(self) -> None:
        horizontal = segmento((0, 0), (2, 0))
        vertical = segmento((5, 5), (5, 7))
        self.assertEqual(
            calcular_distancia_quadrada(horizontal.inicio, horizontal.fim),
            calcular_distancia_quadrada(vertical.inicio, vertical.fim),
        )
        self.assertFalse(sao_paralelos(horizontal, vertical))
        self.assertTrue(sao_perpendiculares(horizontal, vertical))

    def test_identifica_ponto_no_interior_e_nas_extremidades(self) -> None:
        trecho = segmento((0, 0), (4, 4))
        self.assertTrue(ponto_pertence_ao_segmento(ponto(0, 0), trecho))
        self.assertTrue(ponto_pertence_ao_segmento(ponto(2, 2), trecho))
        self.assertTrue(ponto_pertence_ao_segmento(ponto(4, 4), trecho))

    def test_rejeita_ponto_fora_do_trecho_ou_da_reta(self) -> None:
        trecho = segmento((0, 0), (4, 4))
        self.assertFalse(ponto_pertence_ao_segmento(ponto(5, 5), trecho))
        self.assertFalse(ponto_pertence_ao_segmento(ponto(2, 3), trecho))

    def test_rejeita_tipos_geometricos_invalidos(self) -> None:
        with self.assertRaises(TypeError):
            calcular_vetor((0, 0), ponto(1, 1))
        with self.assertRaises(TypeError):
            sao_paralelos("segmento", segmento((0, 0), (1, 1)))

    def test_rejeita_segmento_de_comprimento_zero(self) -> None:
        degenerado = SegmentoGeometrico(ponto(1, 1), ponto(1, 1))
        with self.assertRaises(ValueError):
            sao_paralelos(degenerado, segmento((0, 0), (1, 1)))
        with self.assertRaises(ValueError):
            ponto_pertence_ao_segmento(ponto(1, 1), degenerado)


if __name__ == "__main__":
    unittest.main()
